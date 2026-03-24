import numpy as np

from src.core.models import PreprocessConfig
from src.geometry.processor import GeometryProcessor


def test_threshold_segmentation_and_porosity() -> None:
    image = np.array([[0, 200], [255, 100]], dtype=np.uint8)
    cfg = PreprocessConfig(threshold=128)
    result = GeometryProcessor().preprocess(image, cfg)
    assert result.binary.tolist() == [[0, 1], [1, 0]]
    assert result.stats.porosity == 0.5


def test_binary_value_range() -> None:
    image = np.array([[10, 20], [30, 250]], dtype=np.uint8)
    cfg = PreprocessConfig(threshold=25)
    result = GeometryProcessor().preprocess(image, cfg)
    assert set(np.unique(result.binary).tolist()).issubset({0, 1})


def test_roi_crop() -> None:
    image = np.arange(25, dtype=np.uint8).reshape(5, 5)
    cfg = PreprocessConfig(threshold=0, roi_xmin=1, roi_xmax=4, roi_ymin=1, roi_ymax=3)
    result = GeometryProcessor().preprocess(image, cfg)
    assert result.gray.shape == (2, 3)
