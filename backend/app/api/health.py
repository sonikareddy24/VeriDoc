"""Health, configuration, and research experiment discovery endpoints."""

import json
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter()


@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.ENVIRONMENT,
    }


@router.get("/config")
def get_config():
    return {
        "active_extractor_backend": settings.DEFAULT_EXTRACTOR_BACKEND,
        "ocr_engine": settings.OCR_ENGINE,
        "limits": {
            "max_file_size_bytes": settings.MAX_FILE_SIZE_BYTES,
            "max_file_size_mb": settings.MAX_FILE_SIZE_BYTES // (1024 * 1024),
            "max_pages_per_doc": settings.MAX_PAGES_PER_DOC,
            "session_ttl_seconds": settings.SESSION_TTL_SECONDS,
        },
        "fuzzy_match_threshold": settings.FUZZY_MATCH_THRESHOLD,
        "supported_mime_types": ["application/pdf", "image/png", "image/jpeg"],
    }


@router.get("/experiments")
def get_experiment_results():
    """Checks results/ directory for evaluation benchmark artifacts."""
    results_dir = settings.BASE_DIR / "results"
    summary_file = results_dir / "latest_metrics.json"

    if summary_file.exists():
        try:
            with open(summary_file, "r") as f:
                data = json.load(f)
            return {"has_results": True, "results": data}
        except Exception:
            pass

    return {
        "has_results": False,
        "message": "Research evaluation experiments have not been executed yet.",
        "command": "make eval",
        "quick_command": "python eval/run_eval.py --profile quick",
    }
