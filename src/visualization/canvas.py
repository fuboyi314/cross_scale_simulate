"""Central display tabs for geometry, flow field and REV charts."""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QTabWidget, QTextEdit, QVBoxLayout, QWidget


class ImageTab(QWidget):
    """Single-image display widget using grayscale rendering."""

    def __init__(self, placeholder: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.label = QLabel(placeholder)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("QLabel { background:#1d1f21; color:#ddd; border:1px solid #444; }")
        self.label.setMinimumSize(500, 380)
        layout.addWidget(self.label)

    def show_array(self, arr: np.ndarray, title: str = "") -> None:
        """Display 2D ndarray as grayscale image."""
        if arr.ndim != 2:
            raise ValueError("Only 2D arrays are supported")
        if arr.dtype != np.uint8:
            src = arr.astype(np.float64)
            mn, mx = float(np.min(src)), float(np.max(src))
            arr = ((src - mn) / (mx - mn + 1e-12) * 255).astype(np.uint8)

        h, w = arr.shape
        img = QImage(arr.data, w, h, w, QImage.Format.Format_Grayscale8)
        pix = QPixmap.fromImage(img).scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.label.setPixmap(pix)
        if title:
            self.label.setToolTip(title)


class CentralTabs(QTabWidget):
    """Tab container required by GUI specification."""

    def __init__(self) -> None:
        super().__init__()
        self.raw_tab = ImageTab("原始结构（等待导入图像）")
        self.binary_tab = ImageTab("二值结构（等待预处理）")
        self.velocity_tab = ImageTab("速度场（等待仿真）")
        self.streamline_tab = QLabel("流线图（V1 暂不实现，预留入口）")
        self.rev_tab = ImageTab("REV分析（等待REV运行）")
        self.text_tab = QTextEdit()
        self.text_tab.setReadOnly(True)
        self.text_tab.setText("文本摘要（等待结果）")

        self.streamline_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.streamline_tab.setStyleSheet("QLabel { background:#272727; color:#ccc; border:1px dashed #555; }")

        self.addTab(self.raw_tab, "原始结构")
        self.addTab(self.binary_tab, "二值结构")
        self.addTab(self.velocity_tab, "速度场")
        self.addTab(self.streamline_tab, "流线图")
        self.addTab(self.rev_tab, "REV分析")
        self.addTab(self.text_tab, "文本摘要")

    def set_text_summary(self, text: str) -> None:
        """Update text summary tab content."""
        self.text_tab.setPlainText(text)
