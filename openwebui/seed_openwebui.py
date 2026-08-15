"""One-shot Open WebUI seeder (spec §20 automation).

Runs inside the open-webui image as the `open-webui-init` compose service.
Configures everything that is normally done by hand in the UI:

  1. OpenAI-compatible connection (from LLM_API_KEY / LLM_BASE_URL env)
  2. The package_damage_tools tool (content from the mounted repo file)
  3. A model record with the tool attached + the system prompt
  4. An admin account (ADMIN_EMAIL / ADMIN_PASSWORD env) so no signup is needed

Idempotent: safe to run on every start; existing rows are left untouched.
The open-webui service must have booted once so the DB schema exists
(compose runs this after open-webui is healthy).
"""

import asyncio
import json
import os
import sys

TOOL_ID = "package_damage_tools"
MODEL_ID = os.getenv("ADMIN_MODEL_ID", "package-damage-assistant")
TOOL_FILE = "/app/openwebui-seed/package_damage_tools.py"
SYSTEM_PROMPT_FILE = "/app/openwebui-seed/SYSTEM_PROMPT.txt"

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

# Same capabilities as the manually-created working model.
CAPABILITIES = {
    "file_context": True,
    "vision": True,
    "file_upload": True,
    "web_search": False,
    "image_generation": False,
    "code_interpreter": False,
    "terminal": False,
    "citations": False,
    "status_updates": False,
    "memory": False,
    "builtin_tools": False,
}


def log(msg: str) -> None:
    print(f"[seed] {msg}", flush=True)


async def main() -> int:
    log("starting")

    # The open-webui image runs python from /app/backend (see start.sh);
    # add it to sys.path so the open_webui package is importable here.
    sys.path.insert(0, "/app/backend")
    os.environ.setdefault("WEBUI_SECRET_KEY", "seed-only-secret-key")

    # Importing the app module creates the DB schema (43 tables) on a fresh
    # volume — same as a normal open-webui boot.
    import open_webui.main  # noqa: F401

    from open_webui.internal.db import get_async_db_context
    from open_webui.models.config import Config

    async with get_async_db_context() as db:
        # ------------------------------------------------------------------
        # 1. OpenAI-compatible connection from env
        # ------------------------------------------------------------------
        if LLM_BASE_URL:
            await Config.upsert(
                {
                    "openai.api_base_urls": [LLM_BASE_URL],
                    "openai.api_keys": [LLM_API_KEY],
                    "openai.api_configs": {
                        "0": {
                            "enable": True,
                            "tags": [],
                            "prefix_id": "",
                            "model_ids": [],
                            "connection_type": "external",
                            "auth_type": "bearer",
                            "passthrough_params": [],
                        }
                    },
                }
            )
            log(f"connection configured -> {LLM_BASE_URL}")
        else:
            log("LLM_BASE_URL empty, skipping connection setup")

        # ------------------------------------------------------------------
        # 2. Tool (from the repo file)
        # ------------------------------------------------------------------
        from open_webui.models.tools import ToolForm, Tools
        from open_webui.utils.tools import get_tool_specs, load_tool_module_by_id

        existing = await Tools.get_tool_by_id(TOOL_ID, db=db)
        if existing:
            log(f"tool '{TOOL_ID}' already exists, skipping")
        else:
            if not os.path.exists(TOOL_FILE):
                log(f"ERROR: tool file not found at {TOOL_FILE}")
                return 1
            content = open(TOOL_FILE, encoding="utf-8").read()
            module, _ = await load_tool_module_by_id(TOOL_ID, content=content)
            specs = get_tool_specs(module)
            form = ToolForm(
                id=TOOL_ID,
                name=TOOL_ID,
                content=content,
                meta={"description": "Package damage detection tools"},
            )
            await Tools.insert_new_tool("", form, specs, db=db)
            log(f"tool '{TOOL_ID}' created with {len(specs)} tools")

        # ------------------------------------------------------------------
        # 3. Model (tool attached + system prompt)
        # ------------------------------------------------------------------
        from open_webui.models.models import ModelForm, ModelMeta, ModelParams, Models

        existing_model = await Models.get_model_by_id(MODEL_ID, db=db)
        if existing_model:
            log(f"model '{MODEL_ID}' already exists, skipping")
        else:
            if not LLM_MODEL:
                log("ERROR: LLM_MODEL empty, cannot create model")
                return 1
            system_prompt = ""
            if os.path.exists(SYSTEM_PROMPT_FILE):
                system_prompt = open(SYSTEM_PROMPT_FILE, encoding="utf-8").read()
            meta = ModelMeta(
                description="Package damage detection assistant",
                capabilities=CAPABILITIES,
                toolIds=[TOOL_ID],
                system=system_prompt,
            )
            form = ModelForm(
                id=MODEL_ID,
                base_model_id=LLM_MODEL,
                name="Package Damage Assistant",
                meta=meta,
                params=ModelParams(),
            )
            await Models.insert_new_model(form, "", db=db)
            log(f"model '{MODEL_ID}' created (base: {LLM_MODEL})")

        log("done")
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
