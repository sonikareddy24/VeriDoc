"""Application configuration loaded from environment with safe zero-setup defaults."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "VeriDocs AI"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Storage & Session Limits
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    TEMP_STORAGE_DIR: Path = BASE_DIR / "data" / "sessions_temp"
    SESSION_TTL_SECONDS: int = 3600  # 1 hour
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
    MAX_PAGES_PER_DOC: int = 10
    MAX_IMAGE_PIXELS: int = 25_000_000  # Pillow decompression defense

    # Active Extractor Backend: "ocr_rules", "vlm_zero_shot", "vlm_lora"
    DEFAULT_EXTRACTOR_BACKEND: str = "ocr_rules"
    OCR_ENGINE: str = "rapidocr"
    FUZZY_MATCH_THRESHOLD: float = 85.0
    NUMERIC_TOLERANCE_ABSOLUTE: float = 0.05  # For currency float rounding checks

    # Cross-document comparison tolerances
    SALARY_MATCH_WINDOW_DAYS: int = 7


settings = Settings()
