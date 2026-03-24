"""Geometry preprocessing for porous-media image -> binary pore/solid matrix."""

from __future__ import annotations

from dataclasses import dataclass
from collections import deque

import numpy as np

from src.core.models import PreprocessConfig


@dataclass(slots=True)
class GeometryStats:
    """Geometric statistics used by GUI summary."""

    porosity: float
    pore_pixels: int
    solid_pixels: int
    image_width: int
    image_height: int


@dataclass(slots=True)
class ProcessResult:
    """Preprocessing output bundle."""

    gray: np.ndarray
    binary: np.ndarray
    stats: GeometryStats


class GeometryProcessor:
    """2D preprocessing pipeline with ROI, threshold, denoise and hole-fill."""

    def rgb_to_gray(self, image: np.ndarray) -> np.ndarray:
        """Convert input image to 2D grayscale uint8."""
        if image.ndim == 2:
            return image.astype(np.uint8)
        if image.ndim == 3 and image.shape[2] >= 3:
            gray = 0.299 * image[..., 0] + 0.587 * image[..., 1] + 0.114 * image[..., 2]
            return gray.astype(np.uint8)
        raise ValueError("Unsupported image dimensions")

    def apply_roi(self, gray: np.ndarray, cfg: PreprocessConfig) -> np.ndarray:
        """Crop by ROI. If max values are 0, use full size."""
        h, w = gray.shape
        x0 = max(0, min(cfg.roi_xmin, w - 1))
        y0 = max(0, min(cfg.roi_ymin, h - 1))
        x1 = cfg.roi_xmax if cfg.roi_xmax > 0 else w
        y1 = cfg.roi_ymax if cfg.roi_ymax > 0 else h
        x1 = max(x0 + 1, min(x1, w))
        y1 = max(y0 + 1, min(y1, h))
        return gray[y0:y1, x0:x1]

    def threshold_binarize(self, gray: np.ndarray, threshold: int, invert_binary: bool = False) -> np.ndarray:
        """Threshold grayscale image to pore(1) / solid(0)."""
        binary = (gray >= threshold).astype(np.uint8)
        return (1 - binary) if invert_binary else binary

    def remove_small_pore_components(self, binary: np.ndarray, min_size: int) -> np.ndarray:
        """Remove connected pore components smaller than `min_size` (4-neighbor)."""
        if min_size <= 1:
            return binary
        h, w = binary.shape
        visited = np.zeros_like(binary, dtype=bool)
        out = binary.copy()
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for y in range(h):
            for x in range(w):
                if visited[y, x] or binary[y, x] == 0:
                    continue
                q = deque([(y, x)])
                visited[y, x] = True
                comp: list[tuple[int, int]] = []
                while q:
                    cy, cx = q.popleft()
                    comp.append((cy, cx))
                    for dy, dx in dirs:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and binary[ny, nx] == 1:
                            visited[ny, nx] = True
                            q.append((ny, nx))
                if len(comp) < min_size:
                    for cy, cx in comp:
                        out[cy, cx] = 0
        return out

    def fill_small_solid_holes(self, binary: np.ndarray, max_hole_size: int = 64) -> np.ndarray:
        """Fill enclosed solid holes within pore regions up to `max_hole_size`."""
        h, w = binary.shape
        solid = (binary == 0).astype(np.uint8)
        visited = np.zeros_like(solid, dtype=bool)
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        out = binary.copy()

        for y in range(h):
            for x in range(w):
                if visited[y, x] or solid[y, x] == 0:
                    continue
                q = deque([(y, x)])
                visited[y, x] = True
                comp: list[tuple[int, int]] = []
                touches_boundary = False
                while q:
                    cy, cx = q.popleft()
                    comp.append((cy, cx))
                    if cy in (0, h - 1) or cx in (0, w - 1):
                        touches_boundary = True
                    for dy, dx in dirs:
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and solid[ny, nx] == 1:
                            visited[ny, nx] = True
                            q.append((ny, nx))
                if (not touches_boundary) and len(comp) <= max_hole_size:
                    for cy, cx in comp:
                        out[cy, cx] = 1
        return out

    def calc_stats(self, binary: np.ndarray) -> GeometryStats:
        """Compute porosity, pore/solid counts and image dimensions."""
        pore_pixels = int(np.sum(binary == 1))
        total = int(binary.size)
        solid_pixels = total - pore_pixels
        h, w = binary.shape
        porosity = float(pore_pixels / total) if total > 0 else 0.0
        return GeometryStats(
            porosity=porosity,
            pore_pixels=pore_pixels,
            solid_pixels=solid_pixels,
            image_width=w,
            image_height=h,
        )

    def preprocess(self, image: np.ndarray, cfg: PreprocessConfig) -> ProcessResult:
        """Full preprocessing chain required by milestone M2."""
        gray = self.rgb_to_gray(image)
        roi_gray = self.apply_roi(gray, cfg)
        binary = self.threshold_binarize(roi_gray, cfg.threshold, cfg.invert_binary)
        binary = self.remove_small_pore_components(binary, cfg.min_component_size)
        if cfg.fill_small_holes:
            binary = self.fill_small_solid_holes(binary)
        stats = self.calc_stats(binary)
        return ProcessResult(gray=roi_gray, binary=binary, stats=stats)
