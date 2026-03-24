"""Main application window for scientific workflow."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDockWidget, QMainWindow, QSplitter

from src.core.logging_service import GuiLogEmitter, QtSignalHandler
from src.ui.controllers.main_controller import MainController
from src.ui.widgets.log_panel import LogPanel
from src.ui.widgets.parameter_panel import ParameterPanel
from src.ui.widgets.result_summary_panel import ResultSummaryPanel
from src.ui.widgets.status_bar import AppStatus
from src.visualization.canvas import CentralTabs


class MainWindow(QMainWindow):
    """Top-level window composing all major panels and actions."""

    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self.logger = logger

        self.setWindowTitle("基于LBM的跨尺度多孔介质渗流模拟平台 - V1 第一轮")
        self.resize(1600, 920)

        self.parameter_panel = ParameterPanel()
        self.central_tabs = CentralTabs()
        self.result_panel = ResultSummaryPanel()
        self.log_panel = LogPanel()

        self._build_layout()
        self._build_actions_menu_toolbar()

        self.app_status = AppStatus(self.statusBar())
        self.app_status.update()

        self._bind_logger_to_gui()
        self.controller = MainController(self, self.logger)
        self._connect_actions()

    def _build_layout(self) -> None:
        split = QSplitter(Qt.Orientation.Horizontal)
        split.addWidget(self.parameter_panel)
        split.addWidget(self.central_tabs)
        split.addWidget(self.result_panel)
        split.setSizes([360, 880, 300])
        self.setCentralWidget(split)

        log_dock = QDockWidget("运行日志", self)
        log_dock.setWidget(self.log_panel)
        log_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, log_dock)

    def _build_actions_menu_toolbar(self) -> None:
        self.act_new = QAction("新建项目", self)
        self.act_open = QAction("打开项目", self)
        self.act_save = QAction("保存项目", self)
        self.act_import = QAction("导入二维图像", self)
        self.act_preprocess = QAction("预处理几何", self)
        self.act_run_sim = QAction("运行仿真", self)
        self.act_run_rev = QAction("运行REV分析", self)
        self.act_export = QAction("导出结果", self)
        self.act_open_output = QAction("打开输出目录", self)
        self.act_about = QAction("关于", self)

        menu_file = self.menuBar().addMenu("文件")
        menu_file.addAction(self.act_new)
        menu_file.addAction(self.act_open)
        menu_file.addAction(self.act_save)
        menu_file.addSeparator()
        menu_file.addAction(self.act_open_output)

        menu_workflow = self.menuBar().addMenu("工作流")
        for act in [self.act_import, self.act_preprocess, self.act_run_sim, self.act_run_rev, self.act_export]:
            menu_workflow.addAction(act)

        menu_help = self.menuBar().addMenu("帮助")
        menu_help.addAction(self.act_about)

        tb = self.addToolBar("主工具栏")
        for act in [
            self.act_new,
            self.act_open,
            self.act_save,
            self.act_import,
            self.act_preprocess,
            self.act_run_sim,
            self.act_run_rev,
            self.act_export,
            self.act_open_output,
            self.act_about,
        ]:
            tb.addAction(act)

    def _bind_logger_to_gui(self) -> None:
        self.log_emitter = GuiLogEmitter()
        self.log_emitter.message.connect(self.log_panel.append)
        self.logger.addHandler(QtSignalHandler(self.log_emitter))

    def _connect_actions(self) -> None:
        self.act_new.triggered.connect(self.controller.new_project)
        self.act_open.triggered.connect(self.controller.open_project)
        self.act_save.triggered.connect(self.controller.save_project)
        self.act_import.triggered.connect(self.controller.import_image)
        self.act_preprocess.triggered.connect(self.controller.preprocess_geometry)
        self.act_run_sim.triggered.connect(self.controller.run_simulation)
        self.act_run_rev.triggered.connect(self.controller.run_rev)
        self.act_export.triggered.connect(self.controller.export_results)
        self.act_open_output.triggered.connect(self.controller.open_output_dir)
        self.act_about.triggered.connect(self.controller.about)
