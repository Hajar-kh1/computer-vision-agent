"""Agent tests (spec §35 recommended: test_agent_tool_call; §18 grounding).

These tests run OFFLINE — no LLM API key, no backend, no network. Two
techniques make that possible:

  1. get_client() is monkeypatched to return a FakeClient whose
     chat.completions.create() returns scripted responses. This lets us test
     the LOOP logic (does it call tools? does it feed results back?) without
     paying for tokens.
  2. Where a test must exercise the real dispatcher, it uses tools that fail
     on missing args (no HTTP needed). Everything else monkeypatches
     agent.agent.execute_tool so tool calls never touch the network.

The schema tests (test_tool_schemas_*) are the cheapest and most valuable:
they pin the contract from spec §17, so if anyone edits agent/tools.py and
breaks the tool names/params, the suite catches it immediately.
"""

import json
from types import SimpleNamespace

import pytest

from agent.agent import run_agent
from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOLS, _HANDLERS

# The five required tools, exactly as named in spec §17.
REQUIRED_TOOLS = [
    "classify_image",
    "get_prediction_history",
    "get_prediction_by_id",
    "get_prediction_statistics",
    "get_model_info",
]


# ---------------------------------------------------------------------------
# Fakes — a scripted OpenAI client
# ---------------------------------------------------------------------------

def _msg(content: str | None, tool_calls=None) -> SimpleNamespace:
    """Build a fake chat completion message.

    tool_calls: list of (name, arguments_json) tuples, or None for a
    plain text reply.
    """
    calls = None
    if tool_calls:
        calls = [
            SimpleNamespace(
                id=f"call_{i}",
                function=SimpleNamespace(name=name, arguments=args_json),
            )
            for i, (name, args_json) in enumerate(tool_calls)
        ]
    return SimpleNamespace(content=content, tool_calls=calls)


class FakeCompletions:
    """Returns scripted responses in order, records the payloads it saw."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.seen_payloads = []  # every kwargs passed to create()

    def create(self, **kwargs):
        self.seen_payloads.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=self.responses.pop(0))])


class FakeClient:
    def __init__(self, responses):
        self.chat = SimpleNamespace(completions=FakeCompletions(responses))


@pytest.fixture()
def fake_client(monkeypatch):
    """Factory: install a FakeClient as the agent's LLM client.

    Usage: client = fake_client([response1, response2, ...])
    Returns the FakeClient so tests can inspect seen_payloads.
    """
    def _install(responses):
        client = FakeClient(responses)
        monkeypatch.setattr("agent.agent.get_client", lambda: client)
        return client

    return _install


@pytest.fixture()
def stub_execute_tool(monkeypatch):
    """Replace the real HTTP tool runner with a scriptable stub."""
    calls = []

    def stub(name, arguments):
        calls.append((name, arguments))
        if name == "get_model_info":
            return json.dumps({"model_name": "resnet18", "version": "1.0.0"})
        if name == "get_prediction_statistics":
            return json.dumps({"total_predictions": 4})
        return json.dumps({"error": f"tool '{name}' not stubbed"})

    monkeypatch.setattr("agent.agent.execute_tool", stub)
    return calls


# ---------------------------------------------------------------------------
# 1. Tool schemas (spec §17)
# ---------------------------------------------------------------------------

def test_tool_schemas_complete():
    """All five required tools must be defined."""
    names = [t["function"]["name"] for t in TOOLS]
    assert sorted(names) == sorted(REQUIRED_TOOLS)


def test_tool_schemas_wellformed():
    """Every schema must be an OpenAI function schema with valid params."""
    for tool in TOOLS:
        fn = tool["function"]
        assert tool["type"] == "function"
        assert fn["name"]
        assert fn["description"]
        assert fn["parameters"]["type"] == "object"
        # every required arg must actually be declared
        for req in fn["parameters"].get("required", []):
            assert req in fn["parameters"].get("properties", {})


def test_tool_schemas_mapped_to_handlers():
    """Every tool name must have a handler registered in the dispatcher."""
    for tool in TOOLS:
        assert tool["function"]["name"] in _HANDLERS


# ---------------------------------------------------------------------------
# 2. Grounding (spec §18)
# ---------------------------------------------------------------------------

def test_system_prompt_grounding_rules():
    """The §19 rules must be present so the model never invents data."""
    assert "Never invent prediction results" in SYSTEM_PROMPT
    assert "If a tool fails" in SYSTEM_PROMPT
    assert "Never claim that an image was classified" in SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# 3. Real dispatcher (no HTTP: only paths that fail before the network)
# ---------------------------------------------------------------------------

def test_dispatcher_unknown_tool():
    from agent.tools import execute_tool as real_execute

    result = json.loads(real_execute("does_not_exist"))
    assert "error" in result


def test_dispatcher_missing_required_arg():
    from agent.tools import execute_tool as real_execute

    result = json.loads(real_execute("classify_image", {}))
    assert "error" in result
    assert "image_path" in result["error"]


# ---------------------------------------------------------------------------
# 4. Agent loop (spec §17-18)
# ---------------------------------------------------------------------------

def test_run_agent_plain_reply(fake_client):
    """No tool calls -> the model's answer is returned as-is."""
    fake_client([_msg("Hello, I can help with package damage.")])
    answer = run_agent("hello")
    assert answer == "Hello, I can help with package damage."


