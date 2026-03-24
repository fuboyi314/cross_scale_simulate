"""Asynchronous task runner for non-blocking GUI operations."""

from __future__ import annotations

import traceback
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class TaskSignals(QObject):
    """Signals for async task life-cycle."""

    started = Signal(str)
    progress = Signal(int, int, str)
    finished = Signal(object)
    error = Signal(str)


class TaskWorker(QRunnable):
    """Run arbitrary callable in thread pool."""

    def __init__(self, name: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.name = name
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = TaskSignals()

    def run(self) -> None:
        self.signals.started.emit(self.name)
        try:
            result = self.fn(*self.args, progress=self.signals.progress.emit, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception:
            self.signals.error.emit(traceback.format_exc())


class TaskRunner:
    """Thin wrapper around global QThreadPool."""

    def __init__(self) -> None:
        self.pool = QThreadPool.globalInstance()

    def submit(self, worker: TaskWorker) -> None:
        self.pool.start(worker)
