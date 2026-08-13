"""Prediction statistics endpoint (spec §15, §22).

TODO:
- GET /api/v1/stats -> StatsResponse:
      total_predictions, class_distribution {"damaged": n, "undamaged": m},
      avg_confidence (and optionally avg inference_ms).
"""
