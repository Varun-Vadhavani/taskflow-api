import pytest
from sqlalchemy import func, select

from app.models import Task


def count_tasks(db_session) -> int:
    return db_session.scalar(select(func.count()).select_from(Task))


# ---------- POST /tasks ----------


def test_create_task_minimal(client):
    response = client.post("/tasks", json={"title": "Buy milk"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["title"] == "Buy milk"
    assert body["description"] is None
    assert body["status"] == "todo"
    assert body["due_date"] is None
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


def test_create_task_with_all_fields(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Write report",
            "description": "Quarterly numbers",
            "status": "in_progress",
            "due_date": "2030-01-31",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["description"] == "Quarterly numbers"
    assert body["status"] == "in_progress"
    assert body["due_date"] == "2030-01-31"


def test_create_task_sets_location_header(client):
    response = client.post("/tasks", json={"title": "Buy milk"})

    assert response.headers["location"] == f"/tasks/{response.json()['id']}"


def test_create_task_strips_title(client):
    response = client.post("/tasks", json={"title": "  Buy milk  "})

    assert response.status_code == 201
    assert response.json()["title"] == "Buy milk"


def test_create_task_allows_past_due_date(client):
    response = client.post("/tasks", json={"title": "Old task", "due_date": "2001-01-01"})

    assert response.status_code == 201


def test_create_task_title_boundary(client):
    assert client.post("/tasks", json={"title": "x" * 100}).status_code == 201
    assert client.post("/tasks", json={"title": "x" * 101}).status_code == 422


@pytest.mark.parametrize(
    "bad_body",
    [
        {},
        {"title": ""},
        {"title": "   "},
        {"title": "ok", "status": "finished"},
        {"title": "ok", "due_date": "2026-13-45"},
        {"title": "ok", "description": "d" * 501},
        {"title": "ok", "priorty": "high"},
        {"title": "ok", "id": 5},
        {"title": None},
        {"title": 123},
    ],
)
def test_create_task_rejects_invalid_body_and_stores_nothing(client, db_session, bad_body):
    before = count_tasks(db_session)

    response = client.post("/tasks", json=bad_body)

    assert response.status_code == 422
    assert count_tasks(db_session) == before


def test_create_task_rejects_malformed_json(client):
    response = client.post(
        "/tasks", content="{not json", headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422


# ---------- GET /tasks/{id} ----------


def test_get_existing_task(client):
    created = client.post("/tasks", json={"title": "Buy milk"}).json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@pytest.mark.parametrize("bad_id", ["abc", "0", "-1", "1.5", "99999999999"])
def test_get_task_rejects_invalid_id(client, bad_id):
    response = client.get(f"/tasks/{bad_id}")

    assert response.status_code == 422