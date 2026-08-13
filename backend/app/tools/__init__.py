"""Agent tool implementations (spec §17).

These five tools back the LLM agent. Each tool must return REAL data
(from the model/DB) — never fabricated results (spec §18).

Tools:
    classify_image          -> run inference on an uploaded image
    get_prediction_history  -> most recent N predictions
    get_prediction_by_id    -> single stored prediction
    get_prediction_statistics -> aggregated stats
    get_model_info          -> deployed model details
"""
