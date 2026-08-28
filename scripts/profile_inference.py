"""
Inference Profiler
==================
Captures real end-to-end latency for the chat path: live data fetch,
prompt build, prefill (time to first token) and decode.

Runs the *production* model configuration by default -- the values
config.ModelConfig falls back to when no .env is present, which is what
the Hugging Face Space actually runs. Any local .env is deliberately
ignored so the numbers describe the deployed configuration.

    python scripts/profile_inference.py [--out docs/profiling_run.json]
"""

import argparse
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Production configuration: the defaults in app/config.py, pinned here so a
# developer .env cannot silently change what is being measured.
PROD_ENV = {
    "MODEL_CONTEXT_LENGTH": "768",
    "MODEL_THREADS": "2",
    "MODEL_GPU_LAYERS": "0",
    "MODEL_MAX_TOKENS": "500",
    "MODEL_TEMPERATURE": "0.7",
}

# One query per intent branch in ChatEngine.detect_intent, so the run covers
# the cheap and the expensive data paths rather than a single best case.
QUERIES = [
    ("single_country", "What is India's GDP growth rate?"),
    ("comparison", "Compare USA and China inflation."),
    ("regional", "What is the economic outlook for Asia - South?"),
    ("ranking", "Which countries have the highest unemployment?"),
]


def machine_info():
    info = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python": platform.python_version(),
        "logical_cpus": os.cpu_count(),
    }
    try:
        import llama_cpp
        info["llama_cpp_python"] = llama_cpp.__version__
    except Exception:
        info["llama_cpp_python"] = "unavailable"
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="docs/profiling_run.json")
    parser.add_argument("--no-live-data", action="store_true",
                        help="Skip upstream API calls and profile the model alone")
    args = parser.parse_args()

    os.environ.update(PROD_ENV)
    sys.path.insert(0, str(REPO_ROOT / "app"))
    os.chdir(REPO_ROOT)

    import config
    # A .env is loaded at import time; re-pin so the run is reproducible.
    os.environ.update(PROD_ENV)
    config.model_config = config.ModelConfig()
    model_config = config.model_config

    from model_loader import model_loader
    from chat_engine import chat_engine

    use_live = not args.no_live_data

    run = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "machine": machine_info(),
        "model": {
            "repo": model_config.hf_repo_id,
            "file": model_config.hf_filename,
            "n_ctx": model_config.n_ctx,
            "n_threads": model_config.n_threads,
            "n_gpu_layers": model_config.n_gpu_layers,
            "n_batch": 128,
            "max_tokens": model_config.max_tokens,
            "temperature": model_config.temperature,
        },
        "live_data": use_live,
        "queries": [],
    }

    print("Loading model (cold start)...", flush=True)
    t0 = time.perf_counter()
    llm = model_loader.load_model()
    run["model_load_seconds"] = round(time.perf_counter() - t0, 2)
    print(f"  loaded in {run['model_load_seconds']}s", flush=True)

    for kind, query in QUERIES:
        print(f"\n[{kind}] {query}", flush=True)

        t_fetch = time.perf_counter()
        intent = chat_engine.detect_intent(query)
        data = chat_engine.fetch_relevant_data(intent, use_live=use_live) if use_live else []
        fetch_s = time.perf_counter() - t_fetch

        data_context = chat_engine.format_data_context(data) if data else ""
        enhanced = f"{query}\n\n{data_context}" if data_context else query
        prompt = model_loader._build_prompt(enhanced)
        prompt_tokens = len(llm.tokenize(prompt.encode("utf-8"), add_bos=True))

        t_gen = time.perf_counter()
        ttft = None
        n_tokens = 0
        text = ""
        error = None
        try:
            for chunk in model_loader.generate_stream(enhanced):
                if ttft is None:
                    ttft = time.perf_counter() - t_gen
                n_tokens += 1
                text += chunk
        except Exception as exc:
            # A prompt long enough to leave < max_tokens of headroom inside
            # n_ctx raises here. That is a real production failure mode, so
            # record it instead of aborting the run.
            error = f"{type(exc).__name__}: {exc}"
            print(f"  !! {error}", flush=True)
        gen_s = time.perf_counter() - t_gen

        decode_s = gen_s - (ttft or 0)
        # The first streamed chunk is the first token, so decode covers the rest.
        decode_tps = round((n_tokens - 1) / decode_s, 2) if decode_s > 0 and n_tokens > 1 else None

        record = {
            "kind": kind,
            "query": query,
            "data_rows": len(data),
            "live_rows": sum(1 for d in data if getattr(d, "is_live", False)),
            "data_fetch_seconds": round(fetch_s, 2),
            "prompt_tokens": prompt_tokens,
            "context_headroom_tokens": model_config.n_ctx - prompt_tokens,
            "time_to_first_token_seconds": round(ttft, 2) if ttft else None,
            "generation_seconds": round(gen_s, 2),
            "completion_tokens": n_tokens,
            "decode_tokens_per_second": decode_tps,
            "wall_clock_seconds": round(fetch_s + gen_s, 2),
            "response_chars": len(text),
            "hit_max_tokens": n_tokens >= model_config.max_tokens,
            "error": error,
        }
        run["queries"].append(record)
        print("  " + json.dumps({k: record[k] for k in (
            "data_fetch_seconds", "prompt_tokens", "context_headroom_tokens",
            "time_to_first_token_seconds", "generation_seconds",
            "completion_tokens", "decode_tokens_per_second")}), flush=True)

    out = REPO_ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(run, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
