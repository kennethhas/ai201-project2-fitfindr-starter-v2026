"""Collect real HTTP evidence, three trials; never invent criterion verdicts.

Run only after reviewing the cases and committing your capstone criteria:
    python capture_capstone.py --label before
    python capture_capstone.py --label after
The local server must already be running with AI201_CACHE=0.
"""

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import config
from observability import redact

ROOT = Path(__file__).resolve().parent
# Test inputs, not acceptance criteria. Review before collecting the baseline.
QUERIES = [
    ("graphic tee under $30", 30), ("jeans under $40", 40),
    ("flannel shirt under $30", 30), ("track jacket under $50", 50),
    ("cardigan under $40", 40), ("leather belt under $20", 20),
    ("graphic hoodie under $30", 30), ("sneakers under $50", 50),
    ("boots under $50", 50), ("shoulder bag under $40", 40),
]
CASES = [
    {"name": f"valid_{i + 1}", "kind": "valid", "payload": {"query": query}, "budget": budget}
    for i, (query, budget) in enumerate(QUERIES)
] + [
    {"name": "missing_query", "kind": "invalid", "payload": {}},
    {"name": "blank_query", "kind": "invalid", "payload": {"query": "   "}},
    {"name": "numeric_query", "kind": "invalid", "payload": {"query": 123}},
]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def normalize(text):
    return text.replace("\r\n", "\n").strip()


def read_logs(path):
    # A request can be in a rotated file. Keep all matches to detect duplicates.
    records = []
    for source in [Path(str(path) + ".2"), Path(str(path) + ".1"), path]:
        if source.exists():
            for line in source.read_text(encoding="utf-8").splitlines():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    # An unrelated concurrent writer may have an incomplete tail.
                    continue
    return records


def post(url, payload):
    req = Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        response = urlopen(req, timeout=240)
    except HTTPError as exc:
        response = exc  # 400/500 responses are evidence, not reasons to skip a case.
    with response:
        raw = response.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {"non_json_body": raw}
        return {
            "status": response.code, "body": body,
            "request_id": response.headers.get("X-Request-ID"),
            "client_elapsed_seconds": time.perf_counter() - started,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, choices=["before", "after"])
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--log", type=Path, default=ROOT / "logs/requests.jsonl")
    args = parser.parse_args()
    criteria = ROOT / "criteria.md"
    text = criteria.read_text(encoding="utf-8-sig")
    if "capstone" not in text.lower():
        parser.error("criteria.md still appears to contain the old criteria. Write your Unit 9 criteria first.")
    if normalize(text) != normalize(git("show", "HEAD:criteria.md")):
        parser.error("Commit criteria.md before collecting acceptance evidence.")
    if git("diff", "HEAD", "--name-only"):
        parser.error("Commit tracked code changes first so evidence identifies the exact tested version.")
    if not git("ls-files", "capture_capstone.py"):
        parser.error("Commit this collector before running it.")
    if config.CACHE_ENABLED:
        parser.error("Set AI201_CACHE=0 in this terminal AND the server terminal.")
    with urlopen(args.url.rstrip("/") + "/health", timeout=10) as response:
        if json.load(response).get("status") != "ok":
            parser.error("Server health check did not return ok.")
        health_id = response.headers.get("X-Request-ID")
    health_logs = [r for r in read_logs(args.log) if health_id and r.get("request_id") == health_id]
    if len(health_logs) != 1 or health_logs[0].get("cache_enabled") is not False:
        parser.error("Cannot confirm uncached server and matching local log. Restart with AI201_CACHE=0 and check --log.")
    digest = hashlib.sha256(normalize(text).encode()).hexdigest()
    folder = ROOT / "results" / f"capstone_{args.label}"
    if args.label == "after":
        before = ROOT / "results/capstone_before/manifest.json"
        if not before.exists():
            parser.error("Collect and diagnose the before evidence first.")
        baseline = json.loads(before.read_text(encoding="utf-8"))
        if not baseline.get("complete"):
            parser.error("The before collection is incomplete. Resolve that before running the after phase.")
        if baseline.get("criteria_sha256") != digest or baseline.get("cases") != CASES:
            parser.error("Criteria or inputs changed. Preserve the original standard; document any necessary revision separately.")
    if folder.exists():
        parser.error(f"{folder} already exists. Evidence will not be overwritten; inspect it before a new attempt.")
    folder.mkdir(parents=True)
    manifest = {
        "label": args.label, "started_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git("rev-parse", "HEAD"), "criteria_sha256": digest,
        "trials": 3, "cases": CASES, "base_url": args.url,
        "definition": "Warm server process; includes MCP startup and model waits. Ten-second pacing between valid cases.",
        "complete": False,
    }
    manifest_path = folder / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (folder / "criteria_snapshot.md").write_text(text, encoding="utf-8")
    try:
        with (folder / "responses.jsonl").open("x", encoding="utf-8") as output:
            for trial in range(1, 4):
                for case in CASES:
                    print(f"Trial {trial}/3: {case['name']} ...", flush=True)
                    result = post(args.url.rstrip("/") + "/ask", case["payload"])
                    matches = [r for r in read_logs(args.log) if result["request_id"] and r.get("request_id") == result["request_id"]]
                    record = redact({"trial": trial, "case": case, "http": result, "matching_logs": matches})
                    output.write(json.dumps(record, ensure_ascii=False) + "\n")
                    output.flush()
                    print(f"  HTTP {result['status']}; {result['client_elapsed_seconds']:.2f}s; log matches: {len(matches)}", flush=True)
                    if case["kind"] == "valid":
                        time.sleep(10)  # Two model calls per valid query; leave quota headroom.
        manifest["complete"] = True
        print(f"Saved 39 actual responses to {folder}. No verdicts have been assigned.")
    except (URLError, TimeoutError, OSError, KeyboardInterrupt) as exc:
        manifest["interruption"] = redact(f"{type(exc).__name__}: {exc}")
        print("Stopped. Partial evidence has been preserved. Do not treat it as a completed evaluation.")
    finally:
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if not manifest["complete"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
