from typing import List

import numpy as np
import torch
from albumentations import (
    BasicTransform,
    MotionBlur,
    Resize,
    Compose,
    CoarseDropout,
    Rotate,
    CLAHE,
    Blur,
    MedianBlur,
    GlassBlur,
    HueSaturationValue,
    RandomBrightnessContrast,
    OneOf,
    ImageCompression,
)


def img_to_tensor(im):
    tensor = torch.from_numpy(np.moveaxis(im, -1, 0).astype(np.float32))
    return tensor


class ToTensor(BasicTransform):
    def __init__(self, num_classes=1, sigmoid=True):
        super().__init__(always_apply=True, p=1.0)
        self.num_classes = num_classes
        self.sigmoid = sigmoid

    def __call__(self, **kwargs):
        kwargs.update({"image": img_to_tensor(kwargs["image"])})
        return kwargs


def _build_blurs() -> List[BasicTransform]:
    blurs = [
        Blur(blur_limit=5, p=1.0),
        MedianBlur(blur_limit=5, p=1.0),
        MotionBlur(blur_limit=5, p=1.0),
        GlassBlur(sigma=0.9, max_delta=2, iterations=1, p=1.0),
    ]
    return blurs


def get_transforms_train(image_size, p=0.8, **kwargs):
    augmentations = [
        # We apply all visual augmentations at first
        HueSaturationValue(p=0.3),
        RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, brightness_by_max=False, p=0.5),
        OneOf(_build_blurs(), p=0.2),
        ImageCompression(quality_lower=10, quality_upper=100, p=0.3),
        CLAHE(clip_limit=4.0, tile_grid_size=(8, 8), p=0.3),
        Rotate(limit=10, p=0.3),
        Resize(image_size[0], image_size[1], always_apply=True),
        CoarseDropout(max_holes=2, max_height=10, max_width=10),
        #ToTensor(),
    ]
    return Compose(augmentations, p=p, **kwargs)


def get_transforms_val(image_size, p=1, **kwargs):
    return Compose([Resize(image_size[0], image_size[1], always_apply=True), ToTensor()], p=p, **kwargs)


def get_transforms_simple(image_size, p=1, **kwargs):
    return Compose([Resize(image_size[0], image_size[1], always_apply=True), ToTensor()], p=p, **kwargs)
