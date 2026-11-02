import logging

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_request_is_logged(caplog):
    caplog.set_level(logging.INFO, logger="taskflow.access")

    client.get("/health")

    messages = [record.getMessage() for record in caplog.records]
    assert any("GET /health -> 200" in message for message in messages)


def test_404_is_logged_with_status(caplog):
    caplog.set_level(logging.INFO, logger="taskflow.access")

    client.get("/nope")

    messages = [record.getMessage() for record in caplog.records]
    assert any("GET /nope -> 404" in message for message in messages)