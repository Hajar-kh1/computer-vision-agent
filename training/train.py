"""Train a MobileNetV3 image classifier using transfer learning."""

import argparse
import json
import time
from pathlib import Path

import torch
from torch import nn
from torch.optim import Adam
from torchvision.models import (
    MobileNet_V3_Small_Weights,
    mobilenet_v3_small,
)

from training.dataset import CLASS_NAMES, get_dataloaders, set_seed


MODEL_VERSION = "1.0.0"
INPUT_SIZE = 224


def create_model(num_classes: int) -> nn.Module:
    """Create a pretrained MobileNetV3 Small classification model."""
    weights = MobileNet_V3_Small_Weights.DEFAULT
    model = mobilenet_v3_small(weights=weights)

    for parameter in model.features.parameters():
        parameter.requires_grad = False

    input_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(input_features, num_classes)

    return model


def run_epoch(
    model: nn.Module,
    dataloader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None = None,
) -> tuple[float, float]:
    """Run one training or validation epoch."""
    is_training = optimizer is not None

    if is_training:
        model.train()
    else:
        model.eval()

    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for images, labels in dataloader:
        images = images.to(device)
        labels = labels.to(device)

        if is_training:
            optimizer.zero_grad()

        with torch.set_grad_enabled(is_training):
            logits = model(images)
            loss = criterion(logits, labels)

            if is_training:
                loss.backward()
                optimizer.step()

        predictions = logits.argmax(dim=1)
        batch_size = labels.size(0)

        total_loss += loss.item() * batch_size
        total_correct += (predictions == labels).sum().item()
        total_samples += batch_size

    average_loss = total_loss / total_samples
    accuracy = total_correct / total_samples

    return average_loss, accuracy


def train(
    data_root: Path,
    epochs: int,
    batch_size: int,
    learning_rate: float,
) -> dict:
    """Train the model and save the best validation checkpoint."""
    set_seed()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Device: {device}")
    print(f"Classes: {CLASS_NAMES}")

    dataloaders = get_dataloaders(
        data_root=data_root,
        batch_size=batch_size,
        input_size=INPUT_SIZE,
    )

    print(f"Training images: {len(dataloaders['train'].dataset)}")
    print(f"Validation images: {len(dataloaders['val'].dataset)}")

    model = create_model(num_classes=len(CLASS_NAMES))
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(
        filter(lambda parameter: parameter.requires_grad, model.parameters()),
        lr=learning_rate,
    )

    models_dir = Path("models")
    reports_dir = Path("reports")
    models_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    best_validation_accuracy = 0.0
    history = []
    training_start = time.perf_counter()

    for epoch in range(1, epochs + 1):
        epoch_start = time.perf_counter()

        training_loss, training_accuracy = run_epoch(
            model=model,
            dataloader=dataloaders["train"],
            criterion=criterion,
            device=device,
            optimizer=optimizer,
        )

        validation_loss, validation_accuracy = run_epoch(
            model=model,
            dataloader=dataloaders["val"],
            criterion=criterion,
            device=device,
        )

        epoch_seconds = time.perf_counter() - epoch_start

        epoch_metrics = {
            "epoch": epoch,
            "training_loss": training_loss,
            "validation_loss": validation_loss,
            "training_accuracy": training_accuracy,
            "validation_accuracy": validation_accuracy,
            "epoch_seconds": epoch_seconds,
        }
        history.append(epoch_metrics)

        print(
            f"Epoch {epoch}/{epochs} | "
            f"train_loss={training_loss:.4f} | "
            f"val_loss={validation_loss:.4f} | "
            f"train_acc={training_accuracy:.4f} | "
            f"val_acc={validation_accuracy:.4f} | "
            f"time={epoch_seconds:.1f}s"
        )

        if validation_accuracy > best_validation_accuracy:
            best_validation_accuracy = validation_accuracy

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "model_name": "mobilenet_v3_small",
                    "model_version": MODEL_VERSION,
                    "class_names": CLASS_NAMES,
                    "input_size": INPUT_SIZE,
                    "validation_accuracy": validation_accuracy,
                },
                models_dir / "model.pt",
            )

            print("Saved new best model.")

    training_seconds = time.perf_counter() - training_start

    labels = {
        str(index): class_name
        for index, class_name in enumerate(CLASS_NAMES)
    }

    with (models_dir / "labels.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(labels, file, indent=2)

    training_report = {
        "model_name": "mobilenet_v3_small",
        "model_version": MODEL_VERSION,
        "device": str(device),
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "training_time_seconds": training_seconds,
        "best_validation_accuracy": best_validation_accuracy,
        "history": history,
    }

    with (reports_dir / "training_history.json").open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(training_report, file, indent=2)

    print(f"Best validation accuracy: {best_validation_accuracy:.4f}")
    print(f"Training time: {training_seconds:.1f} seconds")
    print("Saved models/model.pt")
    print("Saved models/labels.json")
    print("Saved reports/training_history.json")

    return training_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train the package classification model."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data/raw/package_detection"),
    )
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=0.001)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    train(
        data_root=args.data,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )


if __name__ == "__main__":
    main()