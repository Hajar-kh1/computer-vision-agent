"""Shared pytest fixtures (spec §35).

- ``client``: FastAPI TestClient with an in-memory SQLite database (the
  get_db dependency is overridden) so tests run WITHOUT PostgreSQL.
- ``fake_classifier``: a deterministic fake model injected into the
  inference dependency (no torch needed in tests) that always returns
  {"predicted_class": "damaged", "confidence": 0.9, ...}.
- ``sample_image_bytes``: a tiny valid JPEG (PIL-generated) plus a .txt
  bytes fixture for the invalid-image test.
"""

import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.services import inference as inference_service
from backend.app.services.inference import get_inference


class FakeClassifier:
    """Deterministic classifier — no torch, no model file (spec §35)."""

    model_name = "fake_mobilenet"
    model_version = "1.0.0"
    class_names = ["damaged", "undamaged"]
    input_size = 224

    def predict(self, image_bytes: bytes, top_k: int = 2) -> dict:
        return {
            "predicted_class": "damaged",
            "confidence": 0.9,
            "top_predictions": [
                {"class_name": "damaged", "probability": 0.9},
                {"class_name": "undamaged", "probability": 0.1},
            ],
            "inference_ms": 1.23,
            "model_version": "1.0.0",
        }


@pytest.fixture()
def client(monkeypatch):
    """TestClient with SQLite + fake model; fresh DB per test."""
    # In-memory SQLite, shared connection so the same DB is visible everywhere.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine, autocommit=False, autoflush=False
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Fake model: both the dependency and the health check see it as "loaded".
    fake = FakeClassifier()
    inference_service._inference = fake  # type: ignore[assignment]

    # Lifespan must not try to reach PostgreSQL or load the real checkpoint.
    monkeypatch.setattr("backend.app.main.init_db", lambda: None)
    monkeypatch.setattr(
        "backend.app.main.inference_service.init_inference",
        lambda *a, **k: fake,
    )
    monkeypatch.setattr(
        "backend.app.main.inference_service.reset_inference", lambda: None
    )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_inference] = lambda: fake

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    inference_service._inference = None


@pytest.fixture()
def fake_classifier() -> FakeClassifier:
    """Direct access to the fake model (for pure-service tests)."""
    return FakeClassifier()


@pytest.fixture()
def sample_image_bytes() -> bytes:
    """A tiny valid JPEG generated with PIL."""
    buffer = io.BytesIO()
    Image.new("RGB", (32, 32), color=(120, 80, 40)).save(buffer, format="JPEG")
    return buffer.getvalue()


@pytest.fixture()
def text_file_bytes() -> bytes:
    """A .txt payload — the instructor's failure test (spec §41)."""
    return b"this is not an image, just a plain text document"
