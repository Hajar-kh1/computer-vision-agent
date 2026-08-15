"""POST /api/v1/chat — agent chat for the frontend popup (spec §17, §18).

Runs the same tool-calling agent loop that Open WebUI uses (agent/agent.py)
and returns the final answer. The agent's tools call back into this backend
over HTTP (localhost:8000 in dev, same container in compose), so every
number it quotes comes from the real model/DB — never invented.
"""

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# The agent module reads LLM_* from the process env at import time — make
# sure the values are visible even when they only exist in .env (settings).
from backend.app.config import settings

os.environ.setdefault("LLM_API_KEY", settings.LLM_API_KEY)
os.environ.setdefault("LLM_BASE_URL", settings.LLM_BASE_URL)
os.environ.setdefault("LLM_MODEL", settings.LLM_MODEL)

from agent.agent import run_agent  # noqa: E402  (needs env set above)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    system_prompt: str | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """Run the agent on one message and return its final answer."""
    message = (req.message or "").strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message must not be empty.")

    if not os.getenv("LLM_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="Agent chat is not configured: LLM_API_KEY is missing.",
        )

    try:
        reply = run_agent(message, system_prompt=req.system_prompt)
    except Exception as exc:  # noqa: BLE001 — clean error, no traceback (§33)
        raise HTTPException(
            status_code=503,
            detail=f"Agent failed: {exc}",
        ) from exc

    return ChatResponse(reply=reply)
