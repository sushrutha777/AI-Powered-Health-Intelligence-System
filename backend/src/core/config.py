"""
Application configuration using pydantic-settings.

All configuration is loaded from environment variables with validation.
Use get_settings() to access the singleton settings instance.
"""

from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Validates all required configuration at startup to fail fast
    if any critical settings are missing or malformed.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "Health Intelligence System"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT Authentication ───────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── CORS ─────────────────────────────────────────────────────
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── LLM / AI ─────────────────────────────────────────────────
    HUGGINGFACE_API_KEY: str = ""
    LLM_MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.3"

    # ── MLflow ───────────────────────────────────────────────────
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    # ── Vector Store ─────────────────────────────────────────────
    FAISS_INDEX_PATH: str = "ml/models/faiss_index"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",")]
        if isinstance(v, str):
            import json
            parsed: list[str] = [str(item) for item in json.loads(v)]
            return parsed
        return [str(item) for item in v]

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached singleton Settings instance.

    Settings are loaded once from environment variables and reused
    across the application lifetime.
    """
    return Settings()  # type: ignore[call-arg]
