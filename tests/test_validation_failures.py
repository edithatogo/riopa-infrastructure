from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from riopa_provenance.validation import (
    ManifestReference,
    _domain_schema_name,
    _load_and_validate_references,
    _resolve_local_reference,
    _validate_artifact_payloads,
    _validate_event_streams,
    artifact_payload_references,
    discover_manifests,
    manifest_reference_specs,
    validate_bundle,
    validate_file,
    validate_manifest_closure,
    validate_schema_directory,
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
    assert _domain_schema_name({"record_type": "source_health_observation"}) == (
        "source-health-observation.schema.json"
    )


def test_reference_helpers_cover_ambiguous_unknown_and_duplicate_records(tmp_path: Path) -> None:
    assert _domain_schema_name([]) is None
    assert _domain_schema_name({"unrecognised": True}) is None
    ambiguous = {
        "capture_set_id": "set",
        "metadata_capture_id": "metadata",
        "page_capture_ids": [],
        "capabilities_capture_id": "capabilities",
        "type_name": "layer-1",
    }
    assert _domain_schema_name(ambiguous) is None

    manifest = {
        "sources": [{}, "invalid", {"source_record": "source.json"}],
        "artifacts": [1, "artifact.json"],
        "quality_report": "",
        "rights_inventory": "rights.json",
        "domain_records": [2, "domain.json"],
    }
    assert [(item.reference, item.role) for item in manifest_reference_specs(manifest)] == [
        ("source.json", "source"),
        ("artifact.json", "artifact"),
        ("rights.json", "rights_inventory"),
        ("domain.json", "domain_record"),
    ]

    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    (tmp_path / "broken.json").write_text("{", encoding="utf-8")
    (tmp_path / "unknown.json").write_text("{}", encoding="utf-8")
    errors: list[str] = []
    loaded = _load_and_validate_references(
        tmp_path,
        [
            ManifestReference("broken.json", None, "domain_record"),
            ManifestReference("unknown.json", None, "domain_record"),
            ManifestReference("unknown.json", None, "domain_record"),
            ManifestReference("../escape.json", None, "domain_record"),
            ManifestReference("missing.json", "missing.schema.json", "artifact"),
        ],
        schema_dir,
        errors,
    )
    assert loaded == {"unknown.json": {}}
    assert any("duplicate local reference" in error for error in errors)
    assert any("could not read referenced JSON" in error for error in errors)
    assert any("cannot determine schema" in error for error in errors)
    assert any("escapes bundle root" in error for error in errors)
    assert any("missing referenced file" in error for error in errors)


def test_artifact_payload_validation_reports_path_content_and_status_failures(
    tmp_path: Path,
) -> None:
    payload = tmp_path / "payload.bin"
    payload.write_bytes(b"actual")
    artifacts = [
        {"artifact_id": "skipped", "payload_status": "external"},
        {"artifact_id": "no-path", "payload_status": "included"},
        {"artifact_id": "escape", "payload_status": "included", "path": "../escape"},
        {"artifact_id": "missing", "payload_status": "included", "path": "absent.bin"},
        {
            "artifact_id": "tampered",
            "payload_status": "included",
            "path": "payload.bin",
            "size_bytes": 1,
            "sha256": "0" * 64,
            "verification_status": "unverified",
        },
    ]
    errors: list[str] = []
    _validate_artifact_payloads(tmp_path, artifacts, errors)
    assert any("has no local path" in error for error in errors)
    assert any("escapes bundle root" in error for error in errors)
    assert any("payload is missing" in error for error in errors)
    assert any("size mismatch" in error for error in errors)
    assert any("hash mismatch" in error for error in errors)
    assert any("verification_status=verified" in error for error in errors)

    references = artifact_payload_references(
        tmp_path,
        [
            {"payload_status": "external", "path": "other.bin"},
            {"payload_status": "included", "path": 3},
            {"payload_status": "included", "path": "payload.bin"},
            {"payload_status": "included", "path": "payload.bin"},
        ],
    )
    assert references == ["payload.bin"]


def test_event_stream_validation_reports_chain_and_reference_failures() -> None:
    events = [
        {
            "event_id": "event-0",
            "event_type": "capture.download",
            "activity": {"activity_id": "capture-1"},
            "stream_id": "stream",
            "partition_id": "p",
            "sequence": 1,
            "previous_event_hash": "wrong",
            "event_hash": "wrong",
            "inputs": ["unknown"],
            "outputs": [],
            "causal_parent_event_ids": ["absent"],
        },
        {
            "event_id": "event-1",
            "event_type": "transform",
            "activity": {},
            "stream_id": "stream",
            "partition_id": "p",
            "sequence": 1,
            "previous_event_hash": None,
            "event_hash": "wrong",
            "inputs": [],
            "outputs": [],
        },
        {
            "event_id": "event-2",
            "event_type": "transform",
            "activity": {},
            "stream_id": "stream",
            "partition_id": "p",
            "sequence": 3,
            "previous_event_hash": None,
            "event_hash": "wrong",
            "inputs": [],
            "outputs": [],
        },
        {
            "event_id": "event-x",
            "event_type": "transform",
            "activity": {},
            "stream_id": "stream",
            "sequence": "not-an-integer",
            "inputs": [],
            "outputs": [],
        },
    ]
    errors: list[str] = []
    assert _validate_event_streams(events, set(), errors) == {"capture-1"}
    assert any("undeclared entity" in error for error in errors)
    assert any("duplicate sequence" in error for error in errors)
    assert any("sequence gaps" in error for error in errors)
    assert any("begins at sequence" in error for error in errors)
    assert any("previous hash mismatch" in error for error in errors)
    assert any("hash mismatch" in error for error in errors)
    assert any("undeclared causal parent" in error for error in errors)


def test_manifest_and_schema_directory_failure_surfaces(tmp_path: Path) -> None:
    manifest = tmp_path / "snapshot-manifest.json"
    manifest.write_text("[]", encoding="utf-8")
    assert validate_manifest_closure(manifest).errors == ("manifest root must be an object",)

    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    manifest.write_text("{}", encoding="utf-8")
    missing = validate_manifest_closure(manifest, schema_dir=schema_dir)
    assert any("missing snapshot schema" in error for error in missing.errors)

    snapshot_schema = schema_dir / "snapshot-manifest.schema.json"
    snapshot_schema.write_text("{", encoding="utf-8")
    unreadable = validate_manifest_closure(manifest, schema_dir=schema_dir)
    assert any("could not read snapshot schema" in error for error in unreadable.errors)

    assert validate_schema_directory(tmp_path / "empty")[0].errors == ("no schemas found",)
    schema_dir.joinpath("one.schema.json").write_text(
        json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object"}),
        encoding="utf-8",
    )
    duplicate_id = "https://example.test/schema"
    for name in ("two.schema.json", "three.schema.json"):
        schema_dir.joinpath(name).write_text(
            json.dumps(
                {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "$id": duplicate_id,
                    "type": "object",
                }
            ),
            encoding="utf-8",
        )
    results = validate_schema_directory(schema_dir)
    errors = [error for result in results for error in result.errors]
    assert "schema has no non-empty $id" in errors
    assert any("duplicate $id" in error for error in errors)


def test_manifest_discovery_ignores_generated_directories(tmp_path: Path) -> None:
    expected = tmp_path / "evidence" / "snapshot-manifest.json"
    expected.parent.mkdir()
    expected.write_text("{}", encoding="utf-8")
    ignored = tmp_path / "build" / "snapshot-manifest.json"
    ignored.parent.mkdir()
    ignored.write_text("{}", encoding="utf-8")
    assert discover_manifests(tmp_path) == [expected]


def test_provenance_profile_manifest_records_bounded_conformance() -> None:
    manifest = json.loads(
        (ROOT / "docs/provenance-profile-conformance-manifest-1.0.0.json").read_text()
    )
    assert manifest["status"] == "bounded-pending"
    assert manifest["checks"]["python_schema"] == "passing"
    assert manifest["checks"]["non_python_round_trip"] == "not-run"
    assert manifest["checks"]["signed_attestation"] == "not-run"
