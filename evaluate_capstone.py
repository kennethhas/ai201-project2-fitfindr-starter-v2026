"""Score saved evidence against the five frozen, disclosed capstone criteria.

Usage: python evaluate_capstone.py --label before
This does not call Gemini, change evidence, or invent a cause for a failure.
"""

import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

from capture_capstone import CASES, ROOT, normalize
from summarize_usage import summarize

EXPECTED_CRITERIA_SHA256 = "057291c0de683c6e8819234c8e4dd4d0c531794a53abdbd06b4bbc52dcdb03d3"
TITLES = ["Complete request records", "HTTP response time", "Recorded model usage",
          "Invalid input rejection", "Preserve original behavior"]
TARGETS = [13, 10, 10, 3, 10]


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def one_log(record):
    logs = record.get("matching_logs", [])
    return logs[0] if len(logs) == 1 else None


def successful(record):
    body = record["http"]["body"]
    return (record["http"]["status"] == 200 and isinstance(body, dict)
            and body.get("error") is None and nonempty(body.get("fit_card")))


def check_log(record):
    log = one_log(record)
    http = record["http"]
    if log is None or not nonempty(http.get("request_id")):
        return False
    try:
        stamp = datetime.fromisoformat(log["timestamp"])
        if stamp.utcoffset() is None:
            return False
    except (KeyError, ValueError, TypeError):
        return False
    body = http["body"]
    expected_output = body
    if isinstance(body, dict) and "non_json_body" in body:
        output = log.get("output")
        output_matches = isinstance(output, dict) and output.get("http_status") == http["status"] and nonempty(output.get("message"))
    else:
        output_matches = log.get("output") == expected_output
    expected_outcome = "error" if http["status"] >= 500 else (
        "rejected" if http["status"] >= 400 else (
            "agent_stopped" if isinstance(body, dict) and body.get("error") else "success"
        )
    )
    return (log.get("request_id") == http["request_id"]
            and log.get("input") == record["case"]["payload"]
            and log.get("status_code") == http["status"]
            and log.get("outcome") == expected_outcome
            and finite_number(log.get("duration_ms")) and log["duration_ms"] >= 0
            and output_matches)


def check_latency(record):
    elapsed = record["http"].get("client_elapsed_seconds")
    return successful(record) and finite_number(elapsed) and 0 <= elapsed <= 30.0


def check_usage(record):
    log = one_log(record)
    if not successful(record) or log is None or log.get("cache_enabled") is not False:
        return False
    tokens = log.get("reported_tokens", {})
    return (type(log.get("model_calls")) is int and log["model_calls"] > 0
            and all(type(tokens.get(k)) is int and tokens[k] > 0 for k in ("prompt", "output", "total"))
            and tokens["total"] == tokens["prompt"] + tokens["output"])


def check_rejection(record):
    log = one_log(record)
    body = record["http"]["body"]
    return (record["http"]["status"] == 400 and isinstance(body, dict)
            and nonempty(body.get("error")) and log is not None
            and type(log.get("model_calls")) is int and log["model_calls"] == 0)


def check_regression(record):
    if not successful(record):
        return False
    body = record["http"]["body"]
    selected = body.get("selected_item")
    results = body.get("search_results")
    if not isinstance(selected, dict) or not isinstance(results, list):
        return False
    return (nonempty(selected.get("id"))
            and any(isinstance(item, dict) and item.get("id") == selected["id"] for item in results)
            and finite_number(selected.get("price"))
            and selected["price"] <= record["case"]["budget"]
            and nonempty(body.get("outfit_suggestion")))


CHECKS = [check_log, check_latency, check_usage, check_rejection, check_regression]


