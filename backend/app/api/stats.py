"""Prediction statistics endpoint (spec §15, §22)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas import StatsResponse
from backend.app.services import prediction_service

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
def stats(db: Session = Depends(get_db)) -> StatsResponse:
    """Aggregated statistics over all stored predictions."""
    return StatsResponse(**prediction_service.get_stats(db))
