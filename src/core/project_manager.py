"""Project lifecycle and persistence manager."""

from __future__ import annotations

import json
from pathlib import Path

from src.core.models import ProjectConfig


class ProjectManager:
    """Manage current project and recent project list."""

    def __init__(self) -> None:
        self.current_project: ProjectConfig | None = None
        self.recent_projects: list[str] = []

    def create_project(self, project_name: str, working_directory: str) -> ProjectConfig:
        """Create new project object and prepare output directory."""
        project = ProjectConfig(project_name=project_name, working_directory=working_directory)
        project.output_dir.mkdir(parents=True, exist_ok=True)
        project.summary.output_directory = str(project.output_dir)
        self.current_project = project
        self._push_recent(str(project.project_file))
        return project

    def save_project(self, project_file: Path | None = None) -> Path:
        """Save current project to JSON."""
        if self.current_project is None:
            raise RuntimeError("No project loaded")
        target = project_file or self.current_project.project_file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.current_project.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        self._push_recent(str(target))
        return target

    def load_project(self, project_file: Path) -> ProjectConfig:
        """Load project from JSON file."""
        raw = json.loads(project_file.read_text(encoding="utf-8"))
        project = ProjectConfig.from_dict(raw)
        project.output_dir.mkdir(parents=True, exist_ok=True)
        if not project.summary.output_directory:
            project.summary.output_directory = str(project.output_dir)
        self.current_project = project
        self._push_recent(str(project_file))
        return project

    def _push_recent(self, path: str) -> None:
        if path in self.recent_projects:
            self.recent_projects.remove(path)
        self.recent_projects.insert(0, path)
        self.recent_projects = self.recent_projects[:10]