def validate(folder):
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("complete") or manifest.get("trials") != 3 or manifest.get("cases") != CASES:
        raise ValueError("Incomplete or different test plan: do not assign final verdicts.")
    snapshot = (folder / "criteria_snapshot.md").read_text(encoding="utf-8-sig")
    digest = hashlib.sha256(normalize(snapshot).encode()).hexdigest()
    # Git am changes commit IDs, so compare the canonical criterion text, not a hash of a commit ID.
    current = (ROOT / "criteria.md").read_text(encoding="utf-8-sig")
    if digest != manifest.get("criteria_sha256") or normalize(snapshot) != normalize(current):
        raise ValueError("Criteria differ from the captured standard; review before evaluating.")
    # Verify exact criterion text for which these checks were written.
    expected_digest = EXPECTED_CRITERIA_SHA256
    if digest != expected_digest:
        raise ValueError("This evaluator does not implement the edited criteria. Update it explicitly before using it.")
    records = [json.loads(line) for line in (folder / "responses.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    expected = {(trial, case["name"]) for trial in range(1, 4) for case in CASES}
    pairs = [(record["trial"], record["case"]["name"]) for record in records]
    if len(pairs) != 39 or len(set(pairs)) != 39 or set(pairs) != expected:
        raise ValueError("Missing, duplicate, or unexpected cases: no complete verdict table can be produced.")
    cases = {case["name"]: case for case in CASES}
    ids = []
    for record in records:
        if record["case"] != cases[record["case"]["name"]]:
            raise ValueError("A recorded payload differs from the test plan.")
        if record["http"].get("request_id"):
            ids.append(record["http"]["request_id"])
    if len(ids) != len(set(ids)):
        raise ValueError("Repeated response IDs: inspect evidence integrity.")
    return manifest, records


def report(folder):
    manifest, records = validate(folder)
    lines = [f"# Capstone {manifest['label']} — measured results", "",
             f"Tested commit: `{manifest['git_commit']}`. Three trials; 39 actual requests.", "",
             "| Criterion | Target per trial | Run 1 | Run 2 | Run 3 | Verdict |",
             "|---|---|---|---|---|---|"]
    failures = []
    for index, check in enumerate(CHECKS):
        applicable = records if index == 0 else [r for r in records if r["case"]["kind"] == ("invalid" if index == 3 else "valid")]
        counts = [sum(bool(check(r)) for r in applicable if r["trial"] == trial) for trial in range(1, 4)]
        target = TARGETS[index]
        verdict = "MET" if all(count == target for count in counts) else "MISSED"
        cells = " | ".join(f"{count}/{target}" for count in counts)
        lines.append(f"| {index + 1}. {TITLES[index]} | {target}/{target}" + (" within 30s" if index == 1 else "") + f" | {cells} | {verdict} |")
        for r in applicable:
            if not check(r):
                log = one_log(r)
                failures.append(f"- C{index + 1}, trial {r['trial']}, `{r['case']['name']}`: HTTP {r['http']['status']}; client {r['http']['client_elapsed_seconds']:.3f}s; ID `{r['http'].get('request_id')}`; matching logs {len(r['matching_logs'])}; calls {log.get('model_calls') if log else 'unavailable'}.")
    lines += ["", "## Misses to diagnose", ""] + (failures or ["All five targets were met. Discuss whether a target was too lenient and what to tighten next."])
    lines += ["", "These are observed failures, not automatic causal diagnoses. Inspect the saved response, log, and producing function before explaining the mechanism.", "", "## Measured usage", ""]
    logs = [one_log(r) for r in records if one_log(r) is not None]
    eligible = [r for r in logs if r.get("path") == "/ask" and r.get("outcome") == "success" and r.get("cache_enabled") is False and r.get("model_calls", 0) > 0]
    try:
        cost = summarize(eligible[:10])
        cost["selection"] = "first ten eligible successful uncached /ask runs from this phase"
        lines += ["```json", json.dumps(cost, indent=2), "```"]
    except ValueError as exc:
        lines.append(f"Usage average unavailable: {exc}")
    lines += ["", "## Actual structured log extract", "", "First ten valid-query log records from trial 1, plus its invalid-input records. Missing records are explicitly noted. These are emitted by serve.finish_record and observability.write_record.", "", "```jsonl"]
    for r in records:
        if r["trial"] == 1:
            if r["matching_logs"]:
                lines += [json.dumps(log, ensure_ascii=False) for log in r["matching_logs"]]
            else:
                lines.append(json.dumps({"missing_log_for_case": r["case"]["name"]}))
    lines += ["```", "", "Full raw responses: responses.jsonl. Explain one actual example per criterion in the README; do not substitute the mock checks for this evidence."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", choices=["before", "after"], required=True)
    args = parser.parse_args()
    folder = ROOT / "results" / f"capstone_{args.label}"
    try:
        result = report(folder)
        destination = folder / "report.md"
        destination.write_text(result, encoding="utf-8")
        print(result.split("## Actual structured log extract")[0])
        print(f"Full report saved to {destination}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Cannot evaluate: {exc}\n")
