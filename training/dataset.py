"""COCO dataset loader converted to single-label image classification."""

import json
import random
from pathlib import Path
from typing import Callable

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from training.transforms import get_eval_transforms, get_train_transforms


SEED = 42
CLASS_NAMES = ["Box", "Box_broken", "Open_package", "Package"]
CLASS_TO_INDEX = {name: index for index, name in enumerate(CLASS_NAMES)}


def set_seed(seed: int = SEED) -> None:
    """Set random seeds for reproducible training."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class CocoClassificationDataset(Dataset):
    """Convert single-class COCO images into a classification dataset."""

    def __init__(
        self,
        split_dir: Path,
        transform: Callable | None = None,
    ) -> None:
        self.split_dir = Path(split_dir)
        self.transform = transform

        annotation_path = self.split_dir / "_annotations.coco.json"

        if not annotation_path.exists():
            raise FileNotFoundError(
                f"COCO annotation file not found: {annotation_path}"
            )

        with annotation_path.open("r", encoding="utf-8") as file:
            coco_data = json.load(file)

        category_names = {
            category["id"]: category["name"]
            for category in coco_data["categories"]
        }

        annotations_by_image: dict[int, list[int]] = {}

        for annotation in coco_data["annotations"]:
            image_id = annotation["image_id"]
            category_id = annotation["category_id"]

            annotations_by_image.setdefault(image_id, []).append(category_id)

        self.samples: list[tuple[Path, int]] = []
        self.excluded_images: list[str] = []

        for image_info in coco_data["images"]:
            image_id = image_info["id"]
            file_name = image_info["file_name"]

            unique_category_ids = set(
                annotations_by_image.get(image_id, [])
            )

            if len(unique_category_ids) != 1:
                self.excluded_images.append(file_name)
                continue

            category_id = next(iter(unique_category_ids))
            class_name = category_names.get(category_id)

            if class_name not in CLASS_TO_INDEX:
                self.excluded_images.append(file_name)
                continue

            image_path = self.split_dir / file_name

            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            label = CLASS_TO_INDEX[class_name]
            self.samples.append((image_path, label))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        image_path, label = self.samples[index]

        with Image.open(image_path) as image:
            image = image.convert("RGB")

            if self.transform is not None:
                image = self.transform(image)

        return image, label


def get_dataloaders(
    data_root: Path,
    batch_size: int = 32,
    input_size: int = 224,
    num_workers: int = 0,
) -> dict[str, DataLoader]:
    """Create training, validation, and test data loaders."""
    set_seed()

    data_root = Path(data_root)

    datasets = {
        "train": CocoClassificationDataset(
            data_root / "train",
            transform=get_train_transforms(input_size),
        ),
        "val": CocoClassificationDataset(
            data_root / "valid",
            transform=get_eval_transforms(input_size),
        ),
        "test": CocoClassificationDataset(
            data_root / "test",
            transform=get_eval_transforms(input_size),
        ),
    }

    generator = torch.Generator()
    generator.manual_seed(SEED)

    return {
        "train": DataLoader(
            datasets["train"],
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            generator=generator,
        ),
        "val": DataLoader(
            datasets["val"],
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
        ),
        "test": DataLoader(
            datasets["test"],
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
        ),
    }