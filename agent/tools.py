"""Tool registry — JSON-schema tool definitions for the LLM (spec §17).

The five required tools, each with an OpenAI-style function schema:

    1. classify_image          — image bytes/path -> prediction
    2. get_prediction_history  — limit -> recent predictions
    3. get_prediction_by_id    — prediction_id -> record
    4. get_prediction_statistics — -> totals + distribution
    5. get_model_info          — -> deployed model details

TODO (Student 3):
- Define TOOLS: list[dict] with name, description, parameters (JSON Schema).
- Implement execute_tool(name, arguments) -> str that calls the backend
  services (or the running FastAPI HTTP endpoints via httpx).
- The tool functions themselves live in backend/app/tools/ — import/reuse them
  so the agent and the API never drift apart.
"""
