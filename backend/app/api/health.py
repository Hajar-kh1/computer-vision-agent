"""GET /health — liveness + readiness (spec §32).

Production health check verifies API, database, and model:

    {"status": "healthy", "api": "healthy", "database": "healthy", "model": "loaded"}
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas import HealthResponse
from backend.app.services import inference as inference_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    """Liveness + readiness. 200 when the API is up; sub-statuses for DB/model."""
    # Database readiness: cheap SELECT 1; a broken DB must not take the API down.
    try:
        db.execute(text("SELECT 1"))
        database = "healthy"
    except Exception:  # noqa: BLE001 — health must never 500
        database = "unhealthy"

    model = "loaded" if inference_service._inference is not None else "not_loaded"

    return HealthResponse(
        status="healthy",
        api="healthy",
        database=database,
        model=model,
    )
