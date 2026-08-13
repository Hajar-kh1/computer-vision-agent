"""Package Damage dataset loading and splitting (spec §9–§10).

TODO (Student 1 — CV Engineer):
- Load raw images from ``data/raw`` (per-class folders, torchvision ImageFolder style).
- Apply the fixed split: train/val/test with SEED = 42 (70/15/15 or 80/10/10).
- Write the split to ``data/processed/{train,val,test}/<class>/``.
- Return torch ``Dataset`` / ``DataLoader`` objects for training and evaluation.
- Avoid data leakage: no image may appear in more than one split.

Suggested signatures:
    def load_raw_dataset(raw_dir: Path) -> torchvision.datasets.ImageFolder: ...
    def split_dataset(...) -> tuple[train, val, test]: ...
    def get_dataloaders(data_root: Path, batch_size: int = 32) -> dict: ...
"""

SEED = 42  # fixed random seed required by the spec
