import os

# Must run before app modules are imported, because they read settings at import time.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://taskflow:taskflow_dev_pw@localhost:5433/taskflow",
)

import pytest  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app import models  # noqa: E402, F401  (registers the Task table on Base)
from app.db import Base, engine  # noqa: E402


@pytest.fixture
def db_session():
    """A session whose changes are always rolled back after the test."""
    Base.metadata.create_all(engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()