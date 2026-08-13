"""Train the package-damage classifier with transfer learning (spec §11–§13).

TODO (Student 1 — CV Engineer):
- Load data via ``dataset.py`` + ``transforms.py``.
- Transfer learning: start from a pretrained backbone
  (ResNet18 / MobileNetV3 / EfficientNet-B0 / ConvNeXt Tiny / ViT Tiny)
  and replace the final classification head with 2 outputs (damaged/undamaged).
- Train for a sensible number of epochs; record per-epoch:
      training loss, validation loss, training accuracy, validation accuracy.
- Save artifacts:
      models/model.pt      <- full model state (torch.save(model.state_dict(), ...))
      models/labels.json   <- {"0": "damaged", "1": "undamaged"}
- Do NOT use an interactive notebook — this must run from the CLI:
      uv run python training/train.py --data data/processed --epochs 10

Suggested signature:
    def train(data_root: Path, epochs: int, batch_size: int, lr: float) -> dict: ...
"""

# TODO: implement main() with argparse (--data, --epochs, --batch-size, --lr, --model-arch)
