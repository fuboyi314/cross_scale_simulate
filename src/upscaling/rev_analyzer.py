"""REV analyzer for permeability-vs-window-size analysis."""

from __future__ import annotations

import random

import numpy as np

from src.core.models import LBMConfig, REVConfig
from src.lbm.interface import LBMSolver
from src.lbm.permeability import estimate_permeability_lattice
from src.upscaling.interface import REVRecord, REVResult


class REVAnalyzer:
    """Perform multi-window REV sampling using solver callback."""

    def __init__(self, solver: LBMSolver) -> None:
        self.solver = solver

    def analyze(self, binary_geometry: np.ndarray, rev_cfg: REVConfig, lbm_cfg: LBMConfig, progress=None) -> REVResult:
        """Run REV sampling and return fluctuation statistics."""
        h, w = binary_geometry.shape
        max_win = min(rev_cfg.max_window_size, h, w)
        if max_win < rev_cfg.min_window_size:
            return REVResult(records=[], suggested_size=None, note="window size invalid")

        sizes = np.linspace(rev_cfg.min_window_size, max_win, rev_cfg.num_window_sizes).astype(int)
        sizes = sorted(set(int(s) for s in sizes))

        records: list[REVRecord] = []
        total = max(1, len(sizes))
        for idx, win in enumerate(sizes, start=1):
            perms: list[float] = []
            pors: list[float] = []
            for _ in range(rev_cfg.samples_per_size):
                y = random.randint(0, h - win)
                x = random.randint(0, w - win)
                sub = binary_geometry[y : y + win, x : x + win]
                por = float(np.mean(sub))
                pors.append(por)
                if por < 0.05:
                    continue
                sim = self.solver.run(sub, lbm_cfg)
                try:
                    k = estimate_permeability_lattice(
                        sim.average_velocity,
                        viscosity=(lbm_cfg.tau - 0.5) / 3.0,
                        dp=(lbm_cfg.rho_in - lbm_cfg.rho_out),
                        length=float(win),
                    )
                except ValueError:
                    k = 0.0
                perms.append(float(k))

            mean_k = float(np.mean(perms)) if perms else 0.0
            std_k = float(np.std(perms)) if perms else 0.0
            mean_por = float(np.mean(pors)) if pors else 0.0
            records.append(
                REVRecord(
                    window_size=win,
                    mean_porosity=mean_por,
                    mean_permeability=mean_k,
                    std_permeability=std_k,
                    valid_samples=len(perms),
                )
            )
            if progress:
                progress(idx, total, f"REV size {win} done ({idx}/{total})")

        suggested = self._suggest_rev(records)
        note = "ok" if records else "no records"
        return REVResult(records=records, suggested_size=suggested, note=note)

    def _suggest_rev(self, records: list[REVRecord]) -> int | None:
        """Rule-based suggested REV size by relative fluctuation threshold."""
        for r in records:
            if abs(r.mean_permeability) < 1e-12:
                continue
            rel = abs(r.std_permeability / r.mean_permeability)
            if rel < 0.1:
                return r.window_size
        return records[-1].window_size if records else None
