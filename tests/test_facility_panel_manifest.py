import json
from pathlib import Path

from scripts.validate_facility_panel_manifest import validate


def _manifest() -> dict:
    member = {
        "role": "methods",
        "session_id": "session-1",
        "model_identity": "agent-model-1",
        "environment": {"python": "3.14"},
        "commands": ["pytest"],
        "results": {"status": "pass"},
        "findings": [],
        "dissent": [],
        "remediation": [],
        "rerun_outcome": "not-required",
        "artifact_digests": [{"path": "report.json", "sha256": "b" * 64}],
    }
    panel = []
    for index, role in enumerate(("methods", "provenance", "governance", "reproducibility")):
        item = dict(member)
        item["role"] = role
        item["session_id"] = f"session-{index}"
        item["model_identity"] = f"agent-model-{index}"
        panel.append(item)
    return {
        "schema": "riopa.facility-panel-manifest.v1",
        "manifest_id": "facility-panel-manifest-test",
        "packet_id": "facility-panel-frame-qualification-20260825",
        "source_revision": "a" * 40,
        "packet_sha256": "c" * 64,
        "evaluated_at": "2026-08-29T00:00:00Z",
        "panel": panel,
        "synthesis": {"disposition": "open"},
        "promotion_allowed": False,
    }


def test_manifest_shape_passes(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(_manifest()), encoding="utf-8")
    assert validate(path) == []


def test_manifest_rejects_missing_content_binding(tmp_path: Path) -> None:
    value = _manifest()
    del value["panel"][0]["session_id"]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("session_id" in error for error in validate(path))


def test_manifest_rejects_duplicate_session_and_model_identity(tmp_path: Path) -> None:
    value = _manifest()
    value["panel"][1]["session_id"] = value["panel"][0]["session_id"]
    value["panel"][1]["model_identity"] = value["panel"][0]["model_identity"]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    errors = validate(path)
    assert "panel session_id values must be unique" in errors
    assert "panel model_identity values must be unique" in errors


def test_manifest_requires_the_four_facility_lenses(tmp_path: Path) -> None:
    value = _manifest()
    value["panel"] = value["panel"][:1]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("exactly methods, provenance" in error for error in validate(path))


def test_manifest_rejects_non_utc_time_and_unsafe_duplicate_paths(tmp_path: Path) -> None:
    value = _manifest()
    value["evaluated_at"] = "2026-08-29T00:00:00+10:00"
    value["panel"][0]["artifact_digests"] = [
        {"path": "../report.json", "sha256": "b" * 64},
        {"path": "../report.json", "sha256": "c" * 64},
    ]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    errors = validate(path)
    assert any("evaluated_at" in error for error in errors)
    assert any("canonical relative path" in error for error in errors)
    assert any("paths must be unique" in error for error in errors)


def test_manifest_rejects_noncanonical_artifact_alias(tmp_path: Path) -> None:
    value = _manifest()
    value["panel"][0]["artifact_digests"] = [{"path": "reports//result.json", "sha256": "b" * 64}]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    assert any("canonical relative path" in error for error in validate(path))


def test_existing_frame_is_not_falsely_qualified() -> None:
    path = Path(__file__).parents[1] / "docs/facility-panel-frame-qualification-20260825.json"
    errors = validate(path)
    assert "unexpected manifest schema" in errors
    assert any("manifest_id" in error for error in errors)
