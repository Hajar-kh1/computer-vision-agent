"""Model loading + inference service (spec §13, §14, §50).

Design:
- The checkpoint (models/model.pt) carries everything we need:
  model_state_dict, class_names, model_version, input_size.
- The model is loaded ONCE into a module-level singleton at startup
  (main.py lifespan) — never per request.
- Preprocessing matches training/transforms.py get_eval_transforms():
  PIL -> RGB -> Resize(input_size) -> ToTensor -> ImageNet normalize.
- ``predict()`` returns the standard PredictionResponse dict; on decode
  failure it raises InferenceError so the API layer can answer with a
  clean 4xx instead of a traceback.

Testability: the API layer depends on ``get_inference()``, which tests
override with a fake classifier — no torch / no model file needed in tests.
"""

import io
import time
from pathlib import Path
from typing import Any

import torch
from PIL import Image, UnidentifiedImageError
from torch import nn
from torchvision import transforms
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# model_name -> factory, mirroring training/train.py create_model().
_MODEL_FACTORIES: dict[str, Any] = {
    "mobilenet_v3_small": lambda num_classes: _build_mobilenet_v3_small(num_classes),
}


def _build_mobilenet_v3_small(num_classes: int) -> nn.Module:
    """MobileNetV3-Small with a fresh classifier head (matches training)."""
    model = mobilenet_v3_small(weights=None)
    for parameter in model.features.parameters():
        parameter.requires_grad = False
    input_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(input_features, num_classes)
    return model


class InferenceError(Exception):
    """Raised for unreadable/corrupt images or inference failures."""


class ModelInference:
    """Load the checkpoint once and classify package images from bytes."""

    def __init__(
        self,
        model_path: Path | str,
        labels_path: Path | str | None = None,
    ) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        checkpoint = torch.load(
            str(model_path),
            map_location=self.device,
            weights_only=False,
        )

        self.class_names: list[str] = list(checkpoint["class_names"])
        self.model_name: str = checkpoint.get("model_name", "unknown")
        self.model_version: str = checkpoint.get("model_version", "unknown")
        self.input_size: int = int(checkpoint.get("input_size", 224))

        factory = _MODEL_FACTORIES.get(self.model_name)
        if factory is None:
            raise InferenceError(
                f"Unsupported model architecture in checkpoint: {self.model_name}"
            )

        self.model: nn.Module = factory(len(self.class_names))
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model = self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose(
            [
                transforms.Resize((self.input_size, self.input_size)),
                transforms.ToTensor(),
                transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ]
        )

        if labels_path is not None and Path(labels_path).exists():
            self.labels_path = Path(labels_path)
        else:
            self.labels_path = None

    def predict(self, image_bytes: bytes, top_k: int = 2) -> dict:
        """Classify one image (JPEG/PNG/WebP bytes) and return the standard dict."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.load()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InferenceError(f"Could not read image: {exc}") from exc

        image = image.convert("RGB")
        tensor = self.transform(image).unsqueeze(0).to(self.device)

        start_time = time.perf_counter()
        with torch.inference_mode():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)[0]
        inference_ms = (time.perf_counter() - start_time) * 1000

        k = min(top_k, len(self.class_names))
        top_probabilities, top_indices = torch.topk(probabilities, k=k)

        top_predictions = [
            {
                "class_name": self.class_names[index],
                "probability": round(float(probability), 4),
            }
            for probability, index in zip(
                top_probabilities.cpu().tolist(),
                top_indices.cpu().tolist(),
            )
        ]

        return {
            "predicted_class": top_predictions[0]["class_name"],
            "confidence": top_predictions[0]["probability"],
            "top_predictions": top_predictions,
            "inference_ms": round(inference_ms, 2),
            "model_version": self.model_version,
        }

    @property
    def loaded(self) -> bool:
        return self.model is not None


# ---------------------------------------------------------------------------
# Singleton holder — set once in main.py lifespan, read by API dependencies.
# ---------------------------------------------------------------------------

_inference: ModelInference | None = None


def init_inference(model_path: Path | str) -> ModelInference:
    """Load the model once at startup and stash it as the global instance."""
    global _inference
    _inference = ModelInference(model_path)
    return _inference


def get_inference() -> ModelInference:
    """FastAPI dependency: return the loaded model (503 if not loaded yet)."""
    if _inference is None:
        raise InferenceError("Model is not loaded")
    return _inference


def reset_inference() -> None:
    """Testing helper: clear the singleton between tests."""
    global _inference
    _inference = None
