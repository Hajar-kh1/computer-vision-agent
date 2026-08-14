"""Prediction history endpoints (spec §15)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas import PredictionList, PredictionOut
from backend.app.services import prediction_service

router = APIRouter(tags=["predictions"])

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


@router.get("/predictions", response_model=PredictionList)
def list_predictions(
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
) -> PredictionList:
    """Return the most recent predictions (newest first)."""
    limit = max(1, min(limit, MAX_LIMIT))
    records = prediction_service.list_predictions(db, limit=limit)
    return PredictionList(items=[PredictionOut.model_validate(r) for r in records],
                          total=len(records))


@router.get("/predictions/{prediction_id}", response_model=PredictionOut)
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
) -> PredictionOut:
    """Return a single stored prediction; 404 with a clean message if missing."""
    record = prediction_service.get_prediction(db, prediction_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Prediction {prediction_id} not found.",
        )
    return PredictionOut.model_validate(record)
