# Backend image — built from the repo root so it can COPY pyproject.toml + uv.lock
# (compose.yaml uses: context: ., dockerfile: backend/Dockerfile)

# TODO: implement per spec §26 (example provided there). Baseline:
#
#   FROM python:3.12-slim
#   COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
#   WORKDIR /app
#   COPY pyproject.toml uv.lock ./
#   RUN uv sync --frozen --no-dev --no-install-project
#   COPY . .
#   RUN uv sync --frozen --no-dev
#   EXPOSE 8000
#   CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
