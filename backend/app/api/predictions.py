"""POST /api/v1/predict — image classification (spec §15, §33).

Input: multipart/form-data, image=<file>
Output: standard PredictionResponse (see schemas.py).

TODO (Student 2 — Backend Engineer):
- Validate file type (jpg/png/webp only), reject others with clean 400/415.
- Reject corrupted images and oversized uploads (> settings.MAX_UPLOAD_MB).
- Sanitize the original filename (no path traversal).
- Call services.inference.predict(image_bytes) -> PredictionResponse.
- Persist via services.prediction_service.create_prediction(...).
- Map inference/DB failures to clean errors (503 etc.), no tracebacks.
"""
