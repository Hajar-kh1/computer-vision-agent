"""Tool-calling agent loop (spec §17, §18).

Flow per turn:
    user message
      -> LLM (with TOOLS from tools.py + SYSTEM_PROMPT from prompts.py)
      -> if tool_calls: execute each via tools.execute_tool, feed results
         back to the LLM, loop (max MAX_TOOL_ROUNDS)
      -> else: return the final answer

Grounding rules (spec §18), enforced here:
  - execute_tool returns {"error": ...} on any failure (never fabricates).
  - Tool results are handed back to the LLM verbatim, so every number the
    model quotes came from a real tool call or a real backend response.
  - If the LLM API itself fails, we say so instead of inventing an answer.

Run it:
    uv run python -m agent.agent "Show me the latest 3 predictions"
    uv run python -m agent.agent "What model is deployed?" --model llama-3.3-70b-versatile
"""

import argparse
import json
import os
from typing import Any

# openai SDK talks to any OpenAI-compatible endpoint (Groq, DeepSeek, ...).
from openai import OpenAI

from agent.prompts import SYSTEM_PROMPT, build_system_prompt
from agent.tools import TOOLS, execute_tool

# --- configuration ---
# Read from env (same names as .env.example). The backend URL used by the
# tools lives in tools.py (AGENT_BACKEND_URL).
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# LangFuse LLM observability (tracing, tokens, latency, cost). Optional:
# when both keys are set, every LLM call in the agent loop is traced.
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

MAX_TOOL_ROUNDS = 5  # hard cap: an agent that never stops calling tools is a bug


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client for the configured provider.

    When LangFuse is configured (LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY),
    the client is wrapped with LangFuse's OpenAI integration, so each
    chat.completions.create call is traced automatically: input/output,
    tool calls, token counts, latency and cost.
    """
    if not LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is not set. Add it to .env or export it "
            "(e.g. python -m agent.agent ...)."
        )
    if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
        from langfuse.openai import OpenAI as LangfuseOpenAI

        return LangfuseOpenAI(
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
        )
    return OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)


def run_agent(user_message: str, *, system_prompt: str | None = None,
              model: str | None = None, max_tool_rounds: int = MAX_TOOL_ROUNDS) -> str:
    """Run the tool-calling loop and return the final assistant answer."""
    client = get_client()
    model = model or LLM_MODEL
    system = system_prompt or build_system_prompt()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]

    for _ in range(max_tool_rounds):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,          # the five schemas from tools.py
            tool_choice="auto",   # let the model decide when to call
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or ""

        # one or more tool calls: execute them, append results
        # Each tool result is attached to the specific tool_call_id so the
        # model can match arguments to results (OpenAI tool-calling format).
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {"id": tc.id, "type": "function", "function": {
                    "name": tc.function.name, "arguments": tc.function.arguments}
                 } for tc in message.tool_calls
            ],
        })
        for tc in message.tool_calls:
            # arguments arrive as a JSON string — parse, then run the tool.
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = execute_tool(tc.function.name, args)  # always a JSON string
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # Only reached if the model kept calling tools for max_tool_rounds.
    return "I could not finish answering within the allowed number of tool calls."


def main() -> None:
    parser = argparse.ArgumentParser(description="Package Damage agent CLI")
    parser.add_argument("message", help="What to ask the agent")
    parser.add_argument("--model", default=None, help="Override LLM_MODEL")
    parser.add_argument("--max-rounds", type=int, default=MAX_TOOL_ROUNDS)
    args = parser.parse_args()

    try:
        answer = run_agent(args.message, model=args.model, max_tool_rounds=args.max_rounds)
    except Exception as exc:  # noqa: BLE001 — CLI must not traceback on user
        # Spec §18: report the failure, never fabricate an answer.
        print(f"Agent failed: {exc}")
        return
    print(answer)


if __name__ == "__main__":
    main()
