"""Tool-calling agent loop (spec §17, §18).

TODO (Student 3 — Agentic AI Engineer):
- Configure the LLM client from env: LLM_BASE_URL, LLM_API_KEY, LLM_MODEL
  (OpenAI-compatible chat completions API).
- Load the tool definitions (see tools.py) and the system prompt (prompts.py).
- Implement the loop: user message -> LLM -> tool_calls -> execute tool ->
  return tool result -> LLM final answer. Stop when no more tool calls.
- Grounding rules (spec §18):
    * never invent prediction results / history / stats
    * if a tool fails, report the failure — do not fabricate an answer
- Keep this runnable standalone for testing:
      uv run python -m agent.agent "Show me the latest 3 predictions"

Suggested signature:
    def run_agent(user_message: str, max_tool_rounds: int = 5) -> str: ...
"""
