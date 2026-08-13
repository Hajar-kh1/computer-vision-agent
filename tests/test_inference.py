"""Inference tests (spec §35: test_model_loaded, test_valid_prediction, test_invalid_image).

TODO:
- test_model_loaded: inference service holds a model / labels.json loads.
- test_valid_prediction: POST /api/v1/predict with a valid JPEG returns 200
  and the standard PredictionResponse shape (predicted_class, confidence,
  top_predictions, inference_ms, model_version).
- test_invalid_image: POST /api/v1/predict with a .txt file (spec §41 failure
  test) returns a clean 4xx validation error — no traceback.
"""