def test_run_agent_calls_tool_and_returns_final(fake_client, stub_execute_tool):
    """Tool-call round -> execute_tool runs -> final answer returned."""
    # Round 1: model asks for model info. Round 2: model answers.
    client = fake_client([
        _msg(None, tool_calls=[("get_model_info", "{}")]),
        _msg("The deployed model is resnet18 v1.0.0."),
    ])
    answer = run_agent("Which model is deployed?")

    assert answer == "The deployed model is resnet18 v1.0.0."
    # the tool must have been executed with the model-provided arguments
    assert stub_execute_tool == [("get_model_info", {})]
    # and the loop must have made exactly two LLM calls
    assert len(client.chat.completions.seen_payloads) == 2


def test_run_agent_feeds_tool_result_to_llm(fake_client, stub_execute_tool):
    """The tool result JSON must be appended as a role=tool message."""
    client = fake_client([
        _msg(None, tool_calls=[("get_model_info", "{}")]),
        _msg("done."),
    ])
    run_agent("Which model is deployed?")

    second_call_messages = client.chat.completions.seen_payloads[1]["messages"]
    tool_msgs = [m for m in second_call_messages if m["role"] == "tool"]
    assert len(tool_msgs) == 1
    assert "model_name" in tool_msgs[0]["content"]
    # the assistant's tool_calls block must be in the history too
    assert any(m["role"] == "assistant" and m.get("tool_calls") for m in second_call_messages)


def test_run_agent_reports_tool_failure(fake_client, monkeypatch):
    """A failing tool must surface its error to the LLM (never a guess)."""
    def failing_tool(name, arguments):
        return json.dumps({"error": "backend returned 503: db down"})

    monkeypatch.setattr("agent.agent.execute_tool", failing_tool)
    client = fake_client([
        _msg(None, tool_calls=[("get_prediction_statistics", "{}")]),
        _msg("The statistics could not be retrieved: db down."),
    ])
    answer = run_agent("How many Box_broken images?")

    assert "could not be retrieved" in answer
    # the error JSON was fed back so the model saw it verbatim
    second_call_messages = client.chat.completions.seen_payloads[1]["messages"]
    assert any(
        m["role"] == "tool" and "db down" in m["content"]
        for m in second_call_messages
    )


def test_run_agent_max_rounds(fake_client, stub_execute_tool):
    """Runaway tool loops must stop at the cap, not hang."""
    fake_client([_msg(None, tool_calls=[("get_model_info", "{}")])] * 10)
    answer = run_agent("loop?", max_tool_rounds=3)
    assert "could not finish" in answer
