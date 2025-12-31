from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health_check():
    """
    Health check endpoint.
    Used to verify the application is running.
    """
    return {"status": "ok"}
