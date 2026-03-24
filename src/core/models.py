"""Dataclasses for project, preprocessing, simulation, REV and export configurations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class PreprocessConfig:
    """Image preprocessing options for 2D porous media."""

    threshold: int = 128
    invert_binary: bool = False
    min_component_size: int = 0
    fill_small_holes: bool = False
    roi_xmin: int = 0
    roi_xmax: int = 0
    roi_ymin: int = 0
    roi_ymax: int = 0


@dataclass(slots=True)
class LBMConfig:
    """D2Q9 BGK/SRT simulation configuration."""

    tau: float = 0.8
    rho_in: float = 1.01
    rho_out: float = 1.0
    max_steps: int = 3000
    convergence_tol: float = 1e-6
    save_interval: int = 100


@dataclass(slots=True)
class REVConfig:
    """REV window sampling configuration."""

    min_window_size: int = 20
    max_window_size: int = 120
    num_window_sizes: int = 6
    samples_per_size: int = 10


@dataclass(slots=True)
class ExportConfig:
    """Export options for outputs and reports."""

    export_directory: str = ""
    figure_dpi: int = 220
    export_csv: bool = True
    export_png: bool = True
    export_report: bool = True


@dataclass(slots=True)
class GeometryMeta:
    """Geometry source metadata."""

    input_file_path: str = ""
    image_width: int = 0
    image_height: int = 0


@dataclass(slots=True)
class ResultSummary:
    """Summary values displayed in right panel."""

    porosity: float | None = None
    pore_pixels: int | None = None
    solid_pixels: int | None = None
    average_velocity: float | None = None
    permeability: float | None = None
    convergence_status: str = "N/A"
    rev_suggested_size: int | None = None
    output_directory: str = ""


@dataclass(slots=True)
class ProjectConfig:
    """Serializable project aggregate config."""

    project_name: str
    working_directory: str
    geometry: GeometryMeta = field(default_factory=GeometryMeta)
    preprocess: PreprocessConfig = field(default_factory=PreprocessConfig)
    lbm: LBMConfig = field(default_factory=LBMConfig)
    rev: REVConfig = field(default_factory=REVConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    summary: ResultSummary = field(default_factory=ResultSummary)

    def to_dict(self) -> dict[str, Any]:
        """Convert config to JSON-compatible dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectConfig":
        """Build project config from plain dictionary."""
        return cls(
            project_name=data["project_name"],
            working_directory=data["working_directory"],
            geometry=GeometryMeta(**data.get("geometry", {})),
            preprocess=PreprocessConfig(**data.get("preprocess", {})),
            lbm=LBMConfig(**data.get("lbm", {})),
            rev=REVConfig(**data.get("rev", {})),
            export=ExportConfig(**data.get("export", {})),
            summary=ResultSummary(**data.get("summary", {})),
        )

    @property
    def project_file(self) -> Path:
        """Default project file path."""
        return Path(self.working_directory) / f"{self.project_name}.project.json"

    @property
    def output_dir(self) -> Path:
        """Output root directory."""
        if self.export.export_directory:
            return Path(self.export.export_directory)
        return Path(self.working_directory) / "outputs"
