"""Logging setup shared by file logger and GUI log panel."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal


class GuiLogEmitter(QObject):
    """Qt signal wrapper to emit formatted logs to GUI."""

    message = Signal(str, str)  # level, formatted text


class QtSignalHandler(logging.Handler):
    """Logging handler that forwards messages to Qt signal."""

    def __init__(self, emitter: GuiLogEmitter) -> None:
        super().__init__()
        self.emitter = emitter

    def emit(self, record: logging.LogRecord) -> None:
        ts = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{ts} [{record.levelname}] {record.getMessage()}"
        self.emitter.message.emit(record.levelname.lower(), msg)


def setup_logging(log_dir: Path) -> logging.Logger:
    """Create app logger with file + stream handlers."""
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("cross_scale_simulate")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    fhandler = logging.FileHandler(log_dir / "application.log", encoding="utf-8")
    fhandler.setFormatter(formatter)

    shandler = logging.StreamHandler()
    shandler.setFormatter(formatter)

    logger.addHandler(fhandler)
    logger.addHandler(shandler)
    return logger
