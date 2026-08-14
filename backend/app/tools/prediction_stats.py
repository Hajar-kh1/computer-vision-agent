"""Tool 4 — get_prediction_statistics (spec §17)."""

from backend.app.database import SessionLocal
from backend.app.services import prediction_service


def get_prediction_statistics() -> dict:
    """Return aggregated statistics over all stored predictions."""
    db = SessionLocal()
    try:
        return prediction_service.get_stats(db)
    except Exception as exc:  # noqa: BLE001 — tools never raise (spec §18)
        return {"error": f"could not load prediction statistics: {exc}"}
    finally:
        db.close()
