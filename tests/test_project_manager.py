from pathlib import Path

from src.core.project_manager import ProjectManager


def test_create_save_load_project(tmp_path: Path) -> None:
    manager = ProjectManager()
    project = manager.create_project("demo", str(tmp_path))
    saved = manager.save_project()
    assert saved.exists()

    loaded = manager.load_project(saved)
    assert loaded.project_name == "demo"
    assert Path(loaded.summary.output_directory).exists()
