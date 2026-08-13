"""Pydantic schemas (spec §14, §15).

Standard inference output shape (keep this contract stable — frontend and
agent tools depend on it):

    {
      "predicted_class": "damaged",
      "confidence": 0.9412,
      "top_predictions": [{"class_name": "damaged", "probability": 0.9412}, ...],
      "inference_ms": 37.5,
      "model_version": "1.0.0"
    }

TODO (Student 2 — Backend Engineer):
- PredictionResponse (shape above)
- PredictionOut (DB record: id, image_name, predicted_class, confidence,
  inference_ms, model_version, created_at)
- PredictionList (items: list[PredictionOut])
- StatsResponse (total_predictions, class_distribution, avg_confidence)
- ModelInfoResponse (model name, version, classes, input size, metrics,
  deployment status)
"""

# from pydantic import BaseModel
#
# class TopPrediction(BaseModel):
#     class_name: str
#     probability: float
#
# class PredictionResponse(BaseModel):
#     predicted_class: str
#     confidence: float
#     top_predictions: list[TopPrediction]
#     inference_ms: float
#     model_version: str
