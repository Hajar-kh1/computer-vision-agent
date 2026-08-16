"""Download / prepare the package-damage dataset (spec §9).

TODO (Student 1 — CV Engineer):
- Pick a public package-damage dataset (Kaggle, Roboflow Universe, or self-collected).
- Download into data/raw/ as per-class folders: data/raw/damaged, data/raw/undamaged.
- Print a summary: image count per class, dimensions, any imbalance.
- Keep this script idempotent (skip download if files already exist).

Examples:
    # Kaggle CLI (after `kaggle auth`)
    # kaggle datasets download -d <owner>/<dataset> -p data/raw --unzip

    # Roboflow (after creating an API key) — see data/README.md
"""
