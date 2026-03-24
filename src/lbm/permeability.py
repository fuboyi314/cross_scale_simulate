"""Permeability estimation utilities."""

from __future__ import annotations


def estimate_permeability_lattice(average_velocity: float, viscosity: float, dp: float, length: float) -> float:
    """Estimate permeability in lattice units.

    Darcy-like relation (lattice-unit form):
        k = u * mu * L / Δp

    Assumptions:
        - Steady single-phase flow
        - Incompressible approximation
        - Pressure driving represented by density difference proxy
    """
    if abs(dp) < 1e-14:
        raise ValueError("dp must be non-zero")
    return average_velocity * viscosity * length / dp


def lattice_to_physical_interface(k_lattice: float, scale_factor: float | None = None) -> float | None:
    """Physical conversion interface placeholder.

    Returns:
        If `scale_factor` provided, return scaled permeability.
        Otherwise return None to indicate physical conversion not yet defined.
    """
    if scale_factor is None:
        return None
    return k_lattice * scale_factor
