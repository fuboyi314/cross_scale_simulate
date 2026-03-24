"""Bottom log panel showing runtime messages."""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget


class LogPanel(QWidget):
    """Timestamped log viewer with colored levels."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)
        self.viewer.setMinimumHeight(150)
        layout.addWidget(self.viewer)

    def append(self, level: str, text: str) -> None:
        """Append formatted line with color by level."""
        color = {
            "info": QColor("#d8d8d8"),
            "warning": QColor("#f2c94c"),
            "error": QColor("#ff6b6b"),
        }.get(level, QColor("#d8d8d8"))
        self.viewer.setTextColor(color)
        self.viewer.append(text)
