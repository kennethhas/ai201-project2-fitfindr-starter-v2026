"""Engineering checks with a stubbed agent, NOT capstone acceptance evidence."""

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from observability import make_logger, write_record
from summarize_usage import summarize


class ObservabilityChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "requests.jsonl"
        self.env = patch.dict(os.environ, {"FITFINDR_LOG_PATH": str(self.path)})
        self.env.start()
        self.addCleanup(self.env.stop)
        import serve
        self.serve = serve
        self.logger = make_logger(self.path)
        self.logger_patch = patch.object(serve, "request_logger", self.logger)
        self.logger_patch.start()
        self.addCleanup(self.logger_patch.stop)
        self.addCleanup(self.close_logger)
        self.client = serve.app.test_client()

    def close_logger(self):
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

    def records(self):
        return [json.loads(line) for line in self.path.read_text().splitlines()]

    def test_response_unchanged_and_request_id_links_log(self):
        session = {"error": None, "fit_card": "stubbed output"}
        with patch.object(self.serve, "run_agent", return_value=session):
            response = self.client.post("/ask", json={"query": "tee"})
        self.assertEqual(response.get_json(), session)
        records = self.records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["request_id"], response.headers["X-Request-ID"])
        self.assertEqual(records[0]["input"], {"query": "tee"})
        self.assertEqual(records[0]["output"], session)
        self.assertGreaterEqual(records[0]["duration_ms"], records[0]["agent_ms"])

    def test_rejection_and_raised_failure_are_recorded(self):
        self.assertEqual(self.client.post("/ask", json={}).status_code, 400)
        with patch.object(self.serve, "run_agent", side_effect=RuntimeError("stubbed failure")):
            self.assertEqual(self.client.post("/ask", json={"query": "tee"}).status_code, 500)
        records = self.records()
        self.assertEqual([r["outcome"] for r in records], ["rejected", "error"])
        self.assertIn("stubbed failure", records[1]["output"]["error"])

    def test_usage_is_per_request_and_stopped_session_is_not_success(self):
        with patch.object(self.serve, "run_agent", return_value={"error": "no match"}), \
             patch.object(self.serve.generate, "call_count", side_effect=[4, 6]), \
             patch.object(self.serve.generate, "token_counts", side_effect=[
                 {"prompt": 100, "output": 20, "total": 120},
                 {"prompt": 150, "output": 30, "total": 180},
             ]):
            self.client.post("/ask", json={"query": "tee"})
        record = self.records()[0]
        self.assertEqual(record["model_calls"], 2)
        self.assertEqual(record["reported_tokens"]["total"], 60)
        self.assertEqual(record["outcome"], "agent_stopped")

    def test_redaction_and_rotation_preserve_json_lines(self):
        self.logger.handlers[0].maxBytes = 180
        with patch.dict(os.environ, {"GEMINI_API_KEY": "synthetic-secret"}):
            for _ in range(10):
                write_record(self.logger, {"api_key": "synthetic-secret", "text": "echo synthetic-secret", "value": float("nan")})
        paths = list(Path(self.temp.name).glob("requests.jsonl*"))
        self.assertEqual(len(paths), 3)
        for path in paths:
            text = path.read_text()
            self.assertNotIn("synthetic-secret", text)
            for line in text.splitlines():
                self.assertEqual(json.loads(line)["api_key"], "[REDACTED]")

    def test_cost_summary_requires_real_uncached_runs(self):
        self.client.get("/health")
        with self.assertRaisesRegex(ValueError, "found 0"):
            summarize(self.records())


if __name__ == "__main__":
    unittest.main()
