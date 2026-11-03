import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db import get_db
from app.main import app

client = TestClient(app)


class BrokenSession:
    """A fake session that behaves like a database that is down."""

    def execute(self, *args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    def close(self):
        pass


@pytest.fixture
def broken_db():
    def override():
        yield BrokenSession()

    app.dependency_overrides[get_db] = override
    yield
    app.dependency_overrides.clear()


def test_health_db_ok_with_real_database():
    # Needs `docker compose up -d` running.
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_db_returns_503_when_database_is_down(broken_db):
    response = client.get("/health/db")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}


def test_plain_health_still_works_when_database_is_down(broken_db):
    response = client.get("/health")

    assert response.status_code == 200