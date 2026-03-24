"""Application entrypoint for the porous-media platform."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from src.core.logging_service import setup_logging
from src.ui.main_window import MainWindow


def main() -> int:
    """Launch Qt application."""
    logs_dir = Path.cwd() / "logs"
    logger = setup_logging(logs_dir)

    app = QApplication(sys.argv)
    app.setApplicationName("基于LBM的跨尺度多孔介质渗流模拟平台")
    window = MainWindow(logger=logger)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
