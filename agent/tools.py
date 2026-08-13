"""Agent tool registry — LLM-facing schemas + dispatcher (spec §17, §18).

The chat LLM cannot touch the model or the database directly. This file
gives it two things:

1. TOOLS           — the five tool schemas the LLM reads to decide WHAT to call
                     and with WHICH arguments (pure JSON Schema — no backend
                     needed, which is why we write them first).
2. execute_tool()  — the dispatcher that runs the matching handler for real.

Design choice — why HTTP instead of importing backend functions:
  The same tools must also work from Open WebUI, whose Functions run inside
  the Open WebUI container and CANNOT import our backend code. So the
  handlers here call the FastAPI endpoints over HTTP, exactly like the
  frontend does. The backend's own logic lives in backend/app/services/ and
  backend/app/tools/; this module is just a thin client for the LLM.

Contract: response shapes below match docs/api.md and backend/app/schemas.py.
"""

import json
import os
from typing import Any, Callable

# Base URL of the FastAPI backend (spec §29: use Docker service names in compose):
#   local dev:      http://localhost:8000
#   docker compose: http://backend:8000
#   production:     https://<api-domain>
# Overridable via env so tests can point at a test client.
BACKEND_URL = os.getenv("AGENT_BACKEND_URL", "http://localhost:8000")

# ---------------------------------------------------------------------------
# 1. Tool schemas — the ONLY thing the LLM sees.
# ---------------------------------------------------------------------------
# Each entry is an OpenAI-style function schema:
#   - "description" is what the LLM uses to pick the right tool → make it
#     specific about WHEN to use it and WHAT it returns.
#   - "parameters" is a JSON Schema object; "required" lists the args the
#     tool cannot run without. Keep optional args out of "required" so the
#     LLM is not forced to guess values.
TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "classify_image",
            "description": (
                "Run an image of a shipping package through the deployed "
                "computer vision model and return the predicted class "
                "(damaged or undamaged), the confidence score, the top-K "
                "predictions and the inference latency. Use this whenever "
                "the user asks to classify or check an image."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": (
                            "Path to the image file on the server "
                            "(e.g. data/uploads/<file>.jpg). The frontend "
                            "saves uploaded images to this folder."
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 5,
                        "description": "How many top predictions to return (default 2).",
                    },
                },
                "required": ["image_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_prediction_history",
            "description": (
                "Retrieve the most recent N predictions from the PostgreSQL "
                "database. Use this when the user asks about previous "
                "predictions or 'latest' results."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "description": "How many recent predictions to return (default 5).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_prediction_by_id",
            "description": (
                "Retrieve a single stored prediction record by its numeric "
                "ID. Use this when the user references a specific prediction ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "prediction_id": {
                        "type": "integer",
                        "description": "The numeric ID of the prediction record.",
                    },
                },
                "required": ["prediction_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_prediction_statistics",
            "description": (
                "Retrieve aggregated statistics over all stored predictions: "
                "total count, per-class distribution (damaged / undamaged) "
                "and average confidence. Use this for 'how many', 'which "
                "class is most common' or 'average confidence' questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_model_info",
            "description": (
                "Retrieve information about the currently deployed model: "
                "model name, version, class list, input size, metrics and "
                "deployment status. Use this whenever the user asks what "
                "model is deployed."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]

# ---------------------------------------------------------------------------
# 2. Dispatcher — routes an LLM tool call to the right handler.
# ---------------------------------------------------------------------------

def execute_tool(name: str, arguments: dict[str, Any] | None = None) -> str:
    """Execute tool `name` with `arguments` and return a JSON string.

    Why a string: chat APIs hand tool results back to the LLM as text, so we
    serialize once here and every handler can simply return dicts.

    Failure handling (spec §18): any error is wrapped into {"error": ...}
    instead of raising — the agent must report the failure to the user,
    never invent a result. Returning an error JSON is what lets the LLM
    phrase that honestly.
    """
    arguments = arguments or {}
    handler = _HANDLERS.get(name)
    if handler is None:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        result = handler(arguments)
    except Exception as exc:  # noqa: BLE001 — must never crash the agent loop
        return json.dumps({"error": f"Tool '{name}' failed: {exc}"})

    return json.dumps(result, ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# 3. Handlers — one per tool, each maps 1:1 to a backend endpoint.
# ---------------------------------------------------------------------------
# STEP 6 TODO: replace each `raise NotImplementedError` with a real httpx call
# to BACKEND_URL + the endpoint listed in the docstring. The schemas above are
# already final, so this step is purely mechanical:
#
#   def _classify_image(args: dict[str, Any]) -> dict[str, Any]:
#       files = {"image": open(args["image_path"], "rb")}
#       resp = httpx.post(f"{BACKEND_URL}/api/v1/predict", files=files, timeout=30)
#       resp.raise_for_status()
#       return resp.json()
#
# Endpoint mapping (docs/api.md):
#   classify_image            -> POST /api/v1/predict
#   get_prediction_history    -> GET  /api/v1/predictions?limit=N
#   get_prediction_by_id      -> GET  /api/v1/predictions/{id}
#   get_prediction_statistics -> GET  /api/v1/stats
#   get_model_info            -> GET  /api/v1/model

def _classify_image(args: dict[str, Any]) -> dict[str, Any]:
    """POST /api/v1/predict (multipart form: image=<file>)."""
    raise NotImplementedError("Step 6: httpx call to POST /api/v1/predict")


def _get_prediction_history(args: dict[str, Any]) -> dict[str, Any]:
    """GET /api/v1/predictions?limit={limit} (default 5)."""
    raise NotImplementedError("Step 6: httpx call to GET /api/v1/predictions")


def _get_prediction_by_id(args: dict[str, Any]) -> dict[str, Any]:
    """GET /api/v1/predictions/{prediction_id}."""
    raise NotImplementedError("Step 6: httpx call to GET /api/v1/predictions/{id}")


def _get_prediction_statistics(args: dict[str, Any]) -> dict[str, Any]:
    """GET /api/v1/stats."""
    raise NotImplementedError("Step 6: httpx call to GET /api/v1/stats")


def _get_model_info(args: dict[str, Any]) -> dict[str, Any]:
    """GET /api/v1/model."""
    raise NotImplementedError("Step 6: httpx call to GET /api/v1/model")


_HANDLERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "classify_image": _classify_image,
    "get_prediction_history": _get_prediction_history,
    "get_prediction_by_id": _get_prediction_by_id,
    "get_prediction_statistics": _get_prediction_statistics,
    "get_model_info": _get_model_info,
}

__all__ = ["TOOLS", "execute_tool", "BACKEND_URL", "_HANDLERS"]
