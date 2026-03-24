"""Image loader utilities for 2D porous-media images."""

from __future__ import annotations

from pathlib import Path

import imageio.v3 as iio
import numpy as np


class ImageLoader:
    """Load common 2D image formats and normalize channels."""

    SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

    def load(self, file_path: Path) -> np.ndarray:
        """Load image as numpy array (H,W) grayscale or (H,W,C) color."""
        if file_path.suffix.lower() not in self.SUPPORTED_SUFFIXES:
            raise ValueError(f"Unsupported image format: {file_path.suffix}")
        arr = iio.imread(file_path)
        if arr.ndim == 2:
            return arr.astype(np.uint8)
        if arr.ndim == 3 and arr.shape[2] in (3, 4):
            return arr[..., :3].astype(np.uint8)
        raise ValueError(f"Unsupported image shape: {arr.shape}")
