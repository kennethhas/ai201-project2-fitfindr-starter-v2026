"""Synthetic evaluator unit tests; these are NOT live capstone results."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from capture_capstone import CASES, ROOT
from evaluate_capstone import EXPECTED_CRITERIA_SHA256, report


def fixtures():
    records = []
    for trial in range(1, 4):
        for case in CASES:
            valid = case["kind"] == "valid"
            body = {
                "error": None, "selected_item": {"id": "synthetic", "price": 10},
                "search_results": [{"id": "synthetic", "price": 10}],
                "outfit_suggestion": "stub", "fit_card": "stub",
            } if valid else {"error": "synthetic invalid input"}
            request_id = f"synthetic-{trial}-{case['name']}"
            status = 200 if valid else 400
            log = {
                "timestamp": "2000-01-01T00:00:00+00:00", "request_id": request_id,
                "method": "POST", "path": "/ask", "input": case["payload"],
                "output": body, "status_code": status, "duration_ms": 100,
                "outcome": "success" if valid else "rejected", "cache_enabled": False,
                "model_calls": 2 if valid else 0,
                "reported_tokens": {"prompt": 100, "output": 20, "total": 120} if valid else {"prompt": 0, "output": 0, "total": 0},
            }
            records.append({"trial": trial, "case": case, "http": {
                "status": status, "body": body, "request_id": request_id,
                "client_elapsed_seconds": 0.2,
            }, "matching_logs": [log]})
    return records


class EvaluatorChecks(unittest.TestCase):
    def make_report(self, records, complete=True):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = {"complete": complete, "trials": 3, "cases": CASES,
                        "criteria_sha256": EXPECTED_CRITERIA_SHA256,
                        "label": "synthetic", "git_commit": "synthetic-not-a-real-run"}
            (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "criteria_snapshot.md").write_bytes((ROOT / "criteria.md").read_bytes())
            (root / "responses.jsonl").write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
            return report(root)

    def test_pass_counts_and_usage_arithmetic(self):
        text = self.make_report(fixtures())
        self.assertEqual(text.count("| MET |"), 5)
        self.assertIn('"reported_prompt_plus_output_tokens_sum": 1200', text)
        self.assertIn('"daily_reported_prompt_plus_output_tokens": 12000', text)

    def test_one_failed_trial_means_missed(self):
        records = copy.deepcopy(fixtures())
        records[0]["http"]["client_elapsed_seconds"] = 30.001
        text = self.make_report(records)
        self.assertIn("| 2. HTTP response time | 10/10 within 30s | 9/10 | 10/10 | 10/10 | MISSED |", text)

    def test_missing_logs_and_invalid_status_are_not_hidden(self):
        records = copy.deepcopy(fixtures())
        records[0]["matching_logs"] = []
        records[12]["http"]["status"] = 500
        text = self.make_report(records)
        self.assertIn("| 1. Complete request records | 13/13 | 11/13 | 13/13 | 13/13 | MISSED |", text)
        self.assertIn("| 4. Invalid input rejection | 3/3 | 2/3 | 3/3 | 3/3 | MISSED |", text)

    def test_missing_and_duplicate_cases_are_rejected(self):
        records = fixtures()
        with self.assertRaises(ValueError):
            self.make_report(records[:-1])
        records[-1] = records[0]
        with self.assertRaises(ValueError):
            self.make_report(records)

    def test_partial_run_cannot_get_verdicts(self):
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            self.make_report(fixtures(), complete=False)

    def test_missing_tokens_and_over_budget_are_misses(self):
        records = copy.deepcopy(fixtures())
        records[0]["matching_logs"][0]["reported_tokens"]["output"] = 0
        records[1]["http"]["body"]["selected_item"]["price"] = 1000
        text = self.make_report(records)
        self.assertIn("| 3. Recorded model usage | 10/10 | 9/10 | 10/10 | 10/10 | MISSED |", text)
        self.assertIn("| 5. Preserve original behavior | 10/10 | 9/10 | 10/10 | 10/10 | MISSED |", text)


if __name__ == "__main__":
    unittest.main()
