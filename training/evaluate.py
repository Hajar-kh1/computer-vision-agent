"""Evaluate the trained model on the held-out test set (spec §12, §43-A).

TODO (Student 1 — CV Engineer):
- Load models/model.pt + models/labels.json.
- Compute on the TEST split:
      test accuracy, precision, recall, F1-score, confusion matrix.
- Write machine-readable metrics to: reports/model_metrics.json
      (include training time if recorded in train.py).
- Verify the exported model works through the same preprocessing the
  backend inference service uses.

Suggested signature:
    def evaluate(model_path: Path, data_root: Path) -> dict: ...
"""

# TODO: implement main() and dump reports/model_metrics.json
