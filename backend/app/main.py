"""FastAPI application entrypoint (spec §15, §32, §33).

- Loads the ML model ONCE at startup via lifespan (never per request, §50 Q3).
- Creates database tables at startup.
- CORS restricted to settings.CORS_ORIGINS (no "*" in production, §34).
- Global exception handlers return clean JSON errors — no tracebacks to users.
- Routers mounted under /api/v1.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api import health, history, model_info, predictions, stats
from backend.app.config import settings
from backend.app.database import init_db
from backend.app.services import inference as inference_service
from backend.app.services.inference import InferenceError

logger = logging.getLogger("package-damage.backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables, load model once. Shutdown: release resources."""
    try:
        init_db()
        logger.info("Database tables ready.")
    except Exception:  # noqa: BLE001 — boot must not crash if DB is briefly down
        logger.exception("Database initialization failed at startup.")

    try:
        inference_service.init_inference(settings.MODEL_PATH)
        logger.info("Model loaded: %s", settings.MODEL_PATH)
    except Exception:  # noqa: BLE001
        logger.exception(
            "Model failed to load at startup (%s) — /health will report not_loaded.",
            settings.MODEL_PATH,
        )
        inference_service.reset_inference()

    yield

    inference_service.reset_inference()


app = FastAPI(
    title="Package Damage Detection API",
    version=settings.MODEL_VERSION,
    lifespan=lifespan,
)

# --- CORS (spec §34: restricted origins, never "*" in production) ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers (spec §15) -----------------------------------------------------
app.include_router(health.router)
app.include_router(predictions.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")
app.include_router(model_info.router, prefix="/api/v1")


# --- Global exception handlers (spec §33: clean errors, no tracebacks) ------

@app.exception_handler(InferenceError)
async def inference_error_handler(request: Request, exc: InferenceError) -> JSONResponse:
    """Model not loaded / inference failure -> 503 Service Unavailable."""
    return JSONResponse(
        status_code=503,
        content={"detail": f"Inference unavailable: {exc}"},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Request body/form validation -> clean 422 (no FastAPI internals)."""
    errors = exc.errors()
    first = errors[0] if errors else {}
    loc = ".".join(str(part) for part in first.get("loc", []) if part != "body")
    message = first.get("msg", "Invalid request")
    return JSONResponse(
        status_code=422,
        content={"detail": f"Invalid request ({loc}): {message}"},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last-resort handler: log the real error, return a clean 500."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )
