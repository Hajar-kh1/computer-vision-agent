"""Pydantic schemas (spec §14, §15).

The standard inference output shape is a stable contract — the frontend
(frontend/src/api.js) and the agent tools (agent/tools.py, openwebui/)
depend on it. Do not rename fields without updating those consumers.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Inference output
# ---------------------------------------------------------------------------

class TopPrediction(BaseModel):
    """One entry of the top-K predictions."""

    class_name: str
    probability: float


class PredictionResponse(BaseModel):
    """Standard response of POST /api/v1/predict (stable contract)."""

    predicted_class: str
    confidence: float
    top_predictions: list[TopPrediction]
    inference_ms: float
    model_version: str


# ---------------------------------------------------------------------------
# Stored prediction records
# ---------------------------------------------------------------------------

class PredictionOut(BaseModel):
    """A single stored prediction record (DB row)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    image_name: str
    predicted_class: str
    confidence: float
    inference_ms: float
    model_version: str
    top_k_predictions: list[TopPrediction] = []
    created_at: datetime


class PredictionList(BaseModel):
    """List of stored predictions (newest first)."""

    items: list[PredictionOut]
    total: int


# ---------------------------------------------------------------------------
# Statistics / model info / health
# ---------------------------------------------------------------------------

class StatsResponse(BaseModel):
    """Aggregated statistics over all stored predictions."""

    total_predictions: int
    class_distribution: dict[str, int]
    avg_confidence: float | None = None
    avg_inference_ms: float | None = None


class ModelInfoResponse(BaseModel):
    """Deployed model details (served by GET /api/v1/model)."""

    model_name: str
    version: str
    classes: list[str]
    input_size: int
    metrics: dict | None = None
    deployment_status: str = "deployed"


class HealthResponse(BaseModel):
    """Readiness payload for GET /health."""

    status: str = "healthy"
    api: str = "healthy"
    database: str = "unknown"
    model: str = "unknown"
