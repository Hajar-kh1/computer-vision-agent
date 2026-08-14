# Backend image — built from the repo root so it can COPY pyproject.toml + uv.lock
# (compose.yaml uses: context: ., dockerfile: backend/Dockerfile)
#
# Two-stage uv sync:
#   1. deps only (cached layer — rebuilds only when pyproject/uv.lock change)
#   2. project files copied, then final sync installs everything in /app
#
# The backend runs as `backend.app.main:app` (package layout), so the CMD
# imports the module that main.py defines. `uv run` puts the project root on
# the path for the virtual project, making `backend`, `agent`, `training`
# all importable inside the container.

FROM python:3.12-slim

# uv binary (kept small; the environment itself is built from uv.lock)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Dependencies first (layer cached unless the lockfile changes).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2. Project code (model artifact, training package, backend, agent).
COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
