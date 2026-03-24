import numpy as np

from src.core.models import LBMConfig, REVConfig
from src.lbm.d2q9_solver import D2Q9BGKSolver
from src.upscaling.rev_analyzer import REVAnalyzer


def test_rev_sampling_runs() -> None:
    geom = np.ones((40, 40), dtype=np.uint8)
    rev_cfg = REVConfig(min_window_size=10, max_window_size=20, num_window_sizes=3, samples_per_size=2)
    lbm_cfg = LBMConfig(max_steps=30)
    result = REVAnalyzer(D2Q9BGKSolver()).analyze(geom, rev_cfg, lbm_cfg)
    assert len(result.records) == 3


def test_rev_result_dimensions() -> None:
    geom = np.ones((30, 30), dtype=np.uint8)
    rev_cfg = REVConfig(min_window_size=8, max_window_size=16, num_window_sizes=2, samples_per_size=2)
    lbm_cfg = LBMConfig(max_steps=20)
    result = REVAnalyzer(D2Q9BGKSolver()).analyze(geom, rev_cfg, lbm_cfg)
    assert all(r.valid_samples >= 0 for r in result.records)
    assert result.suggested_size is not None
