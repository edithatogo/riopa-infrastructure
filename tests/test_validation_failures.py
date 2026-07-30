from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from riopa_provenance.validation import (
    _resolve_local_reference,
    validate_bundle,
    validate_file,
    validate_manifest_closure,
)

ROOT = Path(__file__).resolve().parents[1]


def test_validate_file_reports_unreadable_json(tmp_path: Path) -> None:
    instance = tmp_path / "broken.json"
    instance.write_text("{not-json", encoding="utf-8")
    result = validate_file(instance, ROOT / "schemas/source-record.schema.json")
    assert not result.valid
    assert result.errors


def test_validate_file_detects_event_and_manifest_hash_tampering(tmp_path: Path) -> None:
    event_path = tmp_path / "provenance-event.json"
    manifest_path = tmp_path / "snapshot-manifest.json"
    shutil.copy2(ROOT / "examples/minimal/provenance-event.json", event_path)
    shutil.copy2(ROOT / "examples/minimal/snapshot-manifest.json", manifest_path)

    event = json.loads(event_path.read_text(encoding="utf-8"))
    event["recorded_at"] = "2026-07-18T12:00:00Z"
    event_path.write_text(json.dumps(event), encoding="utf-8")
    event_result = validate_file(event_path, ROOT / "schemas/provenance-event.schema.json")
    assert any("event_hash mismatch" in error for error in event_result.errors)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["title"] = "Tampered"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    manifest_result = validate_file(manifest_path, ROOT / "schemas/snapshot-manifest.schema.json")
    assert any("manifest_sha256 mismatch" in error for error in manifest_result.errors)


def test_absolute_bundle_reference_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="absolute reference"):
        _resolve_local_reference(tmp_path, "/etc/passwd")


def test_manifest_reader_reports_invalid_json_and_hash_mismatch(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid-manifest.json"
    invalid.write_text("[", encoding="utf-8")
    assert not validate_manifest_closure(invalid).valid

    target = tmp_path / "minimal"
    shutil.copytree(ROOT / "examples/minimal", target)
    manifest_path = target / "snapshot-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["title"] = "Changed without rehashing"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = validate_manifest_closure(manifest_path)
    assert any("manifest hash does not match" in error for error in result.errors)


def test_bundle_validator_reports_missing_examples_schemas_and_bad_schema(tmp_path: Path) -> None:
    schema_dir = tmp_path / "schemas"
    example_dir = tmp_path / "examples/minimal"
    schema_dir.mkdir(parents=True)
    example_dir.mkdir(parents=True)

    # The first configured example is absent, while the second exists without its schema.
    (example_dir / "artifact-raw.json").write_text("{}", encoding="utf-8")
    (schema_dir / "broken.schema.json").write_text(
        json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "type": 7}),
        encoding="utf-8",
    )

    results = validate_bundle(tmp_path)
    errors = [error for result in results for error in result.errors]
    assert "missing example" in errors
    assert "missing schema" in errors
    assert any("not valid" in error or "is not of type" in error for error in errors)


def test_source_health_domain_record_uses_normative_schema() -> None:
    from riopa_provenance.validation import _domain_schema_name

    assert _domain_schema_name({"record_type": "source_health_observation"}) == (
        "source-health-observation.schema.json"
    )
