"""Prediction history endpoints (spec §15).

TODO:
- GET /api/v1/predictions?limit=20 -> list of stored predictions (newest first).
- GET /api/v1/predictions/{prediction_id} -> single prediction;
  404 with a clean message if the record does not exist.
"""
