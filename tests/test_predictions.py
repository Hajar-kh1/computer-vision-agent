"""Prediction persistence + history tests (spec §35).

test_database_insert, test_prediction_history, test_missing_prediction, test_stats.
"""


def _post_prediction(client, name="package.jpg", image_bytes=None):
    if image_bytes is None:
        import io

        from PIL import Image

        buffer = io.BytesIO()
        Image.new("RGB", (32, 32), color=(30, 90, 160)).save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
    return client.post(
        "/api/v1/predict",
        files={"image": (name, image_bytes, "image/jpeg")},
    )


def test_database_insert(client):
    """After POST /api/v1/predict, a row exists with all required fields."""
    response = _post_prediction(client)
    assert response.status_code == 200

    history = client.get("/api/v1/predictions").json()
    assert history["total"] >= 1

    record = history["items"][0]
    assert record["image_name"] == "package.jpg"
    assert record["predicted_class"] == "damaged"
    assert record["confidence"] == 0.9
    assert record["inference_ms"] == 1.23
    assert record["model_version"] == "1.0.0"
    assert record["id"] >= 1


def test_prediction_history_newest_first(client):
    """GET /api/v1/predictions returns records newest first."""
    _post_prediction(client, name="first.jpg")
    _post_prediction(client, name="second.jpg")

    history = client.get("/api/v1/predictions").json()
    assert history["total"] == 2
    assert history["items"][0]["image_name"] == "second.jpg"
    assert history["items"][1]["image_name"] == "first.jpg"

    # limit works
    limited = client.get("/api/v1/predictions?limit=1").json()
    assert limited["total"] == 1

    # single record by id
    first_id = history["items"][1]["id"]
    single = client.get(f"/api/v1/predictions/{first_id}")
    assert single.status_code == 200
    assert single.json()["image_name"] == "first.jpg"


def test_missing_prediction(client):
    """GET /api/v1/predictions/{missing} -> 404 with a clean error."""
    response = client.get("/api/v1/predictions/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_stats(client):
    """GET /api/v1/stats returns total_predictions + class_distribution."""
    _post_prediction(client)

    response = client.get("/api/v1/stats")
    assert response.status_code == 200

    body = response.json()
    assert body["total_predictions"] == 1
    assert body["class_distribution"] == {"damaged": 1}
    assert body["avg_confidence"] == 0.9
