"""Prediction persistence + query service (spec §16)."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import Prediction


def create_prediction(
    db: Session,
    *,
    image_name: str,
    predicted_class: str,
    confidence: float,
    inference_ms: float,
    model_version: str,
    top_k_predictions: list | None = None,
) -> Prediction:
    """Insert a prediction row, commit, and return the refreshed record."""
    prediction = Prediction(
        image_name=image_name,
        predicted_class=predicted_class,
        confidence=confidence,
        inference_ms=inference_ms,
        model_version=model_version,
        top_k_predictions=top_k_predictions or [],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def list_predictions(db: Session, limit: int = 20) -> list[Prediction]:
    """Return the most recent `limit` predictions (newest first)."""
    statement = (
        select(Prediction)
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .limit(limit)
    )
    return list(db.scalars(statement))


def get_prediction(db: Session, prediction_id: int) -> Prediction | None:
    """Return a single prediction by id, or None if missing."""
    return db.get(Prediction, prediction_id)


def get_stats(db: Session) -> dict:
    """Aggregate: total, per-class distribution, avg confidence, avg latency."""
    total = db.scalar(select(func.count()).select_from(Prediction)) or 0

    distribution: dict[str, int] = {}
    for class_name, count in db.execute(
        select(Prediction.predicted_class, func.count()).group_by(
            Prediction.predicted_class
        )
    ):
        distribution[str(class_name)] = int(count)

    avg_confidence = db.scalar(select(func.avg(Prediction.confidence)))
    avg_inference_ms = db.scalar(select(func.avg(Prediction.inference_ms)))

    return {
        "total_predictions": int(total),
        "class_distribution": distribution,
        "avg_confidence": round(float(avg_confidence), 4) if avg_confidence else None,
        "avg_inference_ms": round(float(avg_inference_ms), 2)
        if avg_inference_ms
        else None,
    }
