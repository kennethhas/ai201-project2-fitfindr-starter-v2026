"""Summarize real uncached /ask runs after criteria have been committed.

Usage: python summarize_usage.py logs/requests.jsonl
This reads existing evidence; it does not call the model or assign verdicts.
"""

import argparse
import json
from pathlib import Path
from statistics import mean


def summarize(records, count=10, people=100):
    eligible = [r for r in records if (
        r.get("path") == "/ask" and r.get("outcome") == "success"
        and r.get("cache_enabled") is False and r.get("model_calls", 0) > 0
    )]
    if len(eligible) < count:
        raise ValueError(
            f"Need {count} successful uncached model runs; found {len(eligible)}. "
            "Start the server with AI201_CACHE=0 and collect real runs."
        )
    selected = eligible[-count:]
    seconds = [r["duration_ms"] / 1000 for r in selected]
    tokens = [r["reported_tokens"]["total"] for r in selected]
    complete_counts = all(
        all(type(r["reported_tokens"].get(k)) is int and r["reported_tokens"][k] > 0
            for k in ("prompt", "output", "total"))
        and r["reported_tokens"]["total"] == r["reported_tokens"]["prompt"] + r["reported_tokens"]["output"]
        for r in selected
    )
    token_average = mean(tokens) if complete_counts else None
    return {
        "runs": count,
        "selection": "last successful uncached /ask requests with model calls",
        "request_ids": [r["request_id"] for r in selected],
        "elapsed_seconds_sum": sum(seconds),
        "elapsed_seconds_mean": mean(seconds),
        "reported_prompt_plus_output_tokens_sum": sum(tokens) if token_average is not None else None,
        "reported_prompt_plus_output_tokens_mean": token_average,
        "daily_assumption": f"{people} people, one uncached query per person per day",
        "daily_reported_prompt_plus_output_tokens": (
            token_average * people if token_average is not None else None
        ),
        "daily_elapsed_request_seconds": mean(seconds) * people,
        "limitations": [
            "Elapsed time includes MCP startup, model waits, pacing and queueing; it is not CPU time.",
            "Tokens are the adapter's reported prompt plus output counts, not a dollar bill or all billing categories.",
            "A zero token count is treated as unavailable, not free usage.",
            "These are warm-process requests; server cold-start time is not included.",
            "Selection excludes failed runs; their costs are not included in the daily projection.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--people", type=int, default=100)
    args = parser.parse_args()
    if args.count < 1 or args.people < 1:
        parser.error("count and people must be positive")
    try:
        records = [json.loads(line) for line in args.log.read_text(encoding="utf-8").splitlines() if line.strip()]
        print(json.dumps(summarize(records, args.count, args.people), indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Cannot summarize: {exc}\n")
