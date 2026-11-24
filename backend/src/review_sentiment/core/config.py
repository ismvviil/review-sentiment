"""
Application settings (12-factor): defaults here, overridable with environment variables
prefixed ``SENTIMENT_`` or a ``.env`` file, e.g. ``SENTIMENT_MODEL_VERSION=20261124-093100``.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SENTIMENT_", env_file=BACKEND_ROOT / ".env", extra="ignore"
    )

    app_name: str = "Review Sentiment API"
    environment: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"

    # Model artifacts (written by the training pipeline, read by the API)
    artifacts_dir: Path = BACKEND_ROOT / "artifacts"
    model_name: str = "sentiment-classifier"
    model_version: str = "latest"
    # "torch" (sentence-transformers), "onnx" (same vectors, ~5x less RAM) or "auto"
    encoder_runtime: Literal["auto", "torch", "onnx"] = "auto"

    # Business rules
    max_review_chars: int = Field(default=5000, gt=0)
    max_batch_size: int = Field(default=100, gt=0)

    # HTTP
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    # Folder with the built React app (frontend/dist). When set, the API also serves the
    # website on "/" -> one single URL in production. Unset in development (Vite serves it).
    static_dir: Path | None = None


@lru_cache
def get_settings() -> Settings:
    """Singleton accessor - settings are read once per process."""
    return Settings()
