"""D2Q9 BGK/SRT solver for 2D single-phase steady incompressible-like flow."""

from __future__ import annotations

import numpy as np

from src.core.models import LBMConfig
from src.lbm.interface import LBMRunResult


class D2Q9BGKSolver:
    """Basic D2Q9 BGK solver with bounce-back solid boundary and left-right pressure drive."""

    c = np.array([[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]])
    w = np.array([4 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 36, 1 / 36, 1 / 36, 1 / 36])
    opp = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6])

    def run(self, binary_geometry: np.ndarray, cfg: LBMConfig, progress=None) -> LBMRunResult:
        """Run D2Q9 BGK iteration.

        Args:
            binary_geometry: 2D matrix (1 pore, 0 solid)
            cfg: simulation config
            progress: callback(current, total, msg)
        """
        pore = (binary_geometry == 1)
        solid = ~pore
        ny, nx = binary_geometry.shape

        rho = np.ones((ny, nx), dtype=np.float64)
        ux = np.zeros((ny, nx), dtype=np.float64)
        uy = np.zeros((ny, nx), dtype=np.float64)

        f = np.zeros((9, ny, nx), dtype=np.float64)
        for i in range(9):
            f[i] = self.w[i] * rho

        residual_hist: list[float] = []
        prev_avg = 0.0
        status = "max_steps reached"

        for step in range(1, cfg.max_steps + 1):
            rho = np.sum(f, axis=0)
            ux = np.sum(f * self.c[:, 0, None, None], axis=0) / np.maximum(rho, 1e-12)
            uy = np.sum(f * self.c[:, 1, None, None], axis=0) / np.maximum(rho, 1e-12)
            ux[solid] = 0.0
            uy[solid] = 0.0

            rho[:, 0] = cfg.rho_in
            rho[:, -1] = cfg.rho_out

            usq = ux**2 + uy**2
            feq = np.zeros_like(f)
            for i in range(9):
                cu = 3.0 * (self.c[i, 0] * ux + self.c[i, 1] * uy)
                feq[i] = self.w[i] * rho * (1 + cu + 0.5 * cu**2 - 1.5 * usq)

            f = f - (f - feq) / cfg.tau

            for i in range(9):
                f[i, solid] = f[self.opp[i], solid]

            for i in range(9):
                f[i] = np.roll(np.roll(f[i], self.c[i, 0], axis=1), self.c[i, 1], axis=0)

            avg_u = float(np.mean(np.sqrt(ux[pore] ** 2 + uy[pore] ** 2))) if np.any(pore) else 0.0
            residual = abs(avg_u - prev_avg)
            residual_hist.append(residual)
            prev_avg = avg_u

            if progress and (step == 1 or step % 50 == 0 or step == cfg.max_steps):
                progress(step, cfg.max_steps, f"LBM step={step}/{cfg.max_steps}, residual={residual:.3e}")

            if step > 60 and residual < cfg.convergence_tol:
                status = "converged"
                break

        vel_mag = np.sqrt(ux**2 + uy**2)
        steps = len(residual_hist)
        avg_velocity = float(np.mean(vel_mag[pore])) if np.any(pore) else 0.0
        return LBMRunResult(
            density=rho,
            ux=ux,
            uy=uy,
            velocity_magnitude=vel_mag,
            average_velocity=avg_velocity,
            convergence_history=residual_hist,
            convergence_status=status,
            steps=steps,
        )
