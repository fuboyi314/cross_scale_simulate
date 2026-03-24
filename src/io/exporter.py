"""Export outputs to figures/tables/configs/logs/reports."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import imageio.v3 as iio
import numpy as np

from src.core.models import ProjectConfig
from src.upscaling.interface import REVResult


class ExportManager:
    """Handle structured export for simulation projects."""

    def prepare_dirs(self, root: Path) -> dict[str, Path]:
        """Create output subdirectories and return map."""
        dirs = {
            "figures": root / "figures",
            "tables": root / "tables",
            "configs": root / "configs",
            "logs": root / "logs",
            "reports": root / "reports",
        }
        for p in dirs.values():
            p.mkdir(parents=True, exist_ok=True)
        return dirs

    def export_png(self, path: Path, image: np.ndarray) -> None:
        """Export ndarray as PNG image."""
        path.parent.mkdir(parents=True, exist_ok=True)
        iio.imwrite(path, image.astype(np.uint8))

    def export_csv(self, path: Path, headers: list[str], rows: list[list[float | int | str]]) -> None:
        """Export row data to CSV."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

    def export_json(self, path: Path, payload: dict) -> None:
        """Export payload to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def export_report(self, path: Path, project: ProjectConfig, rev_result: REVResult | None) -> None:
        """Export markdown summary report."""
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# 项目摘要报告 - {project.project_name}",
            "",
            "## 输入信息",
            f"- 输入文件: {project.geometry.input_file_path or 'N/A'}",
            f"- 图像尺寸: {project.geometry.image_width} x {project.geometry.image_height}",
            "",
            "## 预处理参数",
            f"- threshold: {project.preprocess.threshold}",
            f"- invert_binary: {project.preprocess.invert_binary}",
            f"- min_component_size: {project.preprocess.min_component_size}",
            f"- fill_small_holes: {project.preprocess.fill_small_holes}",
            "",
            "## 统计与仿真结果",
            f"- porosity: {project.summary.porosity}",
            f"- average_velocity: {project.summary.average_velocity}",
            f"- permeability: {project.summary.permeability}",
            f"- convergence_status: {project.summary.convergence_status}",
            "",
            "## REV 摘要",
            f"- rev_suggested_size: {project.summary.rev_suggested_size}",
            f"- rev_note: {rev_result.note if rev_result else 'N/A'}",
            "",
            "## 输出路径",
            f"- output_root: {project.output_dir}",
        ]
        path.write_text("\n".join(lines), encoding="utf-8")
