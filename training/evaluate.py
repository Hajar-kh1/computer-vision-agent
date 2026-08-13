"""Evaluate the trained classifier on the held-out test dataset."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from torch import nn

from training.dataset import CLASS_NAMES, get_dataloaders
from training.train import create_model


def evaluate(
    model_path: Path,
    data_root: Path,
    batch_size: int = 32,
) -> dict:
    """Evaluate the saved model and write metrics and confusion matrix."""
    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    checkpoint = torch.load(
        model_path,
        map_location=device,
        weights_only=False,
    )

    class_names = checkpoint.get("class_names", CLASS_NAMES)
    input_size = checkpoint.get("input_size", 224)

    model = create_model(num_classes=len(class_names))
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    model.eval()

    dataloaders = get_dataloaders(
        data_root=data_root,
        batch_size=batch_size,
        input_size=input_size,
    )
    test_loader = dataloaders["test"]

    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0
    total_samples = 0
    true_labels = []
    predicted_labels = []

    with torch.inference_mode():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            logits = model(images)
            loss = criterion(logits, labels)
            predictions = logits.argmax(dim=1)

            batch_size_actual = labels.size(0)
            total_loss += loss.item() * batch_size_actual
            total_samples += batch_size_actual

            true_labels.extend(labels.cpu().tolist())
            predicted_labels.extend(predictions.cpu().tolist())

    test_loss = total_loss / total_samples
    test_accuracy = accuracy_score(true_labels, predicted_labels)

    precision, recall, f1_score, _ = precision_recall_fscore_support(
        true_labels,
        predicted_labels,
        average="weighted",
        zero_division=0,
    )

    matrix = confusion_matrix(
        true_labels,
        predicted_labels,
        labels=list(range(len(class_names))),
    )

    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    training_history_path = reports_dir / "training_history.json"
    training_report = {}

    if training_history_path.exists():
        with training_history_path.open("r", encoding="utf-8") as file:
            training_report = json.load(file)

    metrics = {
        "model_name": checkpoint.get(
            "model_name",
            "mobilenet_v3_small",
        ),
        "model_version": checkpoint.get("model_version", "1.0.0"),
        "classes": class_names,
        "input_size": input_size,
        "test_images": total_samples,
        "test_loss": test_loss,
        "test_accuracy": test_accuracy,
        "weighted_precision": precision,
        "weighted_recall": recall,
        "weighted_f1_score": f1_score,
        "best_validation_accuracy": checkpoint.get(
            "validation_accuracy"
        ),
        "training_time_seconds": training_report.get(
            "training_time_seconds"
        ),
        "confusion_matrix": matrix.tolist(),
    }

    with (reports_dir / "model_metrics.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(metrics, file, indent=2)

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=class_names,
    )
    display.plot(cmap="Blues", xticks_rotation=30)
    plt.title("Package Classification Confusion Matrix")
    plt.tight_layout()
    plt.savefig(
        reports_dir / "confusion_matrix.png",
        dpi=180,
    )
    plt.close()

    print(f"Device: {device}")
    print(f"Test images: {total_samples}")
    print(f"Test loss: {test_loss:.4f}")
    print(f"Test accuracy: {test_accuracy:.4f}")
    print(f"Weighted precision: {precision:.4f}")
    print(f"Weighted recall: {recall:.4f}")
    print(f"Weighted F1-score: {f1_score:.4f}")
    print("Saved reports/model_metrics.json")
    print("Saved reports/confusion_matrix.png")

    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the package classification model."
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("models/model.pt"),
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/raw/package_detection"),
    )
    parser.add_argument("--batch-size", type=int, default=32)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    evaluate(
        model_path=args.model,
        data_root=args.data,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()