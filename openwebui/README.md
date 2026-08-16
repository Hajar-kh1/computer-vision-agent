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
Open WebUI implements tools as **Tools** (Python files in its "Workspace →
Tools" UI — newer versions renamed Functions to Tools). This Open WebUI
build requires a class named `Tools` in the file: every public method of
that class becomes a tool. The method's docstring becomes the tool
description (`:param:` lines become parameter descriptions) and its type
hints the parameter schema. The file contains no third-party imports.

The tool runs INSIDE the Open WebUI container, so it must call your
backend over HTTP (e.g. `http://backend:8000/api/v1/...` using Docker's
service name — spec §29) or via a public URL in production.

## Files
- `openwebui/package_damage_tools.py` — paste its contents into
  Open WebUI → Workspace → Tools (create new tool) and save. Then attach it
  to the model: Admin Panel → Models → (model) → Tools → enable it.

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
