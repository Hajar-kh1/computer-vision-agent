"""Image transforms / preprocessing + augmentation (spec §11, §5).

TODO (Student 1 — CV Engineer):
- Define train transforms: resize to model input size, random flips/rotation/
  color jitter (reasonable augmentation — do NOT overdo it for a 5-hour sprint).
- Define validation/test transforms: resize + normalize only (no augmentation).
- Use ImageNet mean/std normalization so transfer-learning backbones work:
      mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225]
- Keep the SAME input size here and in backend/app/services/inference.py.

Suggested signatures:
    def get_train_transforms(input_size: int = 224) -> transforms.Compose: ...
    def get_eval_transforms(input_size: int = 224) -> transforms.Compose: ...
"""
