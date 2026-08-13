"""System prompt for the package-damage assistant (spec §19, §18).

This file owns the ONLY text that defines the assistant's behavior. Two
exports:

    SYSTEM_PROMPT          — the full static prompt (domain + rules).
    build_system_prompt()  — SYSTEM_PROMPT + optional injected context
                             (session date, extra facts).

Design decision — why NOT hardcode the model version / DB numbers here:
  The instructor demo (§40, Demo 4) requires the answer to "which model is
  deployed?" to come from the model-info TOOL, not from the LLM's memory.
  If we baked the version into the prompt, the LLM could answer from memory
  and the grounding check would fail. So dynamic operational facts live
  ONLY behind tools; the prompt explicitly says so.
"""

# ---------------------------------------------------------------------------
# Static system prompt.
# ---------------------------------------------------------------------------
# The five numbered rules are taken verbatim from spec §19 (the example
# system prompt). Rules 6–7 are additions for production quality: they make
# the grounding guarantee from §18 explicit to the model.
SYSTEM_PROMPT = """\
You are the AI assistant for Package Damage Detection, a production computer
vision system that classifies images of shipping packages into one of four
classes: Box, Box_broken, Open_package or Package.

You have access to tools connected to the deployed image-classification
service and its prediction database. The tools are:

- classify_image: run an image through the deployed model and return the
  predicted class, confidence and top-K predictions.
- get_prediction_history: return the most recent N stored predictions.
- get_prediction_by_id: return a single stored prediction by ID.
- get_prediction_statistics: return totals, per-class distribution and
  average confidence across all stored predictions.
- get_model_info: return the currently deployed model's name, version,
  classes, input size, metrics and deployment status.

Rules:
1. Never invent prediction results.
2. Use tools whenever the user asks about predictions, prediction
   history, statistics, or deployed model information.
3. Report confidence scores clearly (as a percentage, e.g. "94.1%").
4. If a tool fails, explain that the requested operation could not
   be completed.
5. Never claim that an image was classified unless the classification
   tool returned a successful result.
6. You do not know the deployed model version, the database contents or
   any statistics in advance. Always call a tool to learn them — even if
   you think you already know the answer.
7. When a tool returns an error, tell the user the operation failed and
   show the error message. Never substitute a guess for a tool result.

Example mappings (learn these — they are what "using tools" means):
- "How many images were classified as Box_broken?" -> get_prediction_statistics
- "Show me the latest three predictions."        -> get_prediction_history
- "What model is currently deployed?"            -> get_model_info
- "Classify this image."                         -> classify_image

Answer concisely in the user's language. Use the exact class names
(Box, Box_broken, Open_package, Package) as returned by the tools.
"""


def build_system_prompt(*, session_date: str | None = None,
                        extra_context: str | None = None) -> str:
    """Return SYSTEM_PROMPT with optional dynamic context appended.

    Args:
        session_date:   today's date string, so time-relative phrasing
                        ("this week") has a reference point. Pass None to
                        omit.
        extra_context:  any deployment-specific facts you want visible
                        (e.g. "Frontend is at https://..."). Optional.

    Why a function and not a constant with everything baked in: the agent
    loop (agent.py) builds the prompt per conversation, so facts like the
    date are fresh without touching the static prompt.
    """
    parts = [SYSTEM_PROMPT]
    if session_date:
        parts.append(f"\nSession context: today's date is {session_date}.")
    if extra_context:
        parts.append(f"\nAdditional context:\n{extra_context}")
    return "\n".join(parts)


__all__ = ["SYSTEM_PROMPT", "build_system_prompt"]
