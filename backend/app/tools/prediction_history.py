"""Tool 2 — get_prediction_history (spec §17)."""

from backend.app.database import SessionLocal
from backend.app.services import prediction_service


def get_prediction_history(limit: int = 5) -> dict:
    """Return the most recent `limit` stored predictions (newest first)."""
    db = SessionLocal()
    try:
        records = prediction_service.list_predictions(db, limit=max(1, int(limit)))
        return {
            "items": [
                {
                    "id": r.id,
                    "image_name": r.image_name,
                    "predicted_class": r.predicted_class,
                    "confidence": r.confidence,
                    "inference_ms": r.inference_ms,
                    "model_version": r.model_version,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ],
            "total": len(records),
        }
    except Exception as exc:  # noqa: BLE001 — tools never raise (spec §18)
        return {"error": f"could not load prediction history: {exc}"}
    finally:
        db.close()
