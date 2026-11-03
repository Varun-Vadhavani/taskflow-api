import logging

from app import models  # noqa: F401  (registers the Task table on Base)
from app.config import get_settings
from app.db import Base, engine
from app.logging_config import setup_logging

logger = logging.getLogger("taskflow.init_db")


def init_db() -> None:
    """Create any missing tables."""
    Base.metadata.create_all(engine)
    logger.info("Database tables are ready")


if __name__ == "__main__":
    setup_logging(get_settings().log_level)
    init_db()