import os

# Must run before app modules are imported, because they read settings at import time.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://taskflow:taskflow_dev_pw@localhost:5433/taskflow",
)