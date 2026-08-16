"""Reusable inference for the trained package classification model."""

import argparse
import time
from pathlib import Path

import torch
from PIL import Image
from torch import nn

from training.transforms import get_eval_transforms
from training.train import create_model


class PackageClassifier:
    """Load the model once and classify package images."""

    def __init__(
        self,
        model_path: Path = Path("models/model.pt"),
    ) -> None:
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        checkpoint = torch.load(
            model_path,
            map_location=self.device,
            weights_only=False,
        )

        self.class_names = checkpoint["class_names"]
        self.model_name = checkpoint["model_name"]
        self.model_version = checkpoint["model_version"]
        self.input_size = checkpoint["input_size"]

        self.model: nn.Module = create_model(
            num_classes=len(self.class_names)
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model = self.model.to(self.device)
        self.model.eval()

        self.transform = get_eval_transforms(self.input_size)

    def predict(
        self,
        image: Image.Image,
        top_k: int = 3,
    ) -> dict:
        """Classify one PIL image and return a structured result."""
        image = image.convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0)
        image_tensor = image_tensor.to(self.device)

        start_time = time.perf_counter()

        with torch.inference_mode():
            logits = self.model(image_tensor)
            probabilities = torch.softmax(logits, dim=1)[0]

        inference_ms = (time.perf_counter() - start_time) * 1000

        top_k = min(top_k, len(self.class_names))
        top_probabilities, top_indices = torch.topk(
            probabilities,
            k=top_k,
        )

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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify one package image."
    )
    parser.add_argument("image", type=Path)
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("models/model.pt"),
    )
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    classifier = PackageClassifier(args.model)

    with Image.open(args.image) as image:
        result = classifier.predict(image, top_k=args.top_k)

    print(result)


if __name__ == "__main__":
    main()