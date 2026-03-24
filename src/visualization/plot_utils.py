"""Matplotlib helpers to render arrays for Qt display."""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.upscaling.interface import REVResult


def rev_result_to_image(result: REVResult, dpi: int = 140) -> np.ndarray:
    """Render REV curves (mean permeability and relative fluctuation) to grayscale image."""
    if not result.records:
        return np.zeros((240, 360), dtype=np.uint8)

    x = [r.window_size for r in result.records]
    yk = [r.mean_permeability for r in result.records]
    yr = [abs(r.std_permeability / r.mean_permeability) if abs(r.mean_permeability) > 1e-12 else 0.0 for r in result.records]

    fig, ax = plt.subplots(1, 2, figsize=(8, 3.2), dpi=dpi)
    ax[0].plot(x, yk, marker="o")
    ax[0].set_title("k vs window")
    ax[0].set_xlabel("window")
    ax[0].set_ylabel("k")

    ax[1].plot(x, yr, marker="s", color="tab:orange")
    ax[1].set_title("relative fluctuation")
    ax[1].set_xlabel("window")
    ax[1].set_ylabel("std/mean")

    fig.tight_layout()
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)

    gray = (0.299 * rgba[..., 0] + 0.587 * rgba[..., 1] + 0.114 * rgba[..., 2]).astype(np.uint8)
    return gray
