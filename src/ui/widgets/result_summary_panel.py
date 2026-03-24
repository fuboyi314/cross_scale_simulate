"""Right-side summary panel for key scientific indicators."""

from __future__ import annotations

from dataclasses import asdict

from PySide6.QtWidgets import QFormLayout, QLabel, QWidget

from src.core.models import ResultSummary


class ResultSummaryPanel(QWidget):
    """Display and update result summary fields."""

    def __init__(self) -> None:
        super().__init__()
        self._labels: dict[str, QLabel] = {}
        layout = QFormLayout(self)

        for key in [
            "porosity",
            "pore_pixels",
            "solid_pixels",
            "average_velocity",
            "permeability",
            "convergence_status",
            "rev_suggested_size",
            "output_directory",
        ]:
            label = QLabel("N/A")
            label.setWordWrap(True)
            self._labels[key] = label
            layout.addRow(key, label)

    def update_summary(self, summary: ResultSummary) -> None:
        """Apply `ResultSummary` object values to panel."""
        for key, value in asdict(summary).items():
            self._labels[key].setText("N/A" if value is None else str(value))
