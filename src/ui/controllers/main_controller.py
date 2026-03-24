"""Main controller coordinating GUI actions with backend modules."""

from __future__ import annotations

import logging
import os
import traceback
from pathlib import Path

import numpy as np
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from src.core.models import ProjectConfig
from src.core.project_manager import ProjectManager
from src.core.task_runner import TaskRunner, TaskWorker
from src.geometry.processor import GeometryProcessor, ProcessResult
from src.io.exporter import ExportManager
from src.io.image_loader import ImageLoader
from src.lbm.d2q9_solver import D2Q9BGKSolver
from src.lbm.interface import LBMRunResult
from src.lbm.permeability import estimate_permeability_lattice
from src.upscaling.interface import REVResult
from src.upscaling.rev_analyzer import REVAnalyzer
from src.visualization.plot_utils import rev_result_to_image


class MainController:
    """Workflow controller: project->geometry->simulation->REV->export."""

    def __init__(self, window: QMainWindow, logger: logging.Logger) -> None:
        self.window = window
        self.logger = logger

        self.project_manager = ProjectManager()
        self.task_runner = TaskRunner()
        self.image_loader = ImageLoader()
        self.geometry_processor = GeometryProcessor()
        self.solver = D2Q9BGKSolver()
        self.rev_analyzer = REVAnalyzer(self.solver)
        self.exporter = ExportManager()

        self.raw_image: np.ndarray | None = None
        self.preprocessed: ProcessResult | None = None
        self.lbm_result: LBMRunResult | None = None
        self.rev_result: REVResult | None = None

    def _log(self, level: str, text: str) -> None:
        getattr(self.logger, level if level in ("info", "warning", "error") else "info")(text)

    def new_project(self) -> None:
        folder = QFileDialog.getExistingDirectory(self.window, "选择项目目录")
        if not folder:
            return
        name = Path(folder).name
        project = self.project_manager.create_project(name, folder)
        self.window.parameter_panel.from_project_config(project)
        self.window.result_panel.update_summary(project.summary)
        self.window.app_status.update(project_name=project.project_name, state="idle", result="已新建项目")
        self._reset_results()
        self._log("info", f"新建项目成功: {project.project_name}")

    def open_project(self) -> None:
        fp, _ = QFileDialog.getOpenFileName(self.window, "打开项目", filter="Project (*.project.json)")
        if not fp:
            return
        try:
            project = self.project_manager.load_project(Path(fp))
            self.window.parameter_panel.from_project_config(project)
            self.window.result_panel.update_summary(project.summary)
            self.window.app_status.update(project_name=project.project_name, state="idle", result="项目打开成功")
            self._reset_results()
            self._log("info", f"打开项目: {fp}")
        except Exception as exc:
            self._handle_exception("打开项目失败", exc)

    def save_project(self) -> None:
        project = self._ensure_project_context()
        if project is None:
            return
        try:
            saved = self.project_manager.save_project()
            self.window.app_status.update(state="idle", result=f"项目已保存: {saved.name}")
            self._log("info", f"保存项目: {saved}")
        except Exception as exc:
            self._handle_exception("保存项目失败", exc)

    def import_image(self) -> None:
        project = self._ensure_project_context()
        if project is None:
            return

        fp, _ = QFileDialog.getOpenFileName(
            self.window,
            "导入二维图像",
            filter="Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)",
        )
        if not fp:
            return

        self.window.app_status.update(state="importing", result="正在导入图像")
        worker = TaskWorker("导图", self._load_image_task, Path(fp))
        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(lambda arr: self._on_image_loaded(fp, arr))
        worker.signals.error.connect(self._on_worker_error)
        self.task_runner.submit(worker)

    def preprocess_geometry(self) -> None:
        project = self._ensure_project_context()
        if project is None:
            return
        if self.raw_image is None:
            QMessageBox.warning(self.window, "未导入图像", "请先导入二维图像")
            return
        if not self.window.parameter_panel.show_validation_error():
            return

        self.window.parameter_panel.to_project_config(project)
        self.window.app_status.update(state="preprocessing", result="正在预处理")
        worker = TaskWorker("预处理", self._preprocess_task, self.raw_image, project.preprocess)
        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_preprocess_done)
        worker.signals.error.connect(self._on_worker_error)
        self.task_runner.submit(worker)

    def run_simulation(self) -> None:
        project = self._ensure_project_context()
        if project is None:
            return
        if self.preprocessed is None:
            QMessageBox.warning(self.window, "缺少二值结构", "请先执行几何预处理")
            return

        self.window.parameter_panel.to_project_config(project)
        self.window.app_status.update(state="running simulation", result="LBM运行中")
        worker = TaskWorker("LBM", self._simulate_task, self.preprocessed.binary, project.lbm)
        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_simulation_done)
        worker.signals.error.connect(self._on_worker_error)
        self.task_runner.submit(worker)

    def run_rev(self) -> None:
        project = self._ensure_project_context()
        if project is None:
            return
        if self.preprocessed is None:
            QMessageBox.warning(self.window, "缺少二值结构", "请先执行几何预处理")
            return

        self.window.parameter_panel.to_project_config(project)
        self.window.app_status.update(state="running REV", result="REV分析中")
        worker = TaskWorker("REV", self._rev_task, self.preprocessed.binary, project.rev, project.lbm)
        worker.signals.progress.connect(self._on_progress)
        worker.signals.finished.connect(self._on_rev_done)
        worker.signals.error.connect(self._on_worker_error)
        self.task_runner.submit(worker)

    def export_results(self) -> None:
        project = self._ensure_project_context()
        if project is None:
            return
        try:
            self.window.app_status.update(state="exporting", result="导出中")
            dirs = self.exporter.prepare_dirs(project.output_dir)

            if project.export.export_png:
                if self.raw_image is not None:
                    gray = self.geometry_processor.rgb_to_gray(self.raw_image)
                    self.exporter.export_png(dirs["figures"] / "raw.png", gray)
                if self.preprocessed is not None:
                    self.exporter.export_png(dirs["figures"] / "binary.png", self.preprocessed.binary * 255)
                if self.lbm_result is not None:
                    self.exporter.export_png(dirs["figures"] / "velocity.png", self.lbm_result.velocity_magnitude)
                if self.rev_result is not None:
                    self.exporter.export_png(dirs["figures"] / "rev.png", rev_result_to_image(self.rev_result))

            if project.export.export_csv and self.rev_result is not None:
                rows = [[r.window_size, r.mean_porosity, r.mean_permeability, r.std_permeability, r.valid_samples] for r in self.rev_result.records]
                self.exporter.export_csv(
                    dirs["tables"] / "rev_records.csv",
                    ["window_size", "mean_porosity", "mean_permeability", "std_permeability", "valid_samples"],
                    rows,
                )

            self.exporter.export_json(dirs["configs"] / f"{project.project_name}.json", project.to_dict())
            if project.export.export_report:
                self.exporter.export_report(dirs["reports"] / "summary_report.md", project, self.rev_result)

            self.window.app_status.update(state="idle", result="导出完成")
            self._log("info", f"导出完成: {project.output_dir}")
        except Exception as exc:
            self._handle_exception("导出失败", exc)

    def open_output_dir(self) -> None:
        project = self._ensure_project_context()
        if project is None:
            return
        out = project.output_dir
        out.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(out)  # type: ignore[attr-defined]
        else:
            QMessageBox.information(self.window, "输出目录", f"请手动打开: {out}")
        self._log("info", f"输出目录: {out}")

    def about(self) -> None:
        QMessageBox.information(self.window, "关于", "基于LBM的跨尺度多孔介质渗流模拟平台\nV1.0 (2D/单相/稳态)")

    def _ensure_project_context(self) -> ProjectConfig | None:
        project = self.project_manager.current_project
        if project is None:
            QMessageBox.warning(self.window, "无项目", "请先新建或打开项目")
            return None
        self.window.parameter_panel.to_project_config(project)
        return project

    def _load_image_task(self, file_path: Path, progress=None) -> np.ndarray:
        if progress:
            progress(1, 2, "读取图像")
        arr = self.image_loader.load(file_path)
        if progress:
            progress(2, 2, "读取完成")
        return arr

    def _preprocess_task(self, image: np.ndarray, preprocess_cfg, progress=None) -> ProcessResult:
        if progress:
            progress(1, 2, "预处理执行")
        result = self.geometry_processor.preprocess(image, preprocess_cfg)
        if progress:
            progress(2, 2, "预处理完成")
        return result

    def _simulate_task(self, binary: np.ndarray, lbm_cfg, progress=None) -> LBMRunResult:
        return self.solver.run(binary, lbm_cfg, progress=progress)

    def _rev_task(self, binary: np.ndarray, rev_cfg, lbm_cfg, progress=None) -> REVResult:
        return self.rev_analyzer.analyze(binary, rev_cfg, lbm_cfg, progress=progress)

    def _on_image_loaded(self, file_path: str, arr: np.ndarray) -> None:
        self.raw_image = arr
        project = self.project_manager.current_project
        if project is None:
            return
        gray = self.geometry_processor.rgb_to_gray(arr)
        project.geometry.input_file_path = file_path
        project.geometry.image_width = int(gray.shape[1])
        project.geometry.image_height = int(gray.shape[0])
        self.window.parameter_panel.from_project_config(project)
        self.window.central_tabs.raw_tab.show_array(gray, "原始结构")
        self.window.app_status.update(state="idle", result="图像导入成功")
        self._log("info", f"图像导入成功: {file_path}")

    def _on_preprocess_done(self, result: ProcessResult) -> None:
        self.preprocessed = result
        project = self.project_manager.current_project
        if project is None:
            return
        project.summary.porosity = result.stats.porosity
        project.summary.pore_pixels = result.stats.pore_pixels
        project.summary.solid_pixels = result.stats.solid_pixels
        project.geometry.image_width = result.stats.image_width
        project.geometry.image_height = result.stats.image_height
        project.summary.output_directory = str(project.output_dir)

        self.window.central_tabs.binary_tab.show_array(result.binary * 255, "二值结构")
        self.window.result_panel.update_summary(project.summary)
        self.window.central_tabs.set_text_summary(self._build_text_summary(project))
        self.window.app_status.update(state="idle", result="预处理完成")
        self._log("info", "预处理完成")

    def _on_simulation_done(self, result: LBMRunResult) -> None:
        self.lbm_result = result
        project = self.project_manager.current_project
        if project is None:
            return

        k = estimate_permeability_lattice(
            average_velocity=result.average_velocity,
            viscosity=(project.lbm.tau - 0.5) / 3.0,
            dp=(project.lbm.rho_in - project.lbm.rho_out),
            length=float(self.preprocessed.binary.shape[1] if self.preprocessed is not None else 1),
        )
        project.summary.average_velocity = result.average_velocity
        project.summary.permeability = k
        project.summary.convergence_status = result.convergence_status

        self.window.central_tabs.velocity_tab.show_array(result.velocity_magnitude, "速度模场")
        self.window.result_panel.update_summary(project.summary)
        self.window.central_tabs.set_text_summary(self._build_text_summary(project))
        self.window.app_status.update(state="idle", result=f"仿真完成: {result.convergence_status}")
        self._log("info", f"仿真完成: steps={result.steps}, status={result.convergence_status}")

    def _on_rev_done(self, result: REVResult) -> None:
        self.rev_result = result
        project = self.project_manager.current_project
        if project is None:
            return

        project.summary.rev_suggested_size = result.suggested_size
        self.window.result_panel.update_summary(project.summary)
        self.window.central_tabs.rev_tab.show_array(rev_result_to_image(result), "REV曲线")
        self.window.central_tabs.set_text_summary(self._build_text_summary(project))
        self.window.app_status.update(state="idle", result=f"REV完成: {result.note}")
        self._log("info", f"REV完成，建议尺寸={result.suggested_size}")

    def _on_progress(self, current: int, total: int, msg: str) -> None:
        self._log("info", f"[{current}/{total}] {msg}")

    def _on_worker_error(self, tb_text: str) -> None:
        self.logger.error(tb_text)
        self.window.app_status.update(state="idle", result="失败")
        QMessageBox.critical(self.window, "任务失败", tb_text)

    def _handle_exception(self, title: str, exc: Exception) -> None:
        details = f"{title}: {exc}\n{traceback.format_exc()}"
        self.logger.error(details)
        self.window.app_status.update(state="idle", result=title)
        QMessageBox.critical(self.window, title, details)

    def _build_text_summary(self, project: ProjectConfig) -> str:
        return (
            f"项目: {project.project_name}\n"
            f"输入文件: {project.geometry.input_file_path or 'N/A'}\n"
            f"图像尺寸: {project.geometry.image_width}x{project.geometry.image_height}\n"
            f"孔隙率: {project.summary.porosity}\n"
            f"平均速度: {project.summary.average_velocity}\n"
            f"渗透率: {project.summary.permeability}\n"
            f"收敛状态: {project.summary.convergence_status}\n"
            f"REV建议尺寸: {project.summary.rev_suggested_size}\n"
            f"输出目录: {project.output_dir}\n"
        )

    def _reset_results(self) -> None:
        self.raw_image = None
        self.preprocessed = None
        self.lbm_result = None
        self.rev_result = None
        self.window.central_tabs.set_text_summary("文本摘要（等待结果）")
