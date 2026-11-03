from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import Task, TaskStatus
from app.schemas import TaskCreate, TaskRead, TaskUpdate


def test_create_minimal_uses_defaults():
    task = TaskCreate(title="Buy milk")

    assert task.title == "Buy milk"
    assert task.description is None
    assert task.status == TaskStatus.todo
    assert task.due_date is None


def test_title_is_stripped():
    assert TaskCreate(title="  Buy milk  ").title == "Buy milk"


def test_empty_title_rejected():
    with pytest.raises(ValidationError):
        TaskCreate(title="")


def test_whitespace_only_title_rejected():
    with pytest.raises(ValidationError):
        TaskCreate(title="     ")


def test_title_length_boundary():
    assert len(TaskCreate(title="x" * 100).title) == 100

    with pytest.raises(ValidationError):
        TaskCreate(title="x" * 101)


def test_description_length_boundary():
    assert len(TaskCreate(title="t", description="d" * 500).description) == 500

    with pytest.raises(ValidationError):
        TaskCreate(title="t", description="d" * 501)


def test_invalid_status_rejected():
    with pytest.raises(ValidationError):
        TaskCreate(title="t", status="finished")


def test_invalid_due_date_rejected():
    with pytest.raises(ValidationError):
        TaskCreate(title="t", due_date="2026-13-45")

    with pytest.raises(ValidationError):
        TaskCreate(title="t", due_date="not-a-date")


def test_unknown_field_rejected():
    with pytest.raises(ValidationError):
        TaskCreate(title="t", priorty="high")


def test_update_empty_body_rejected():
    with pytest.raises(ValidationError):
        TaskUpdate()


def test_update_partial_only_contains_supplied_fields():
    update = TaskUpdate(status="done")

    assert update.model_dump(exclude_unset=True) == {"status": TaskStatus.done}


def test_update_null_title_rejected():
    with pytest.raises(ValidationError):
        TaskUpdate(title=None)


def test_update_can_clear_description():
    update = TaskUpdate(description=None)

    assert update.model_dump(exclude_unset=True) == {"description": None}


def test_read_schema_builds_from_orm_object():
    now = datetime.now(timezone.utc)
    task = Task(
        id=1,
        title="Buy milk",
        description=None,
        status=TaskStatus.todo,
        due_date=None,
        created_at=now,
        updated_at=now,
    )

    read = TaskRead.model_validate(task)

    assert read.id == 1
    assert read.title == "Buy milk"