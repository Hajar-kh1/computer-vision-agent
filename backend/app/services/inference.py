"""Model loading + inference service (spec §13, §14, §50).

TODO (Student 2, with CV Engineer):
- Load models/model.pt once at startup into a module-level singleton
  (or a class instance created in main.py lifespan). Never reload per request.
- Load models/labels.json for the class mapping.
- Preprocess: PIL open -> RGB -> resize to training input size (224x224) ->
  ImageNet normalize (must match training/transforms.py).
- Forward pass with torch.inference_mode(), softmax -> top-K (K=2) probabilities.
- Return the standard PredictionResponse dict incl. inference_ms timing.

Suggested signature:
    class ModelInference:
        def __init__(self, model_path: Path, labels_path: Path): ...
        def predict(self, image_bytes: bytes) -> dict: ...

Design for testability: allow tests to inject a fake model/classifier so
tests/ do not require torch or a trained model.
"""
