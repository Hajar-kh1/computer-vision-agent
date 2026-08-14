"""Health endpoint tests (spec §35: test_health)."""


def test_health(client):
    """GET /health returns 200 with the readiness shape."""
    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "healthy"
    assert body["api"] == "healthy"
    # SQLite test DB answers SELECT 1 -> healthy
    assert body["database"] == "healthy"
    # Fake classifier is registered as the loaded model
    assert body["model"] == "loaded"
