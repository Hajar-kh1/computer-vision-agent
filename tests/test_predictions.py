"""Prediction persistence + history tests (spec §35: test_database_insert, test_prediction_history).

TODO:
- test_database_insert: after POST /api/v1/predict, a row exists in the DB
  with image_name, predicted_class, confidence, inference_ms, model_version.
- test_prediction_history: GET /api/v1/predictions returns the stored records
  (newest first), and GET /api/v1/predictions/{id} returns the single record.
- test_missing_prediction: GET /api/v1/predictions/999999 -> 404 clean error.
- test_stats: GET /api/v1/stats returns total_predictions + class_distribution.
"""
