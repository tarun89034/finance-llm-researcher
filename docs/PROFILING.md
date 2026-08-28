# Measured inference latency

Real numbers from an actual run, not estimates. Raw data:
[`profiling_run.json`](profiling_run.json). Reproduce with:

```bash
python scripts/profile_inference.py
```

Captured **2026-08-28T14:07:41Z**, after the two fixes described below.

---

## What was measured

`scripts/profile_inference.py` drives the real chat path — intent detection,
live API fetch, `format_data_context`, `ChatEngine.build_model_input` (including
its context trimming), streaming generation — and times each stage separately.
One query per branch of `ChatEngine.detect_intent`, so the cheap and expensive
data paths are both covered rather than a single best case.

The Space runs with no `.env`, so `ModelConfig`'s own defaults *are* the
production configuration. The profiler clears the `MODEL_*` environment
overrides and rebuilds from those defaults rather than restating their values,
so it cannot drift out of sync with `app/config.py`.

| Setting | Value |
| --- | --- |
| Model | `mistral-7b-instruct-v0.3.Q4_K_M.gguf` (4.37 GB, Q4_K_M) |
| `n_ctx` | 1024 |
| `n_threads` | 2 |
| `n_gpu_layers` | 0 (CPU only) |
| `n_batch` | 128 |
| `max_tokens` | 500 |
| `temperature` | 0.7 |
| `context_safety_margin` | 24 |
| `min_answer_tokens` | 256 |
| Live data | enabled (FRED + World Bank) |

Machine: Windows 11, Intel i5-12500H (12 cores / 16 threads, **capped to 2 for
this run**), 15.7 GB RAM, Python 3.12.0, `llama-cpp-python` 0.3.19.

---

## Results

**Cold model load: 11.9 s.** Paid once per container start, before the first
token of the first request. On the Space this lands on the first visitor.
(Observed 3.7-14.5 s across runs, depending on OS file cache.)

| Query type | Rows | Data fetch | Prompt tok | TTFT | Gen | Completion tok | Decode tok/s | Wall clock | Finish |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| single_country | 1 | 3.59 s | 149 | 6.54 s | 31.92 s | 116 | 4.53 | **35.5 s** | stop |
| comparison | 2 | 0.07 s | 194 | 5.28 s | 43.10 s | 167 | 4.39 | **43.2 s** | stop |
| regional | 5 | 0.07 s | 350 | 11.15 s | 65.25 s | 230 | 4.23 | **65.3 s** | stop |
| ranking | 10 | 1.32 s | 631 | 23.58 s | 82.67 s | 243 | 4.10 | **84.0 s** | stop |

Every query now finishes with `finish_reason: stop` — the model ends its own
answer rather than hitting the context wall.

### Reading the numbers

- **Decode is flat at ~4.1-4.5 tok/s** and is the dominant cost. It does not
  vary with prompt size, only with how many tokens the model chooses to emit.
- **Prefill runs ~27-37 tok/s** and scales linearly with prompt length: 194
  tokens gives 5.3 s, 631 tokens gives 23.6 s. Every token added to the data
  context costs roughly 30 ms of time-to-first-token.
- The single_country TTFT (6.54 s for only 149 tokens) is **off the trend
  because it is the first generation after load** — cold caches and allocator
  warmup. Use the comparison row as the representative small-prompt figure.
- Data fetch is not the bottleneck: 0.07 s once the hour-bucketed cache is warm.
- Temperature is 0.7, so completion length — and therefore wall clock — varies
  between runs. Decode tok/s is the stable metric.

**Bottom line: a user waits 35-84 seconds for a complete answer**, and 5-24 s of
that passes before the first token appears. The ranking query got *slower* than
before the fix (60 s to 84 s) because it now produces a whole ten-row answer
instead of stopping mid-word at row nine.

---

## Fixed: answers were silently truncated

**Before.** `n_ctx` was 768 and `max_tokens` 500, so any prompt over 268 tokens
could not receive a full-length answer. The ranking query built a 608-token
prompt, leaving 160 tokens of headroom:

```
prompt_tokens: 608   n_ctx: 768
finish_reason: length
usage: {'prompt_tokens': 608, 'completion_tokens': 160, 'total_tokens': 768}
tail: "8. United Arab Emirates (Middle East): 2.17%\n9. Kuwait (M"
```

`total_tokens` hit `n_ctx` exactly. The answer stopped **mid-word**, and nothing
in the app surfaced it — no exception, no warning, no indication to the user.

**Root cause of the root cause.** `n_ctx=768` was chosen in commit `6c729e2`
("Phase 3: Ultra-fast tuning") on the assumption that a smaller context window
is faster. It is not. Measured on the production config, with one fixed
527-token prompt and greedy decoding:

