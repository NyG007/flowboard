# ============================================================
# FlowBoard — Application Configuration
# Uses pydantic-settings for type-safe env var management.
# All settings are validated at startup — fail fast if misconfigured.
# ============================================================

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator
from typing import Annotated, Any
import json


class Settings(BaseSettings):
    """
    Central settings class. Reads from environment variables and .env file.
    Using Pydantic ensures:
    - Type coercion (str "true" → bool True)
    - Validation at startup, not at runtime
    - Self-documenting code (types serve as documentation)
    """

    # --- Application ---
    APP_NAME: str = "FlowBoard"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security ---
    # CRITICAL: Must be a long random string in production.
    # Generate: openssl rand -hex 32
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Database ---
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # --- CORS ---
    # Accepts JSON string: '["http://localhost:5173"]'
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from JSON string or list."""
        if isinstance(v, str):
            return json.loads(v)
        return v

    @property
    def DATABASE_URL(self) -> str:
        """
        Async PostgreSQL connection URL.
        asyncpg driver is required for FastAPI's async support.
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """
        Sync URL for Alembic migrations (Alembic doesn't support async natively).
        """
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Pydantic v2 config — look for .env file in project root
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Singleton instance — import this everywhere:
# from app.core.config import settings
settings = Settings()