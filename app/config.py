from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Application configuration, loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "TaskFlow API"
    environment: str = "development"
    log_level: LogLevel = "INFO"
    database_url: SecretStr

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Accept 'debug' as well as 'DEBUG'."""
        if isinstance(value, str):
            return value.strip().upper()
        return value


@lru_cache
def get_settings() -> Settings:
    """Create Settings once and reuse it."""
    return Settings()