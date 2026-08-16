"""Model information endpoint (spec §15, §17-Tool5)."""

import json
from pathlib import Path

from fastapi import APIRouter, Depends

from backend.app.config import settings
from backend.app.schemas import ModelInfoResponse
from backend.app.services import inference as inference_service

router = APIRouter(tags=["model"])


def _read_json(path: Path) -> dict | None:
    """Read a JSON file if it exists; return None otherwise."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError):
        return None


@router.get("/model", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    """Deployed model details: name, version, classes, input size, metrics."""
    model_dir = Path(settings.MODEL_PATH).parent

    # Live facts come from the loaded model (ground truth, spec §18).
    inference = inference_service._inference
    if inference is not None:
        model_name = inference.model_name
        version = inference.model_version
        classes = list(inference.class_names)
        input_size = inference.input_size
        deployment_status = "deployed"
    else:
        model_name = "mobilenet_v3_small"
        version = settings.MODEL_VERSION
        classes = _classes_from_labels(model_dir)
        input_size = 224
        deployment_status = "not_loaded"

    metrics = _read_json(Path("reports/model_metrics.json"))
    if metrics is None:
        metrics = _read_json(model_dir.parent / "reports" / "model_metrics.json")

    return ModelInfoResponse(
        model_name=model_name,
        version=version,
        classes=classes,
        input_size=input_size,
        metrics=metrics,
        deployment_status=deployment_status,
    )


def _classes_from_labels(model_dir: Path) -> list[str]:
    """Fallback: read class names from models/labels.json (index -> name)."""
    labels = _read_json(model_dir / "labels.json") or {}
    ordered = sorted(labels.items(), key=lambda item: int(item[0]))
    return [name for _, name in ordered] or ["damaged", "undamaged"]
