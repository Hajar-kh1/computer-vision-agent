"""Open WebUI Function — Package Damage agent tools (spec §17).

HOW TO INSTALL
  1. Open WebUI -> Workspace -> Functions -> (create new) -> paste this file
     -> Save -> enable it.
  2. Attach it to a model: Admin Panel -> Models -> (your model) -> Tools ->
     enable "package_damage_tools". Use a model with tool calling support
     (e.g. llama-3.3-70b-versatile on Groq).
  3. Try in chat: "Show me the latest three predictions."

WHY STDLIB ONLY
  Open WebUI's function runner blocks third-party imports (only stdlib is
  safe), so every HTTP call uses urllib — including the multipart upload.

WHERE IT CALLS
  BACKEND_URL must reach the FastAPI backend:
    - docker compose: http://backend:8000  (Docker service name, spec §29)
    - production:     your public API domain (edit BACKEND_URL)
"""

import json
import urllib.error
import urllib.parse
import urllib.request
import uuid

BACKEND_URL = "http://backend:8000"  # Docker service name; edit for production
TIMEOUT = 30  # seconds — generous for the first (cold) model load


# ---------------------------------------------------------------------------
# Tiny stdlib HTTP helper — returns parsed JSON or {"error": ...}
# ---------------------------------------------------------------------------

def _request(method: str, path: str, *, params: dict | None = None,
             data: bytes | None = None, headers: dict | None = None) -> dict:
    """GET/POST to the backend; never raises — always returns a dict.

    On any failure the dict contains "error" so the LLM can report the
    problem honestly (spec §18) instead of inventing a result.
    """
    url = BACKEND_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        # The backend already formats clean errors (spec §33) — surface them.
        detail = ""
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("detail", "")
        except Exception:
            pass
        return {"error": f"backend returned {exc.code}: {detail}"}
    except Exception as exc:
        return {"error": f"could not reach backend at {BACKEND_URL}: {exc}"}


# ---------------------------------------------------------------------------
# Tool 1 — classify_image (spec §17)
# ---------------------------------------------------------------------------

def classify_image(image_path: str) -> str:
    """Run an image of a shipping package through the deployed model.

    The image must be readable by the Open WebUI container (a path on the
    server, e.g. an uploaded attachment stored under /app/backend/data/...).
    Returns the predicted class, confidence, top-K and latency as JSON.
    """
    try:
        with open(image_path, "rb") as fh:
            content = fh.read()
        filename = image_path.rsplit("/", 1)[-1] or "image.jpg"
    except Exception as exc:
        return json.dumps({"error": f"cannot read image '{image_path}': {exc}"})

    # Build multipart/form-data by hand — stdlib urllib has no multipart API.
    boundary = "----package-damage-" + uuid.uuid4().hex
    pre = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    post = f"\r\n--{boundary}--\r\n".encode("utf-8")

    data = _request(
        "POST", "/api/v1/predict",
        data=pre + content + post,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    return json.dumps(data, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 2 — get_prediction_history (spec §17)
# ---------------------------------------------------------------------------

def get_prediction_history(limit: int = 5) -> str:
    """Retrieve the most recent N predictions from PostgreSQL."""
    data = _request("GET", "/api/v1/predictions", params={"limit": limit})
    return json.dumps(data, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 3 — get_prediction_by_id (spec §17)
# ---------------------------------------------------------------------------

def get_prediction_by_id(prediction_id: int) -> str:
    """Retrieve a single stored prediction record by its numeric ID."""
    data = _request("GET", f"/api/v1/predictions/{prediction_id}")
    return json.dumps(data, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 4 — get_prediction_statistics (spec §17)
# ---------------------------------------------------------------------------

def get_prediction_statistics() -> str:
    """Retrieve aggregated statistics: totals, per-class distribution, avg confidence."""
    data = _request("GET", "/api/v1/stats")
    return json.dumps(data, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool 5 — get_model_info (spec §17)
# ---------------------------------------------------------------------------

def get_model_info() -> str:
    """Retrieve information about the currently deployed model."""
    data = _request("GET", "/api/v1/model")
    return json.dumps(data, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Tool registry — the schemas Open WebUI shows to the LLM.
# Names and descriptions mirror agent/tools.py so both sides stay consistent.
# ---------------------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "classify_image",
            "description": (
                "Run an image of a shipping package through the deployed "
                "computer vision model and return the predicted class "
                "(Box, Box_broken, Open_package or Package), the confidence "
                "score, the top-K predictions and the inference latency."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": (
                            "Path to the image file on the server "
                            "(e.g. an uploaded attachment path)."
                        ),
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
                "database. Use this when the user asks about previous or "
                "'latest' predictions."
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
            "parameters": {"type": "object", "properties": {}},
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
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
