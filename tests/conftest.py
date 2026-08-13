"""Shared pytest fixtures (spec §35).

TODO (Students 2 & 3):
- Fixture `client`: FastAPI TestClient with an in-memory SQLite database
  (override the get_db dependency) so tests run WITHOUT PostgreSQL.
- Fixture `fake_classifier`: inject a deterministic fake model into the
  inference service (no torch needed in tests) that always returns
  {"predicted_class": "damaged", "confidence": 0.9, ...}.
- Fixture `sample_image`: a tiny valid JPEG (e.g. PIL-generated) for
  test_valid_prediction; plus a .txt bytes fixture for test_invalid_image.
"""

# import pytest
# from fastapi.testclient import TestClient
#
# @pytest.fixture()
# def client(): ...
#
# @pytest.fixture()
# def sample_image_bytes(): ...
