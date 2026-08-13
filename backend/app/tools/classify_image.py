"""Tool 1 — classify_image (spec §17).

TODO:
- Accept image bytes (or path) + optional top_k.
- Delegate to services.inference and return the standard PredictionResponse.
- If inference fails, raise/return a structured error so the agent reports
  the failure instead of guessing (spec §18).
"""
