"""Model information endpoint (spec §15, §17-Tool5).

TODO:
- GET /api/v1/model -> ModelInfoResponse:
      model_name, version, classes (from labels.json), input_size,
      metrics (from reports/model_metrics.json if present), deployment status.
"""
