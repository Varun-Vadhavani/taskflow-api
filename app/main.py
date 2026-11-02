import logging
import time

from fastapi import FastAPI, Request

from app.config import get_settings
from app.logging_config import setup_logging

settings = get_settings()
setup_logging(settings.log_level)

logger = logging.getLogger("taskflow.access")

app = FastAPI(
    title=settings.app_name,
    description="A simple task management service.",
    version="0.1.0",
)


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
    """Report that the service is running."""
    return {"status": "ok"}