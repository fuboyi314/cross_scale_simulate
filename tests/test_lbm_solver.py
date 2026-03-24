import numpy as np

from src.core.models import LBMConfig
from src.lbm.d2q9_solver import D2Q9BGKSolver


def test_channel_flow_basic() -> None:
    geom = np.ones((20, 40), dtype=np.uint8)
    cfg = LBMConfig(max_steps=120, convergence_tol=1e-5)
    res = D2Q9BGKSolver().run(geom, cfg)
    assert res.velocity_magnitude.shape == geom.shape
    assert res.average_velocity >= 0.0


def test_solid_obstacle_basic() -> None:
    geom = np.ones((24, 40), dtype=np.uint8)
    geom[:, 20] = 0
    cfg = LBMConfig(max_steps=80, convergence_tol=1e-5)
    res = D2Q9BGKSolver().run(geom, cfg)
    assert res.ux.shape == geom.shape
    assert res.uy.shape == geom.shape


def test_output_shape_consistency() -> None:
    geom = np.ones((12, 16), dtype=np.uint8)
    cfg = LBMConfig(max_steps=40)
    res = D2Q9BGKSolver().run(geom, cfg)
    assert res.density.shape == geom.shape
    assert len(res.convergence_history) == res.steps
