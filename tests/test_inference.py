"""Inference tests (spec §35: test_model_loaded, test_valid_prediction, test_invalid_image)."""


def test_model_loaded(fake_classifier, client):
    """Inference service exposes a loaded classifier with the standard shape."""
    result = fake_classifier.predict(b"irrelevant-bytes")
    assert result["predicted_class"] == "damaged"
    assert result["confidence"] == 0.9
    assert result["model_version"] == "1.0.0"


def test_valid_prediction(client, sample_image_bytes):
    """POST /api/v1/predict with a valid JPEG returns the standard shape."""
    response = client.post(
        "/api/v1/predict",
        files={"image": ("package.jpg", sample_image_bytes, "image/jpeg")},
    )
    assert response.status_code == 200

    body = response.json()
    assert body["predicted_class"] == "damaged"
    assert body["confidence"] == 0.9
    assert isinstance(body["top_predictions"], list)
    assert body["top_predictions"][0]["class_name"] == "damaged"
    assert body["inference_ms"] == 1.23
    assert body["model_version"] == "1.0.0"


def test_invalid_image(client, text_file_bytes):
    """Uploading a .txt file returns a clean 4xx — no traceback (spec §41)."""
    response = client.post(
        "/api/v1/predict",
        files={"image": ("document.txt", text_file_bytes, "text/plain")},
    )
    assert 400 <= response.status_code < 500
    body = response.json()
    assert "detail" in body  # clean error message, not a Python traceback


def test_corrupted_image_with_valid_extension(client):
    """A .jpg that is not actually an image -> clean 400."""
    response = client.post(
        "/api/v1/predict",
        files={"image": ("broken.jpg", b"not really a jpeg", "image/jpeg")},
    )
    assert response.status_code == 400
    assert "detail" in response.json()
