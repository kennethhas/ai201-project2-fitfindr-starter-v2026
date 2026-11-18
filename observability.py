"""Structured HTTP records for the capstone; no model or agent logic here."""

import json
import logging
import math
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def redact(value):
    """Exclude credential fields and the configured key, including echoed text.

    This is not general PII detection: use synthetic clothing inputs for evidence.
    """
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {
            k: "[REDACTED]" if str(k).lower() in {
                "api_key", "gemini_api_key", "authorization", "password", "token"
            } else redact(v)
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        key = os.getenv("GEMINI_API_KEY", "").strip()
        return value.replace(key, "[REDACTED]") if key else value
    return value


def make_logger(path=None):
    path = Path(path or os.getenv("FITFINDR_LOG_PATH", "logs/requests.jsonl")).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"fitfindr.requests.{path}")
    # Audit records always stay enabled; Flask/server verbosity is separate.
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = RotatingFileHandler(
            path, maxBytes=5_000_000, backupCount=2, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger


def write_record(logger, record):
    logger.info(json.dumps(redact(record), ensure_ascii=False, allow_nan=False))
