import json
from pathlib import Path

from scripts.generate_panel_report_templates import generate
from scripts.validate_panel_reports import validate_template_manifest


def test_template_manifest_covers_every_track(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    output = tmp_path / "templates.json"
    generate(root / "conductor" / "tracks", output)
    assert validate_template_manifest(output, root / "conductor" / "tracks") == []
    payload = json.loads(output.read_text())
    assert payload["non_assertive"] is True
    assert all(
        entry["status"] == "pending" and entry["disposition"] is None for entry in payload["tracks"]
    )
