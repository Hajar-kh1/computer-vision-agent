"""Open WebUI Tool — Package Damage agent tools (spec §17).

HOW TO INSTALL
  1. Open WebUI -> Workspace -> Tools -> (create new) -> paste this file
     -> Save. This Open WebUI version requires a class named ``Tools``;
     every public method on it becomes a tool automatically.
  2. Attach it to a model: Admin Panel -> Models -> (your model) -> Tools ->
     enable "package_damage_tools". Use a model with tool calling support
     (e.g. llama-3.3-70b-versatile on Groq).
  3. Try in a NEW chat: "Show me the latest three predictions."

WHY STDLIB ONLY
  Open WebUI's tool runner blocks third-party imports (only stdlib is
  safe), so every HTTP call uses urllib — including the multipart upload.

WHERE IT CALLS
  BACKEND_URL must reach the FastAPI backend:
    - docker compose: http://backend:8000  (Docker service name, spec §29)
    - production:     your public API domain (edit BACKEND_URL)
"""

import json
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
import uuid

BACKEND_URL = "http://backend:8000"  # Docker service name; edit for production
TIMEOUT = 30  # seconds — generous for the first (cold) model load

# Open WebUI stores uploaded chat files here (id -> path in the `file` table).
WEBUI_DB = "/app/backend/data/webui.db"


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


def _resolve_attached_image(files: list | None) -> str:
    """Return an on-disk path for the first image in a chat attachment list.

    Attached-file objects carry an id (uuid), name and type; the actual file
    path is stored in Open WebUI's SQLite DB (file table, path column).
    """
    if not files:
        return ""
    for item in files:
        if not isinstance(item, dict):
            continue
        # Some builds include the local path directly.
        path = item.get("path") or item.get("url") or ""
        if path and not path.startswith(("http://", "https://", "data:")):
            return path
    # Fall back to resolving the first file id against Open WebUI's DB.
    file_id = files[0].get("id") if isinstance(files[0], dict) else None
    if file_id:
        try:
            con = sqlite3.connect(WEBUI_DB)
            try:
                row = con.execute(
                    "SELECT path FROM file WHERE id = ?", (str(file_id),)
                ).fetchone()
            finally:
                con.close()
            if row and row[0]:
                return row[0]
        except Exception:
            pass
    return ""


class Tools:
    """Package damage detection tools — connected to the FastAPI backend."""

    async def classify_image(self, image_path: str = "", top_k: int = 2,
                             __files__: list | None = None) -> str:
        """Run an image of a shipping package through the deployed computer vision model and return the predicted class (Box, Box_broken, Open_package or Package), the confidence score, the top-K predictions and the inference latency. Provide the image by attaching it to the chat (recommended) or by giving its server-side path.

        :param image_path: Optional path to the image file on the server; leave empty when the image is attached to the chat.
        :param top_k: How many top predictions to return (default 2).
        :return: JSON with predicted_class, confidence, top_predictions, inference_ms, model_version.
        """
        path = ""
        if __files__:
            # The user attached an image — that file is ground truth; ignore
            # any path the model may have guessed (it often invents one).
            path = _resolve_attached_image(__files__)
        if not path:
            path = image_path
        if not path:
            return json.dumps({"error": "classify_image needs an image — attach one to the chat or provide image_path"})
        try:
            with open(path, "rb") as fh:
                content = fh.read()
            filename = path.rsplit("/", 1)[-1] or "image.jpg"
        except Exception as exc:
            return json.dumps({"error": f"cannot read image '{path}': {exc}"})

        # Build multipart/form-data by hand — stdlib urllib has no multipart API.
        boundary = "----package-damage-" + uuid.uuid4().hex
        crlf = "\r\n"
        pre = (
            f"--{boundary}{crlf}"
            f'Content-Disposition: form-data; name="image"; filename="{filename}"{crlf}'
            f"Content-Type: application/octet-stream{crlf}{crlf}"
        ).encode("utf-8")
        post = f"{crlf}--{boundary}--{crlf}".encode("utf-8")

        data = _request(
            "POST", "/api/v1/predict",
            data=pre + content + post,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        return json.dumps(data, ensure_ascii=False)

    async def get_prediction_history(self, limit: int = 5) -> str:
        """Retrieve the most recent N predictions from the PostgreSQL database. Use this when the user asks about previous predictions or 'latest' results.

        :param limit: How many recent predictions to return (default 5).
        :return: JSON with items (newest first) and total.
        """
        data = _request("GET", "/api/v1/predictions", params={"limit": limit})
        return json.dumps(data, ensure_ascii=False)

    async def get_prediction_by_id(self, prediction_id: int) -> str:
        """Retrieve a single stored prediction record by its numeric ID. Use this when the user references a specific prediction ID.

        :param prediction_id: The numeric ID of the prediction record.
        :return: JSON with the prediction fields, or an error message.
        """
        data = _request("GET", f"/api/v1/predictions/{prediction_id}")
        return json.dumps(data, ensure_ascii=False)

    async def get_prediction_statistics(self, include_latency: bool) -> str:
        """Retrieve aggregated statistics over all stored predictions: total count, per-class distribution across the four classes and average confidence. Use this for 'how many', 'which class is most common' or 'average confidence' questions.

        :param include_latency: Set to false to omit the average inference latency from the response.
        :return: JSON with total_predictions, class_distribution, avg_confidence.
        """
        data = _request("GET", "/api/v1/stats")
        if not include_latency:
            data.pop("avg_inference_ms", None)
        return json.dumps(data, ensure_ascii=False)

    async def get_model_info(self, include_metrics: bool) -> str:
        """Retrieve information about the currently deployed model: model name, version, class list, input size, metrics and deployment status. Use this whenever the user asks what model is deployed.

        :param include_metrics: Set to false to omit the training metrics from the response.
        :return: JSON with model_name, version, classes, input_size, metrics.
        """
        data = _request("GET", "/api/v1/model")
        if not include_metrics:
            data.pop("metrics", None)
        return json.dumps(data, ensure_ascii=False)
