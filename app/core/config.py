"""Application configuration.

Centralised, type-safe settings loaded from environment variables (and a local
`.env` file in development) via `pydantic-settings`. Import the singleton
`settings` anywhere in the app instead of reading `os.environ` directly — this
keeps configuration in one place and validated at startup.

    from app.core.config import settings
    print(settings.DATABASE_URL)
"""

from enum import Enum
from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Environment(str, Enum):
    """Deployment environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class LLMProvider(str, Enum):
    """Supported large-language-model providers."""

    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Values are read from environment variables; in development a `.env` file at
    the project root is loaded automatically. Unknown variables are ignored.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "AI Travel Planner"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # --- Docs / API surface ---
    DOCS_ENABLED: bool = True  # disable interactive docs in hardened deployments

    # --- Rate limiting (fixed-window, per client IP) ---
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # --- Security ---
    SECRET_KEY: str = "change-me"
    # `NoDecode` stops pydantic-settings from JSON-decoding the raw env value so
    # our validator can accept a plain comma-separated string.
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(
        default_factory=list
    )

    # --- LLM ---
    LLM_PROVIDER: LLMProvider = LLMProvider.OPENAI
    LLM_TEMPERATURE: float = 0.2

    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o"

    GOOGLE_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-pro"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # --- LangSmith observability ---
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str | None = None
    LANGCHAIN_PROJECT: str = "travel-planner"

    # --- PostgreSQL ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://travel:travel@localhost:5432/travel_planner"
    )

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Cache ---
    CACHE_ENABLED: bool = True
    CACHE_BACKEND: str = "redis"  # redis | memory
    # Per-category time-to-live in seconds (tuned to how fast each changes).
    CACHE_TTL_WEATHER: int = 21600  # 6 hours  — climate/forecast moves slowly
    CACHE_TTL_HOTELS: int = 1800  # 30 minutes — inventory changes moderately
    CACHE_TTL_FLIGHTS: int = 300  # 5 minutes  — fares/seats change quickly

    # --- External travel APIs ---
    WEATHER_API_KEY: str | None = None
    FLIGHTS_API_KEY: str | None = None
    HOTELS_API_KEY: str | None = None

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        """Allow CORS origins to be supplied as a comma-separated string."""
        if isinstance(value, str) and not value.startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.APP_ENV is Environment.PRODUCTION

    @model_validator(mode="after")
    def _enforce_production_safety(self) -> "Settings":
        """Fail fast on insecure production configuration."""
        if self.is_production:
            if self.SECRET_KEY == "change-me":
                raise ValueError(
                    "SECRET_KEY must be set to a strong, unique value in "
                    "production (the default 'change-me' is not allowed)."
                )
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached `Settings` instance (read once per process)."""
    return Settings()


# Convenience singleton for direct import.
settings: Settings = get_settings()
