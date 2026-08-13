"""Open WebUI Function — Package Damage tools (paste into Workspace > Functions).

TODO (Student 3): finish this so it can be pasted as-is.

Open WebUI Functions expose a `tools` list; each tool's callable is a module-
level function with the SAME name as the tool. It runs inside the Open WebUI
container and must call the backend over HTTP (Docker service name `backend`).

Note: Open WebUI's function runner has a `__import__` restriction — use only
stdlib (`urllib`) or libraries Open WebUI ships, or add an extra pip package
in the open-webui container if needed.
"""

import json
import urllib.request

# TODO: point at the deployed backend (Docker service name in compose,
# public URL in production).
BACKEND_URL = "http://backend:8000"


def _get(path: str, params: dict | None = None) -> dict:
    """Small HTTP GET helper using only stdlib."""
    url = BACKEND_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode())


def get_prediction_history(limit: int = 5) -> str:
    """Retrieve the most recent N predictions from PostgreSQL."""
    # TODO: call GET {BACKEND_URL}/api/v1/predictions?limit={limit}
    ...


def get_prediction_statistics() -> str:
    """Retrieve aggregated prediction information."""
    # TODO: call GET {BACKEND_URL}/api/v1/stats
    ...


def get_model_info() -> str:
    """Retrieve information about the currently deployed model."""
    # TODO: call GET {BACKEND_URL}/api/v1/model
    ...


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_prediction_history",
            "description": "Retrieve the most recent N predictions from PostgreSQL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 5}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_prediction_statistics",
            "description": "Retrieve aggregated prediction information.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_model_info",
            "description": "Retrieve information about the currently deployed model.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
