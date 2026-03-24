"""REV analysis interfaces and result models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class REVRecord:
    window_size: int
    mean_porosity: float
    mean_permeability: float
    std_permeability: float
    valid_samples: int


@dataclass(slots=True)
class REVResult:
    records: list[REVRecord]
    suggested_size: int | None
    note: str
