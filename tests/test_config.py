import pytest
from pydantic import ValidationError

from app.config import Settings


def test_defaults_are_used_when_env_is_empty(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)

    settings = Settings(_env_file=None)

    assert settings.app_name == "TaskFlow API"
    assert settings.environment == "development"
    assert settings.log_level == "INFO"


def test_env_vars_override_defaults(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ENVIRONMENT", "production")

    settings = Settings(_env_file=None)

    assert settings.log_level == "DEBUG"
    assert settings.environment == "production"


def test_log_level_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "debug")

    settings = Settings(_env_file=None)

    assert settings.log_level == "DEBUG"


def test_invalid_log_level_fails_fast(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "banana")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)

def test_database_url_is_required(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_database_url_is_hidden_when_printed(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL", "postgresql+psycopg://user:supersecret@localhost:5433/db"
    )

    settings = Settings(_env_file=None)

    assert "supersecret" not in repr(settings)
    assert "supersecret" not in str(settings)