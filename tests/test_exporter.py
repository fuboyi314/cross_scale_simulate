from pathlib import Path

from src.core.models import ProjectConfig
from src.io.exporter import ExportManager
from src.upscaling.interface import REVResult


def test_export_csv_json_report(tmp_path: Path) -> None:
    mgr = ExportManager()
    dirs = mgr.prepare_dirs(tmp_path / "outputs")

    csv_path = dirs["tables"] / "x.csv"
    mgr.export_csv(csv_path, ["a", "b"], [[1, 2]])
    assert csv_path.exists()

    json_path = dirs["configs"] / "x.json"
    mgr.export_json(json_path, {"k": 1})
    assert json_path.exists()

    project = ProjectConfig(project_name="demo", working_directory=str(tmp_path))
    report_path = dirs["reports"] / "summary.md"
    mgr.export_report(report_path, project, REVResult(records=[], suggested_size=None, note="n/a"))
    assert report_path.exists()
