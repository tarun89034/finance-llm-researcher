"""
Regression tests for two bugs found by scripts/profile_inference.py:

  1. Rankings ignored the direction the user asked for. "Which countries have
     the highest unemployment?" returned the *lowest* ones, because the data
     layer always sorted best-first and detect_intent discarded the direction
     word.

  2. Answers were silently truncated. A ten-row ranking built a ~600-token
     prompt; with n_ctx=768 and max_tokens=500 llama.cpp stopped mid-word with
     finish_reason="length" and nothing surfaced it.

The sorting checks are pure and always run. The context-budget checks need the
GGUF to tokenize with, and are skipped when it is not present.

    python test_ranking_and_context.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, "app")

# Pin the model config before anything imports it, so a developer .env cannot
# change what is being asserted.
#
# n_ctx is deliberately pinned to the old, too-small 768 rather than the current
# 1024 default: that is the window in which a ten-row ranking overflows, so it
# keeps the trimming safety net under test even though production no longer
# needs to trim.
os.environ.update({
    "MODEL_CONTEXT_LENGTH": "768",
    "MODEL_THREADS": "2",
    "MODEL_MAX_TOKENS": "500",
})

from chat_engine import chat_engine, detect_ranking_direction  # noqa: E402
from data_fetcher import _sort_by_indicator, TriangulatedData  # noqa: E402
from indicators import INDICATORS  # noqa: E402

failures = []


def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        print(f"        got  {got!r}")
        print(f"        want {want!r}")
        failures.append(label)


def row(name, value, indicator_code):
    """Minimal TriangulatedData standing in for a fetched result."""
    return TriangulatedData(
        country_code=name[:3].upper(), country_name=name, region="Test",
        income_level="high", indicator_code=indicator_code,
        indicator_name=indicator_code, consensus_value=value, unit="%",
        fred_value=None, worldbank_value=value, oecd_value=None,
        confidence_level="high", confidence_description="",
        assessment_label="", assessment_description="",
        period="2025", source_count=1,
    )


print("=" * 78)
print("1. DIRECTION IS PARSED OUT OF THE QUERY")
print("=" * 78)

check("'highest unemployment' -> highest",
      detect_ranking_direction("which countries have the highest unemployment?"),
      "highest")
check("'lowest unemployment' -> lowest",
      detect_ranking_direction("which countries have the lowest unemployment?"),
      "lowest")
check("'top 10 by gdp growth' -> highest",
      detect_ranking_direction("top 10 countries by gdp growth"), "highest")
check("'worst inflation' -> worst",
      detect_ranking_direction("which countries have the worst inflation?"), "worst")
check("'best performing' -> best",
      detect_ranking_direction("best performing economies"), "best")
check("no direction word -> None",
      detect_ranking_direction("show me the ranking of government debt"), None)
# Word boundaries: without them "most" fires on "almost" and "top" on "stopped".
check("'almost'/'stopped' are not direction words",
      detect_ranking_direction("almost all countries stopped reporting"), None)

print()
print("  intent plumbing:")
intent = chat_engine.detect_intent("Which countries have the highest unemployment?")
check("is_ranking set", intent["is_ranking"], True)
check("ranking_direction set", intent["ranking_direction"], "highest")


print()
print("=" * 78)
print("2. SORTING HONOURS THE DIRECTION")
print("=" * 78)

# Unemployment: lower is better, so best-first and highest-first are opposites.
# This is exactly the case the original bug got wrong.
check("unemployment is a lower-is-better indicator",
      INDICATORS["unemployment"].higher_is_better, False)

unemp = [row("Alpha", 2.0, "unemployment"),
         row("Beta", 15.0, "unemployment"),
         row("Gamma", 7.0, "unemployment")]
order = lambda d, rows, code: [r.country_name
                               for r in _sort_by_indicator(rows, code, d)]

check("highest unemployment -> worst performers first",
      order("highest", unemp, "unemployment"), ["Beta", "Gamma", "Alpha"])
check("lowest unemployment -> best performers first",
      order("lowest", unemp, "unemployment"), ["Alpha", "Gamma", "Beta"])
check("worst unemployment == highest unemployment",
      order("worst", unemp, "unemployment"), order("highest", unemp, "unemployment"))
check("best unemployment == lowest unemployment",
      order("best", unemp, "unemployment"), order("lowest", unemp, "unemployment"))

# The dashboard tabs pass no direction and must keep their old best-first order.
check("default (None) is unchanged best-first",
      order(None, unemp, "unemployment"), ["Alpha", "Gamma", "Beta"])

# GDP growth: higher is better, so highest and best coincide.
gdp = [row("Alpha", 2.0, "gdp_growth"),
       row("Beta", 15.0, "gdp_growth"),
       row("Gamma", 7.0, "gdp_growth")]
check("highest gdp growth == best gdp growth",
      order("highest", gdp, "gdp_growth"), order("best", gdp, "gdp_growth"))
check("lowest gdp growth == worst gdp growth",
      order("lowest", gdp, "gdp_growth"), order("worst", gdp, "gdp_growth"))


print()
print("=" * 78)
print("3. THE PROMPT STATES THE ORDER IT WAS SORTED IN")
print("=" * 78)

ctx = chat_engine.format_data_context(unemp, {"is_ranking": True,
                                              "ranking_direction": "highest"})
check("context announces highest-first",
      "sorted highest value first" in ctx, True)
ctx_best = chat_engine.format_data_context(unemp, {"is_ranking": True,
                                                   "ranking_direction": None})
check("context defaults to best-first wording",
      "sorted best performer first" in ctx_best, True)
check("non-ranking context stays unannotated",
      "Rows are already sorted" in chat_engine.format_data_context(unemp), False)


print()
print("=" * 78)
print("4. CONTEXT BUDGET (needs the GGUF)")
print("=" * 78)

from config import model_config  # noqa: E402

if not Path(model_config.local_model_path).exists():
    print(f"  SKIP  {model_config.local_model_path} not present")
else:
    from model_loader import model_loader  # noqa: E402

    model_loader.load_model()
    query = "Which countries have the highest unemployment?"
    intent = chat_engine.detect_intent(query)

    # Ten rows is what fetch_relevant_data returns for a ranking, and is what
    # produced the 608-token prompt that got truncated.
    many = [row(f"Country{i:02d}", float(30 - i), "unemployment") for i in range(10)]
    enhanced, kept = chat_engine.build_model_input(query, many, intent)

    budget = model_loader.answer_budget(enhanced)
    print(f"  rows {len(many)} -> {len(kept)}, "
          f"prompt {model_loader.prompt_tokens(enhanced)} tok, budget {budget} tok")

    check("rows were trimmed to fit", len(kept) < len(many), True)
    check("answer budget clears the minimum",
          budget >= model_config.min_answer_tokens, True)
    check("prompt + budget stays inside n_ctx",
          model_loader.prompt_tokens(enhanced) + budget <= model_config.n_ctx, True)

    # A short query needs no trimming at all.
    one = [row("Solo", 5.0, "unemployment")]
    _, kept_one = chat_engine.build_model_input("What is unemployment in Solo?",
                                                one, {"is_ranking": False})
    check("small contexts are left alone", len(kept_one), 1)


print()
print("=" * 78)
if failures:
    print(f"FAILED: {len(failures)} check(s)")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("All checks passed.")
