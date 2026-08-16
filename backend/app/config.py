"""Application settings (spec §28, §34).

Reads from environment variables / .env via pydantic-settings.
All fields mirror .env.example so local dev, Docker Compose and Dokploy
all configure the same way.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the backend service."""

    # PostgreSQL connection string (psycopg driver).
    # Docker Compose: postgresql+psycopg://cvuser:cvpassword@postgres:5432/cvapp
    DATABASE_URL: str = "postgresql+psycopg://cvuser:cvpassword@localhost:5432/cvapp"

    # Model artifact + version.
    MODEL_PATH: str = "models/model.pt"
    MODEL_VERSION: str = "1.0.0"

    # CORS: comma-separated list of allowed origins.
    # Local dev: http://localhost:5173,http://localhost:3000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Max upload size in MB (security: limit oversized uploads).
    MAX_UPLOAD_MB: int = 10

    # LLM provider (used by agent tool calling / Open WebUI).
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_MODEL: str = ""

    # LangFuse LLM observability (optional — tracing of agent LLM calls).
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Production hardening.
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Parse the comma-separated CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        """Max upload size expressed in bytes."""
        return self.MAX_UPLOAD_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (pydantic reads env once)."""
    return Settings()


settings = get_settings()
