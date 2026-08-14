"""Tool 3 — get_prediction_by_id (spec §17)."""

from backend.app.database import SessionLocal
from backend.app.services import prediction_service


def get_prediction_by_id(prediction_id: int) -> dict:
    """Return a single stored prediction, or a clear 'not found' message."""
    db = SessionLocal()
    try:
        record = prediction_service.get_prediction(db, int(prediction_id))
        if record is None:
            return {"error": f"prediction {prediction_id} not found"}
        return {
            "id": record.id,
            "image_name": record.image_name,
            "predicted_class": record.predicted_class,
            "confidence": record.confidence,
            "inference_ms": record.inference_ms,
            "model_version": record.model_version,
            "top_k_predictions": record.top_k_predictions,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
    except Exception as exc:  # noqa: BLE001 — tools never raise (spec §18)
        return {"error": f"could not load prediction {prediction_id}: {exc}"}
    finally:
        db.close()
