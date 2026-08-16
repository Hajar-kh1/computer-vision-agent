# Live Demo Script (spec §40–§42)

## Demo 1 — Computer Vision
1. Open the public frontend.
2. Upload a new package image.
3. Run classification.
4. Show predicted class + confidence.

## Demo 2 — Database
Open prediction history → verify the new prediction is stored.

## Demo 3 — Agent Tool Calling (Open WebUI)
Ask: "Show me the latest three predictions."
→ agent must retrieve REAL data from the system.

## Demo 4 — Model Information
Ask: "Which computer vision model is currently deployed?"
→ answer must come from the model-info tool, not the LLM's memory.

## Demo 5 — Production
Open the app from a public URL (not localhost).

## Optional Demo 6 — Voice
Say: "Show me the latest prediction." → STT → agent → tool → TTS answer.

## Failure test (spec §41)
Upload `document.txt` → clean validation error (no crash, no traceback).

## Persistence test (spec §42)
Restart the backend / redeploy → prediction history remains.
