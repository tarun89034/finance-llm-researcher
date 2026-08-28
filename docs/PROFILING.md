# Measured inference latency

Real numbers from an actual run, not estimates. Raw data:
[`profiling_run.json`](profiling_run.json). Reproduce with:

```bash
python scripts/profile_inference.py
```

Captured **2026-08-28T13:29:34Z**.

---

## What was measured

`scripts/profile_inference.py` drives the real chat path — intent detection,
live API fetch, `format_data_context`, `ModelLoader._build_prompt`, streaming
generation — and times each stage separately. One query per branch of
`ChatEngine.detect_intent`, so the cheap and expensive data paths are both
covered rather than a single best case.

It pins the **production** model configuration: the values `app/config.py` falls
back to when no `.env` is present, which is what the Hugging Face Space runs.
Any local `.env` is deliberately overridden.

| Setting | Value |
| --- | --- |
| Model | `mistral-7b-instruct-v0.3.Q4_K_M.gguf` (4.37 GB, Q4_K_M) |
| `n_ctx` | 768 |
| `n_threads` | 2 |
| `n_gpu_layers` | 0 (CPU only) |
| `n_batch` | 128 |
| `max_tokens` | 500 |
| `temperature` | 0.7 |
| Live data | enabled (FRED + World Bank) |

Machine: Windows 11, Intel i5-12500H (12 cores / 16 threads, **capped to 2 for
this run**), 15.7 GB RAM, Python 3.12.0, `llama-cpp-python` 0.3.19.

---

## Results

**Cold model load: 14.46 s.** Paid once per container start, before the first
token of the first request. On the Space this lands on the first visitor.

| Query type | Data fetch | Prompt tok | TTFT | Gen | Completion tok | Decode tok/s | Wall clock |
| --- | --- | --- | --- | --- | --- | --- | --- |
| single_country | 3.36 s | 149 | 7.36 s | 36.57 s | 117 | 3.97 | **39.9 s** |
| comparison | 0.54 s | 194 | 5.06 s | 44.08 s | 168 | 4.28 | **44.6 s** |
| regional | 0.49 s | 350 | 11.41 s | 65.70 s | 231 | 4.24 | **66.2 s** |
| ranking | 2.52 s | 608 | 21.77 s | 57.21 s | 161 | 4.52 | **59.7 s** |

### Reading the numbers

- **Decode is flat at ~4.0–4.5 tok/s** and is the dominant cost. It does not
  vary with prompt size, only with how many tokens the model chooses to emit.
- **Prefill runs ~28–38 tok/s** and scales linearly with prompt length: 194
  tokens → 5.1 s, 608 tokens → 21.8 s. Every token added to the data context
  costs roughly 30 ms of time-to-first-token.
- The single_country TTFT (7.36 s for only 149 tokens) is **off the trend
  because it is the first generation after load** — cold caches and allocator
  warmup. Use the comparison row as the representative small-prompt figure.
- Data fetch is not the bottleneck. 0.5 s when the hour-bucketed cache is warm;
  the 3.36 s and 2.52 s rows are cold-cache upstream calls.
- Temperature is 0.7, so completion length — and therefore wall clock — varies
  between runs. Decode tok/s is the stable metric.

**Bottom line: a user waits 40–66 seconds for a complete answer**, and roughly
5–22 s of that passes before the first token appears.

---

## Finding 1: ranking answers are silently truncated

`n_ctx` is 768 and `max_tokens` is 500, so any prompt over 268 tokens cannot
receive a full-length answer. The ranking query builds a 608-token prompt (ten
data rows), leaving 160 tokens of headroom.

Verified directly, non-streaming:

```
prompt_tokens: 608   n_ctx: 768
finish_reason: length
usage: {'prompt_tokens': 608, 'completion_tokens': 160, 'total_tokens': 768}
…tail: "7. Russia (Russia and CIS): 2.13%\n8. United Arab Emirates (Middle East): 2.17%\n9. Kuwait (M"
```

`total_tokens` hits `n_ctx` exactly and `finish_reason` is `length`. The answer
stops **mid-word**, and nothing in the app surfaces this — no exception, no
warning, no indication to the user that the response is incomplete.

The regional query (350 tokens) is not truncated today but has only 418 tokens
of headroom against a 500-token cap, so it is one extra data row away from the
same failure.

Options, cheapest first:

1. Cap `max_tokens` dynamically at `n_ctx - prompt_tokens - margin` so the model
   at least stops at a sentence boundary, and surface a "response truncated"
   notice.
2. Cut rows in `format_data_context` for ranking/regional intents (ten rows is
   generous for a ten-item list the model just re-emits).
3. Raise `n_ctx`. Costs prefill time and KV-cache memory on a 2-vCPU box —
   measure before committing.

## Finding 2: rankings ignore the direction the user asked for

Surfaced by the same run. Asked *"Which countries have the highest
unemployment?"*, the model returned **lowest**-unemployment countries (Qatar
0.13 %, Cambodia 0.26 %, …).

This is a data-layer bug, not a model bug. `_sort_by_indicator`
(`app/data_fetcher.py:703`) always sorts *best-first*: unemployment has
`higher_is_better=False`, so it sorts ascending. `detect_intent` recognises
"highest", "lowest", "best" and "worst" as ranking words but only records
`is_ranking=True` — the direction is discarded and never reaches
`get_global_ranking`. The model faithfully described the (wrong) rows it was
handed.

Not fixed here; it is outside the scope of this profiling pass.

## Finding 3: the prompt-size / instruction trade is tighter than it looks

`ModelLoader._build_prompt` sends a skeletal 13-token instruction instead of the
221-token `SYSTEM_INSTRUCTION` that appeared in every training sample — a
measured **208-token saving**, worth roughly 6–7 s of prefill at the rates above.

That is a real latency win, but it is now load-bearing for correctness: restoring
the trained instruction would push the ranking prompt from 608 to 816 tokens,
past `n_ctx=768`, and the request would fail outright rather than truncate. Fix
Finding 1 before touching the prompt. See
[FINE_TUNING.md](FINE_TUNING.md) §4.

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
  magnitude and to expose Findings 1 and 2; not enough for variance.
