"""Agent tool-calling tests (spec §35 recommended: test_agent_tool_call; §18 grounding).

TODO:
- test_agent_tool_call: run agent.execute_tool("get_prediction_history", {...})
  against a test DB and assert the result contains real stored data.
- test_agent_grounding: agent prompt + tool registry reject hallucination —
  e.g. the system prompt contains the "Never invent prediction results" rule
  and every tool schema is present in agent/tools.py.
- test_tool_failure_reported: when a tool errors (e.g. missing record), the
  agent's response explains the failure instead of inventing data.
"""
