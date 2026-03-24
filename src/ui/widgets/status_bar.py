"""Status bar updater utility."""

from __future__ import annotations

from PySide6.QtWidgets import QStatusBar


class AppStatus:
    """Helper for consistent status-bar messages."""

    def __init__(self, status_bar: QStatusBar) -> None:
        self.status_bar = status_bar
        self.project_name = "无"
        self.state = "idle"
        self.last_result = "就绪"

    def update(self, *, project_name: str | None = None, state: str | None = None, result: str | None = None) -> None:
        if project_name is not None:
            self.project_name = project_name
        if state is not None:
            self.state = state
        if result is not None:
            self.last_result = result
        self.status_bar.showMessage(
            f"项目: {self.project_name} | 状态: {self.state} | 最近结果: {self.last_result}"
        )
