# Open WebUI Integration (spec §20, §21)

Open WebUI is the required chat interface. It must be able to call the
application's real tools.

## Requirements checklist (spec §20)
- [ ] Run Open WebUI through Docker (already wired in `compose.yaml` → service `open-webui`)
- [ ] Connect Open WebUI to an LLM provider (`OPENAI_API_BASE_URL` + `OPENAI_API_KEY` env)
- [ ] Connect application tools to the chat environment
- [ ] Enable function/tool calling
- [ ] Verify at least two successful tool calls
- [ ] Demonstrate the tool response comes from the deployed system

## How Open WebUI calls your tools
Open WebUI implements tools as **Functions** (Python files in its "Workspace →
Functions" UI). Each function must export a `tools` list of dicts with
`name`, `description`, and `parameters`, plus a callable with that name that
runs when the LLM invokes the tool.

The function runs INSIDE the Open WebUI container, so it must call your
backend over HTTP (e.g. `http://backend:8000/api/v1/...` using Docker's
service name — spec §29) or via a public URL in production.

## Files
- `openwebui/package_damage_tools.py` — stub Function file: paste its contents
  into Open WebUI → Workspace → Functions and enable it.

## Flow to verify (spec §20)
```
User -> Open WebUI -> LLM -> Tool Call -> FastAPI -> Model / PostgreSQL
     -> Tool Result -> LLM -> User
```

Try in chat:
- "Show me the latest three predictions."      → calls get_prediction_history
- "Which model is currently deployed?"          → calls get_model_info
- "How many images were classified as Box_broken?" → calls get_prediction_statistics

## Voice (stretch, spec §21)
Open WebUI ships browser-based speech-to-text and text-to-speech. Enable
voice input in chat settings once tool calling works; the minimum voice
capability is: Voice Input -> STT -> Agent -> Tool.
