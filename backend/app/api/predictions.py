"""POST /api/v1/predict — image classification (spec §15, §33).

Validation order (clean errors, never a traceback):
1. file type must be jpg/jpeg/png/webp            -> 415
2. upload size must not exceed MAX_UPLOAD_MB      -> 413
3. bytes must decode as a real image              -> 400
4. inference failure / model not loaded           -> 503
"""

import io
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.schemas import PredictionResponse
from backend.app.services import prediction_service
from backend.app.services.inference import InferenceError, ModelInference, get_inference

router = APIRouter(tags=["predictions"])

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
TOP_K_MIN = 1
TOP_K_MAX = 5


def _sanitize_filename(filename: str) -> str:
    """Strip any path components so uploads cannot traverse directories."""
    name = Path(filename or "image").name.strip()
    return name or "image"


def _validate_content(data: bytes) -> None:
    """Reject bytes that do not decode to a real image (spec §41 failure test)."""
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid or corrupted image file: {exc}",
        ) from exc


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    image: UploadFile = File(...),
    top_k: int = Form(default=2),
    db: Session = Depends(get_db),
    model: ModelInference = Depends(get_inference),
) -> dict:
    """Classify an uploaded package image and store the prediction."""
    filename = _sanitize_filename(image.filename or "")
    extension = Path(filename).suffix.lower().lstrip(".")

    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported file type '{extension or 'unknown'}'. "
                f"Allowed types: {allowed}."
            ),
        )

    data = await image.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File too large: {len(data)} bytes exceeds the "
                f"{settings.MAX_UPLOAD_MB} MB limit."
            ),
        )

    _validate_content(data)

    top_k = max(TOP_K_MIN, min(top_k, TOP_K_MAX))

    try:
        result = model.predict(data, top_k=top_k)
    except InferenceError as exc:
        raise HTTPException(status_code=503, detail=f"Inference failed: {exc}") from exc

    prediction = prediction_service.create_prediction(
        db,
        image_name=filename,
        predicted_class=result["predicted_class"],
        confidence=result["confidence"],
        inference_ms=result["inference_ms"],
        model_version=result["model_version"],
        top_k_predictions=result["top_predictions"],
    )

    # Persisted — the response keeps the stable PredictionResponse contract
    # (docs/api.md); the stored row is queryable via /api/v1/predictions/{id}.
    return result
