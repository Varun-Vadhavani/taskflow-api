import pytest
from sqlalchemy.exc import DataError, IntegrityError

from app.models import Task, TaskStatus


def test_task_gets_defaults_from_database(db_session):
    task = Task(title="Buy milk")
    db_session.add(task)
    db_session.flush()
    db_session.refresh(task)

    assert task.id is not None
    assert task.status == TaskStatus.todo
    assert task.description is None
    assert task.due_date is None
    assert task.created_at is not None
    assert task.updated_at is not None


def test_database_rejects_missing_title(db_session):
    db_session.add(Task(title=None))

    with pytest.raises(IntegrityError):
        db_session.flush()


def test_database_rejects_overlong_title(db_session):
    db_session.add(Task(title="x" * 101))

    with pytest.raises(DataError):
        db_session.flush()