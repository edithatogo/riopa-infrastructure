import json
from pathlib import Path

from scripts.validate_panel_reports import validate


def _reports(tmp_path: Path) -> list[Path]:
    paths = []
    for role in ("reproducer", "adversarial-analyst", "evidence-auditor"):
        path = tmp_path / f"{role}.json"
        path.write_text(
            json.dumps(
                {
                    "report_id": f"{role}-20260802",
                    "track_id": "example_track_20260719",
                    "scope": "bounded public-data preview",
                    "evaluated_at": "2026-08-02T00:00:00Z",
                    "role": role,
                    "source_revision": "a" * 40,
                    "bundle_sha256": "b" * 64,
                    "disposition": "pass-with-limitations",
                    "findings": [],
                    "evidence_refs": [],
                    "dissent": [],
                }
            ),
            encoding="utf-8",
        )
        paths.append(path)
    return paths


def test_panel_reports_require_concordance(tmp_path: Path) -> None:
    assert validate(_reports(tmp_path)) == []


def test_panel_reports_fail_on_digest_mismatch(tmp_path: Path) -> None:
    paths = _reports(tmp_path)
    value = json.loads(paths[1].read_text(encoding="utf-8"))
    value["bundle_sha256"] = "c" * 64
    paths[1].write_text(json.dumps(value), encoding="utf-8")
    assert any("bundle_sha256" in error for error in validate(paths))


def test_panel_reports_require_content_bound_fields(tmp_path: Path) -> None:
    paths = _reports(tmp_path)
    value = json.loads(paths[0].read_text(encoding="utf-8"))
    del value["evidence_refs"]
    paths[0].write_text(json.dumps(value), encoding="utf-8")
    assert "evidence_refs must be a list" in validate(paths)
