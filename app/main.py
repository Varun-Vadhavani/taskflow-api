import logging
import time

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.logging_config import setup_logging
from app.routers import tasks

settings = get_settings()
setup_logging(settings.log_level)

logger = logging.getLogger("taskflow.access")
health_logger = logging.getLogger("taskflow.health")

app = FastAPI(
    title=settings.app_name,
    description="A simple task management service.",
    version="0.1.0",
)

app.include_router(tasks.router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request with its status code and duration."""
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("%s %s -> unhandled error", request.method, request.url.path)
        raise
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    """Report that the service process is running."""
    return {"status": "ok"}


@app.get("/health/db", tags=["Health"])
def health_db(db: Session = Depends(get_db)) -> dict[str, str]:
    """Report whether the database is reachable."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        health_logger.exception("Database health check failed")
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok", "database": "ok"}