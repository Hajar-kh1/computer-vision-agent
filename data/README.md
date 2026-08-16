# Package Detection Dataset

## Dataset Information

- Name: Package Detection v6
- Source: Roboflow Universe
- URL: https://universe.roboflow.com/roboflow-ngkro/package-detection-e1ssd
- Export date: February 12, 2024
- Original format: COCO Object Detection
- Total images: 1,200
- Image size: 640 × 640 pixels
- License: Not specified by the dataset provider

## Classes

The usable classes are:

1. Box
2. Box_broken
3. Open_package
4. Package

The COCO file also contains a category named `exp3`, but it has zero annotations and is ignored.

## Dataset Split

| Split | Total images | Single-class images | Multi-class images |
|---|---:|---:|---:|
| Train | 840 | 835 | 5 |
| Validation | 240 | 239 | 1 |
| Test | 120 | 119 | 1 |
| Total | 1,200 | 1,193 | 7 |

## Class Distribution

### Training

| Class | Images |
|---|---:|
| Box | 208 |
| Box_broken | 203 |
| Open_package | 218 |
| Package | 206 |

### Validation

| Class | Images |
|---|---:|
| Box | 64 |
| Box_broken | 63 |
| Open_package | 54 |
| Package | 58 |

### Testing

| Class | Images |
|---|---:|
| Box | 25 |
| Box_broken | 32 |
| Open_package | 29 |
| Package | 33 |

## Preprocessing Applied by Roboflow

- Auto-orientation with EXIF orientation removed
- Images resized to 640 × 640 using stretch resizing
- No image augmentation was applied

## Classification Conversion

The dataset was originally exported for object detection. For this project,
it will be converted to single-label image classification.

Images containing exactly one unique category will be used. Seven images
containing objects from more than one category will be excluded to avoid
assigning an ambiguous label.

Multiple objects of the same category in one image are treated as one
classification label.

The original train, validation, and test splits will be preserved to avoid
data leakage.