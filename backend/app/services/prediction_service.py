"""Prediction persistence + query service (spec §16).

TODO (Student 2 — Backend Engineer):
- create_prediction(db, data) -> Prediction (insert + commit + refresh).
- list_predictions(db, limit) -> list[Prediction] (newest first).
- get_prediction(db, prediction_id) -> Prediction | None.
- get_stats(db) -> total, class_distribution, avg_confidence.
"""
