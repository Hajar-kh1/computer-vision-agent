"""Server-side agent tool implementations (spec §17).

These five tools back the LLM agent. Each returns REAL data from the model
or the database — never fabricated results (spec §18). On any failure the
tools return {"error": ...} so the agent reports the problem honestly.

The LLM-facing client (agent/tools.py) calls the FastAPI endpoints over
HTTP; these server-side functions are the same operations implemented
directly against the services, for internal/Open WebUI use.
"""

from backend.app.tools.classify_image import classify_image
from backend.app.tools.get_prediction_by_id import get_prediction_by_id
from backend.app.tools.model_info import get_model_info
from backend.app.tools.prediction_history import get_prediction_history
from backend.app.tools.prediction_stats import get_prediction_statistics

__all__ = [
    "classify_image",
    "get_prediction_history",
    "get_prediction_by_id",
    "get_prediction_statistics",
    "get_model_info",
]
