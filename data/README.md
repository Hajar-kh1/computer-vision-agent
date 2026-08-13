# Dataset — Package Damage Classification

> TODO: document your dataset here (spec §9). The instructor checks that the
> dataset is documented, split correctly, and free of leakage (spec §10, §43-A).

## Dataset Name
<!-- e.g. "Package Damage" (Kaggle) or a Roboflow project -->

## Source
<!-- URL + how to download. Suggested public sources:
  - Kaggle: search "package damage" (damaged vs undamaged boxes)
  - Roboflow Universe: search "package damage"
  - Your own photos of boxes (small, class-balanced)
-->

## Contents
| Field | Value |
|---|---|
| Number of images | |
| Number of classes | 2 (damaged / undamaged) |
| Images per class | |
| Image dimensions | |
| Class imbalance | |
| License | |

## Class Labels
The model must output exactly these labels (also mirrored in `models/labels.json`):

```json
{"0": "damaged", "1": "undamaged"}
```

## Expected Folder Layout
After running `training/download_dataset.py`, the split should be produced under `data/processed/`:

```text
data/processed/
├── train/{damaged,undamaged}/
├── val/{damaged,undamaged}/
└── test/{damaged,undamaged}/
```

## Split (spec §10)
- Training 70% / Validation 15% / Test 15%  (or 80/10/10)
- Fixed random seed: `SEED = 42`
- Split by image (no duplicates across splits) to avoid data leakage.

## Example Images
<!-- add 2–3 example image paths here -->
