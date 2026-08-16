# API Reference (spec §14, §15)

Base URL: `http://localhost:8000` (local) — Swagger UI at `/docs`.

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness: `{"status": "healthy"}` (+ api/database/model readiness) |
| GET | `/api/v1/model` | Deployed model info |
| POST | `/api/v1/predict` | Classify an image (multipart `image=<file>`) |
| GET | `/api/v1/predictions?limit=20` | Prediction history (newest first) |
| GET | `/api/v1/predictions/{prediction_id}` | Single stored prediction |
| GET | `/api/v1/stats` | total_predictions, class_distribution, avg_confidence |
| POST | `/api/v1/chat` | Agent chat: `{"message": "..."}` → `{"reply": "..."}` (same tools as Open WebUI) |

## Standard prediction response (keep this contract stable)
```json
{
  "predicted_class": "damaged",
  "confidence": 0.9412,
  "top_predictions": [
    {"class_name": "damaged", "probability": 0.9412},
    {"class_name": "undamaged", "probability": 0.0431}
  ],
  "inference_ms": 37.5,
  "model_version": "1.0.0"
}
```

## Errors (spec §33 — clean errors, no tracebacks)
- 400/415 invalid file type (e.g. `.txt` — the instructor's failure test, §41)
- 400 corrupted / unreadable image
- 413 oversized upload (> MAX_UPLOAD_MB)
- 404 missing prediction record
- 503 model not loaded / inference failure
- 503 database failure
