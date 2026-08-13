"""Agent tool registry — LLM-facing schemas + dispatcher + HTTP handlers.

The chat LLM cannot touch the model or the database directly. This file
gives it three things:

1. TOOLS           — the five tool schemas the LLM reads to decide WHAT to call
                     and with WHICH arguments (pure JSON Schema — no backend
                     needed, which is why we write them first).
2. execute_tool()  — the dispatcher that runs the matching handler for real.
3. Handlers        — one per tool; each is a thin HTTP client for a FastAPI
                     endpoint (spec §17: tools connected to FastAPI).

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
from pathlib import Path
from typing import Any, Callable

import httpx

# Base URL of the FastAPI backend (spec §29: use Docker service names in compose):
#   local dev:      http://localhost:8000
#   docker compose: http://backend:8000
#   production:     https://<api-domain>
# Overridable via env so tests can point at a test client or mock server.
BACKEND_URL = os.getenv("AGENT_BACKEND_URL", "http://localhost:8000")

# Seconds to wait for a backend response. Generous for the first (cold) model
# load in the container; the model is loaded once at startup, so steady-state
# predictions are far below this.
_REQUEST_TIMEOUT = 60.0

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
                "(Box, Box_broken, Open_package or Package), the confidence "
                "score, the top-K predictions and the inference latency. "
                "Use this whenever the user asks to classify or check an image."
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
                "total count, per-class distribution across the four classes "
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
# Endpoint mapping (docs/api.md):
#   classify_image            -> POST /api/v1/predict
#   get_prediction_history    -> GET  /api/v1/predictions?limit=N
#   get_prediction_by_id      -> GET  /api/v1/predictions/{id}
#   get_prediction_statistics -> GET  /api/v1/stats
#   get_model_info            -> GET  /api/v1/model

def _request_json(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
    """Perform an HTTP request and return the parsed JSON body.

    On a non-2xx response we re-raise as RuntimeError carrying the backend's
    own "detail" message — the backend already formats clean errors
    (spec §33), so the agent can show them verbatim instead of inventing a
    reason. RuntimeError is caught by execute_tool and serialized as
    {"error": ...}.
    """
    resp = httpx.request(method, f"{BACKEND_URL}{path}", timeout=_REQUEST_TIMEOUT, **kwargs)
    if resp.is_error:
        detail = ""
        try:
            detail = resp.json().get("detail", "")
        except Exception:
            pass
        raise RuntimeError(f"backend returned {resp.status_code}: {detail}")
    return resp.json()


def _classify_image(args: dict[str, Any]) -> dict[str, Any]:
    """POST /api/v1/predict — multipart form with the image file."""
    image_path = args.get("image_path")
    if not image_path:
        return {"error": "Missing required argument: image_path"}
    top_k = args.get("top_k")

    # multipart/form-data, exactly what the endpoint expects:
    #   image=<file>  (+ optional top_k form field; ignored by the backend
    #   until it implements top-K selection — harmless to send).
    with open(image_path, "rb") as fh:
        files = {"image": (Path(image_path).name, fh)}
        data = {"top_k": str(top_k)} if top_k else None
        return _request_json("POST", "/api/v1/predict", files=files, data=data)


def _get_prediction_history(args: dict[str, Any]) -> dict[str, Any]:
    """GET /api/v1/predictions?limit={limit} (default 5)."""
    limit = args.get("limit", 5)
    return _request_json("GET", "/api/v1/predictions", params={"limit": limit})


def _get_prediction_by_id(args: dict[str, Any]) -> dict[str, Any]:
    """GET /api/v1/predictions/{prediction_id}."""
    prediction_id = args.get("prediction_id")
    if prediction_id is None:
        return {"error": "Missing required argument: prediction_id"}
    return _request_json("GET", f"/api/v1/predictions/{prediction_id}")


def _get_prediction_statistics(args: dict[str, Any]) -> dict[str, Any]:
    """GET /api/v1/stats."""
    return _request_json("GET", "/api/v1/stats")


def _get_model_info(args: dict[str, Any]) -> dict[str, Any]:
    """GET /api/v1/model."""
    return _request_json("GET", "/api/v1/model")


_HANDLERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "classify_image": _classify_image,
    "get_prediction_history": _get_prediction_history,
    "get_prediction_by_id": _get_prediction_by_id,
    "get_prediction_statistics": _get_prediction_statistics,
    "get_model_info": _get_model_info,
}

__all__ = ["TOOLS", "execute_tool", "BACKEND_URL", "_HANDLERS"]
