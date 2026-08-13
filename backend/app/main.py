"""FastAPI application entrypoint (spec §15, §32, §33).

TODO (Student 2 — Backend Engineer):
- Create the FastAPI app, include all routers from ``app/api``.
- Load the ML model ONCE at startup (lifespan) — never per request (§50 Q3).
- Configure CORS from settings.CORS_ORIGINS (restrict, do not use "*" in prod).
- Add global exception handlers: invalid/corrupt image, oversized upload,
  inference failure, DB failure, missing record — no Python tracebacks to users.
- Mount routers under ``/api/v1``.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Package Damage Detection API",
    version="1.0.0",  # TODO: read from settings.MODEL_VERSION
)

# TODO: include routers:
#   app.include_router(health.router)
#   app.include_router(predictions.router, prefix="/api/v1")
#   app.include_router(history.router, prefix="/api/v1")
#   app.include_router(stats.router, prefix="/api/v1")
#   app.include_router(model_info.router, prefix="/api/v1")
