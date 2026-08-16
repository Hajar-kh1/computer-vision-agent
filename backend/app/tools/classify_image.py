"""Tool 1 — classify_image (spec §17).

Server-side implementation of the agent's classify_image tool. It runs the
deployed model over an image (given as bytes or a server-side path) and
returns the standard PredictionResponse dict.

Never raises: on any failure it returns {"error": ...} so the agent reports
the failure honestly instead of inventing a result (spec §18).
"""

from pathlib import Path

from backend.app.services.inference import InferenceError, get_inference


def classify_image(
    image_bytes: bytes | None = None,
    image_path: str | None = None,
    top_k: int = 2,
) -> dict:
    """Classify a package image and return the standard prediction dict."""
    if image_bytes is None:
        if not image_path:
            return {"error": "classify_image requires image_bytes or image_path"}
        try:
            image_bytes = Path(image_path).read_bytes()
        except OSError as exc:
            return {"error": f"cannot read image '{image_path}': {exc}"}

    try:
        return get_inference().predict(image_bytes, top_k=top_k)
    except InferenceError as exc:
        return {"error": f"inference failed: {exc}"}
