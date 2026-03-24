"""LBM solver protocol and result dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from src.core.models import LBMConfig


@dataclass(slots=True)
class LBMRunResult:
    """Result fields from D2Q9 BGK solver."""

    density: np.ndarray
    ux: np.ndarray
    uy: np.ndarray
    velocity_magnitude: np.ndarray
    average_velocity: float
    convergence_history: list[float]
    convergence_status: str
    steps: int


class LBMSolver(Protocol):
    """Protocol for LBM solver implementations."""

    def run(self, binary_geometry: np.ndarray, cfg: LBMConfig, progress=None) -> LBMRunResult:
        ...
