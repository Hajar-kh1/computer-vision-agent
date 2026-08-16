"""Tool 5 — get_model_info (spec §17)."""

from backend.app.api.model_info import model_info


def get_model_info() -> dict:
    """Return deployed model details (name, version, classes, metrics)."""
    try:
        return model_info().model_dump()
    except Exception as exc:  # noqa: BLE001 — tools never raise (spec §18)
        return {"error": f"could not load model info: {exc}"}
