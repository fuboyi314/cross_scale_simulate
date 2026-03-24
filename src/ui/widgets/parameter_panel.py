"""Left-side parameter panel with grouped configuration widgets."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from src.core.models import ExportConfig, GeometryMeta, LBMConfig, PreprocessConfig, ProjectConfig, REVConfig


@dataclass(slots=True)
class ValidationResult:
    ok: bool
    message: str = ""


class ParameterPanel(QWidget):
    """Structured parameter editor with read/write validation support."""

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)

        # project
        g_project = QGroupBox("项目信息")
        f_project = QFormLayout(g_project)
        self.project_name = QLineEdit()
        self.working_directory = QLineEdit()
        f_project.addRow("project_name", self.project_name)
        f_project.addRow("working_directory", self.working_directory)

        # geometry
        g_geo = QGroupBox("几何导入")
        f_geo = QFormLayout(g_geo)
        self.input_file_path = QLineEdit()
        self.image_width = QSpinBox(); self.image_width.setRange(0, 100000)
        self.image_height = QSpinBox(); self.image_height.setRange(0, 100000)
        f_geo.addRow("input_file_path", self.input_file_path)
        f_geo.addRow("image_width", self.image_width)
        f_geo.addRow("image_height", self.image_height)

        # preprocess
        g_pre = QGroupBox("预处理参数")
        f_pre = QFormLayout(g_pre)
        self.threshold = QSpinBox(); self.threshold.setRange(0, 255); self.threshold.setValue(128)
        self.invert_binary = QCheckBox()
        self.min_component_size = QSpinBox(); self.min_component_size.setRange(0, 10_000_000)
        self.fill_small_holes = QCheckBox()
        self.roi_xmin = QSpinBox(); self.roi_xmin.setRange(0, 100000)
        self.roi_xmax = QSpinBox(); self.roi_xmax.setRange(0, 100000)
        self.roi_ymin = QSpinBox(); self.roi_ymin.setRange(0, 100000)
        self.roi_ymax = QSpinBox(); self.roi_ymax.setRange(0, 100000)
        f_pre.addRow("threshold", self.threshold)
        f_pre.addRow("invert_binary", self.invert_binary)
        f_pre.addRow("min_component_size", self.min_component_size)
        f_pre.addRow("fill_small_holes", self.fill_small_holes)
        f_pre.addRow("roi_xmin", self.roi_xmin)
        f_pre.addRow("roi_xmax", self.roi_xmax)
        f_pre.addRow("roi_ymin", self.roi_ymin)
        f_pre.addRow("roi_ymax", self.roi_ymax)

        # lbm
        g_lbm = QGroupBox("LBM参数")
        f_lbm = QFormLayout(g_lbm)
        self.tau = QDoubleSpinBox(); self.tau.setRange(0.51, 5.0); self.tau.setValue(0.8)
        self.rho_in = QDoubleSpinBox(); self.rho_in.setRange(0.9, 2.0); self.rho_in.setDecimals(5); self.rho_in.setValue(1.01)
        self.rho_out = QDoubleSpinBox(); self.rho_out.setRange(0.9, 2.0); self.rho_out.setDecimals(5); self.rho_out.setValue(1.0)
        self.max_steps = QSpinBox(); self.max_steps.setRange(1, 50_000_000); self.max_steps.setValue(5000)
        self.convergence_tol = QDoubleSpinBox(); self.convergence_tol.setDecimals(8); self.convergence_tol.setRange(1e-8, 1e-2); self.convergence_tol.setValue(1e-6)
        self.save_interval = QSpinBox(); self.save_interval.setRange(1, 1_000_000); self.save_interval.setValue(200)
        f_lbm.addRow("tau", self.tau)
        f_lbm.addRow("rho_in", self.rho_in)
        f_lbm.addRow("rho_out", self.rho_out)
        f_lbm.addRow("max_steps", self.max_steps)
        f_lbm.addRow("convergence_tol", self.convergence_tol)
        f_lbm.addRow("save_interval", self.save_interval)

        # rev
        g_rev = QGroupBox("REV分析参数")
        f_rev = QFormLayout(g_rev)
        self.min_window_size = QSpinBox(); self.min_window_size.setRange(1, 100000); self.min_window_size.setValue(20)
        self.max_window_size = QSpinBox(); self.max_window_size.setRange(1, 100000); self.max_window_size.setValue(120)
        self.num_window_sizes = QSpinBox(); self.num_window_sizes.setRange(1, 10000); self.num_window_sizes.setValue(6)
        self.samples_per_size = QSpinBox(); self.samples_per_size.setRange(1, 10000); self.samples_per_size.setValue(20)
        f_rev.addRow("min_window_size", self.min_window_size)
        f_rev.addRow("max_window_size", self.max_window_size)
        f_rev.addRow("num_window_sizes", self.num_window_sizes)
        f_rev.addRow("samples_per_size", self.samples_per_size)

        # export
        g_export = QGroupBox("导出选项")
        f_export = QFormLayout(g_export)
        self.export_directory = QLineEdit()
        self.figure_dpi = QSpinBox(); self.figure_dpi.setRange(72, 1200); self.figure_dpi.setValue(200)
        self.export_csv = QCheckBox(); self.export_csv.setChecked(True)
        self.export_png = QCheckBox(); self.export_png.setChecked(True)
        self.export_report = QCheckBox(); self.export_report.setChecked(True)
        f_export.addRow("export_directory", self.export_directory)
        f_export.addRow("figure_dpi", self.figure_dpi)
        f_export.addRow("export_csv", self.export_csv)
        f_export.addRow("export_png", self.export_png)
        f_export.addRow("export_report", self.export_report)

        for g in [g_project, g_geo, g_pre, g_lbm, g_rev, g_export]:
            root.addWidget(g)
        root.addStretch(1)

    def validate(self) -> ValidationResult:
        """Validate current form content before execution."""
        if not self.project_name.text().strip():
            return ValidationResult(False, "project_name 不能为空")
        if not self.working_directory.text().strip():
            return ValidationResult(False, "working_directory 不能为空")
        if self.roi_xmax.value() and self.roi_xmax.value() < self.roi_xmin.value():
            return ValidationResult(False, "roi_xmax 必须 >= roi_xmin")
        if self.roi_ymax.value() and self.roi_ymax.value() < self.roi_ymin.value():
            return ValidationResult(False, "roi_ymax 必须 >= roi_ymin")
        if self.max_window_size.value() < self.min_window_size.value():
            return ValidationResult(False, "max_window_size 必须 >= min_window_size")
        return ValidationResult(True)

    def show_validation_error(self) -> bool:
        """Show validation errors with message box. Returns whether valid."""
        result = self.validate()
        if not result.ok:
            QMessageBox.warning(self, "参数校验失败", result.message)
            return False
        return True

    def to_project_config(self, base: ProjectConfig) -> ProjectConfig:
        """Write panel values into existing project config."""
        base.project_name = self.project_name.text().strip()
        base.working_directory = self.working_directory.text().strip()

        base.geometry = GeometryMeta(
            input_file_path=self.input_file_path.text().strip(),
            image_width=self.image_width.value(),
            image_height=self.image_height.value(),
        )
        base.preprocess = PreprocessConfig(
            threshold=self.threshold.value(),
            invert_binary=self.invert_binary.isChecked(),
            min_component_size=self.min_component_size.value(),
            fill_small_holes=self.fill_small_holes.isChecked(),
            roi_xmin=self.roi_xmin.value(),
            roi_xmax=self.roi_xmax.value(),
            roi_ymin=self.roi_ymin.value(),
            roi_ymax=self.roi_ymax.value(),
        )
        base.lbm = LBMConfig(
            tau=self.tau.value(),
            rho_in=self.rho_in.value(),
            rho_out=self.rho_out.value(),
            max_steps=self.max_steps.value(),
            convergence_tol=self.convergence_tol.value(),
            save_interval=self.save_interval.value(),
        )
        base.rev = REVConfig(
            min_window_size=self.min_window_size.value(),
            max_window_size=self.max_window_size.value(),
            num_window_sizes=self.num_window_sizes.value(),
            samples_per_size=self.samples_per_size.value(),
        )
        base.export = ExportConfig(
            export_directory=self.export_directory.text().strip(),
            figure_dpi=self.figure_dpi.value(),
            export_csv=self.export_csv.isChecked(),
            export_png=self.export_png.isChecked(),
            export_report=self.export_report.isChecked(),
        )
        return base

    def from_project_config(self, cfg: ProjectConfig) -> None:
        """Fill panel widgets from project config."""
        self.project_name.setText(cfg.project_name)
        self.working_directory.setText(cfg.working_directory)

        self.input_file_path.setText(cfg.geometry.input_file_path)
        self.image_width.setValue(cfg.geometry.image_width)
        self.image_height.setValue(cfg.geometry.image_height)

        self.threshold.setValue(cfg.preprocess.threshold)
        self.invert_binary.setChecked(cfg.preprocess.invert_binary)
        self.min_component_size.setValue(cfg.preprocess.min_component_size)
        self.fill_small_holes.setChecked(cfg.preprocess.fill_small_holes)
        self.roi_xmin.setValue(cfg.preprocess.roi_xmin)
        self.roi_xmax.setValue(cfg.preprocess.roi_xmax)
        self.roi_ymin.setValue(cfg.preprocess.roi_ymin)
        self.roi_ymax.setValue(cfg.preprocess.roi_ymax)

        self.tau.setValue(cfg.lbm.tau)
        self.rho_in.setValue(cfg.lbm.rho_in)
        self.rho_out.setValue(cfg.lbm.rho_out)
        self.max_steps.setValue(cfg.lbm.max_steps)
        self.convergence_tol.setValue(cfg.lbm.convergence_tol)
        self.save_interval.setValue(cfg.lbm.save_interval)

        self.min_window_size.setValue(cfg.rev.min_window_size)
        self.max_window_size.setValue(cfg.rev.max_window_size)
        self.num_window_sizes.setValue(cfg.rev.num_window_sizes)
        self.samples_per_size.setValue(cfg.rev.samples_per_size)

        self.export_directory.setText(cfg.export.export_directory)
        self.figure_dpi.setValue(cfg.export.figure_dpi)
        self.export_csv.setChecked(cfg.export.export_csv)
        self.export_png.setChecked(cfg.export.export_png)
        self.export_report.setChecked(cfg.export.export_report)
