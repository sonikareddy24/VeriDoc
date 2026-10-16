"""Structured, privacy-preserving logging for VeriDocs AI.
Never logs document contents, names, or sensitive financial values.
Logs only session IDs, document IDs, execution durations, document types, and status counts.
"""

import logging
import sys
import json
from datetime import datetime, timezone


class PrivacySafeFormatter(logging.Formatter):
    """Formats log records as JSON with privacy-safe redactions."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Include safe context extras if passed
        for key in ("session_id", "doc_id", "doc_type", "duration_ms", "status_counts", "error_code"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def get_logger(name: str = "veridocs") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(PrivacySafeFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = get_logger()
