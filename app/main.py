from fastapi import FastAPI

app = FastAPI(
    title="TaskFlow API",
    description="A simple task management service.",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    """Report that the service is running."""
    return {"status": "ok"}