| `n_ctx` | TTFT | Prefill |
| --- | --- | --- |
| 768 | 21.36 s | 24.7 tok/s |
| 1024 | 21.39 s | 24.6 tok/s |
| 1536 | 21.59 s | 24.4 tok/s |

Prefill cost is proportional to the *actual prompt length*, not to `n_ctx`. The
only thing `n_ctx` buys is KV-cache memory — about 128 KB per token, so
768 to 1024 costs ~32 MB against the Space's 16 GB. The setting was saving
nothing and causing truncation.

**The fix**, in three layers:

1. **`n_ctx` default raised 768 to 1024** (`app/config.py`). This alone lets the
   largest prompt the app builds (631 tokens) carry a complete answer, with 393
   tokens of headroom.
2. **`ChatEngine.build_model_input`** drops data rows until the answer has at
   least `min_answer_tokens` (256) of room. Dropping rows is what actually buys
   a whole answer; clamping `max_tokens` alone only makes the truncation tidier.
   At `n_ctx=1024` nothing trims today — this is the safety net for when a
   region grows or the prompt gets longer.
3. **`ModelLoader.generate_stream`** clamps `max_tokens` to
   `n_ctx - prompt_tokens - context_safety_margin`, records
   `last_finish_reason`, and refuses to generate at all if the prompt fills the
   window. If a verbose answer still exhausts the clamped budget, `ChatEngine`
   appends a visible "response cut short" notice instead of ending mid-sentence.

All four query types now return `finish_reason: stop`.

## Fixed: rankings ignored the direction the user asked for

**Before.** Asked *"Which countries have the highest unemployment?"*, the app
returned the **lowest**: Qatar 0.13 %, Cambodia 0.26 %, Thailand 0.78 %.

This was a data-layer bug, not a model bug. `_sort_by_indicator` always sorted
*best-first*: unemployment has `higher_is_better=False`, so it sorted ascending.
`detect_intent` recognised "highest", "lowest", "best" and "worst" as ranking
words but only recorded `is_ranking=True` — the direction was discarded and
never reached `get_global_ranking`. The model faithfully described the wrong
rows it was handed, and captioned them "Ranking Criteria: Lowest values".

**The fix.** `detect_intent` now records a `ranking_direction`, threaded through
`get_global_ranking` / `get_region_data` into `_sort_by_indicator`, which
distinguishes four orderings:

| Direction | Meaning |
| --- | --- |
| `highest` | largest raw value first |
| `lowest` | smallest raw value first |
| `best` | best performer first, per `higher_is_better` |
| `worst` | worst performer first |
| `None` | same as `best` — what the dashboard tabs want, unchanged |

`best`/`worst` and `highest`/`lowest` only coincide where a larger number is
unambiguously better, which is exactly why the original code got unemployment
wrong. Direction words are matched on word boundaries, or "most" fires on
"almost" and "top" on "stopped". Detection runs only on queries already
classified as rankings, so no query changes branches.

Verified against live World Bank data:

| Query | Direction | Top result |
| --- | --- | --- |
| highest unemployment | `highest` | South Africa 32.39 % |
| lowest unemployment | `lowest` | Qatar 0.13 % |
| worst inflation | `worst` | Zimbabwe 98.55 % |
| top countries by GDP growth | `highest` | Libya 13.37 % |

`format_data_context` now also states the sort order in the prompt, so the model
captions the list the way it was actually sorted instead of inventing criteria.

Regression tests for both fixes: `test_ranking_and_context.py`.

---

## Still open: the prompt-size / instruction trade

`ModelLoader._build_prompt` sends a skeletal 13-token instruction instead of the
221-token `SYSTEM_INSTRUCTION` that appeared in every training sample — a
measured **208-token saving**, worth roughly 6-7 s of prefill.

With `n_ctx` now at 1024 the arithmetic is no longer prohibitive: restoring the
full instruction would put the ranking prompt at ~839 tokens, still inside the
window but leaving only ~160 tokens for the answer, which would trigger row
trimming. Restoring it is a real option if output quality regresses — it would
cost roughly 7 s of prefill and two or three ranking rows. See
[FINE_TUNING.md](FINE_TUNING.md) section 4.

---

## Caveats — do not quote these as the Space's numbers

- **Hardware differs.** The thread count matches the Space (2), but the cores do
  not. These ran on 2 threads of a 12th-gen mobile CPU; the free tier allocates
  2 vCPUs of shared server silicon. Treat every figure here as an **optimistic
  bound** — the deployed Space is likely slower, not faster.
- **Version differs.** `Dockerfile` pins `llama-cpp-python==0.3.2`; this run used
  0.3.19, the newest wheel available for CPython 3.12 on Windows. (The venv's
  previous 0.3.16 install was broken — `ggml-cpu.dll` failed to load with
  `WinError 127` — and had to be reinstalled before anything could run.)
- **One run, one sample per query type.** Enough to establish the order of
  magnitude and to confirm both fixes; not enough for variance.
