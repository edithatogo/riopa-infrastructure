import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from riopa_provenance.capture_migration import (
    CaptureMigrationError,
    migrate_capture,
    migrate_capture_jsonl,
    recover_capture,
)
from riopa_provenance.hashing import sha256_json

SOURCE = Path("evidence/stats-nz-meshblock-2026-projection/capture-records.jsonl")


def native() -> dict:
    return json.loads(SOURCE.read_text().splitlines()[0])


def test_all_real_archived_records_roundtrip_and_validate(tmp_path: Path) -> None:
    schema = json.loads(Path("schemas/archived-capture-view.schema.json").read_text())
    original = SOURCE.read_bytes()
    target = tmp_path / "views.jsonl"
    assert migrate_capture_jsonl(SOURCE, target) == 236
    rows = SOURCE.read_text().splitlines()
    for line, raw in zip(target.read_text().splitlines(), rows, strict=True):
        view = json.loads(line)
        Draft202012Validator(schema).validate(view)
        assert recover_capture(view) == json.loads(raw)
    assert SOURCE.read_bytes() == original
    assert migrate_capture_jsonl(SOURCE, target) == 236


def test_facets_are_isolated_and_integrity_bound() -> None:
    source = native()
    facets = {"quality": [{"uri": "urn:example:quality", "sha256": "a" * 64}]}
    original = copy.deepcopy(source)
    view = migrate_capture(source, facets=facets)
    assert recover_capture(view) == original
    source["record"]["source_id"] = "changed"
    facets["quality"][0]["uri"] = "changed"
    assert recover_capture(view) == original
    recovered = recover_capture(view)
    recovered["record"]["source_id"] = "changed"
    assert recover_capture(view) == original
    view["facets"]["quality"][0]["uri"] = "tampered"
    with pytest.raises(CaptureMigrationError, match="view digest"):
        recover_capture(view)


@pytest.mark.parametrize(
    "field,value", [("schema_version", "2.0.0"), ("record_type", "invented"), ("source_id", "")]
)
def test_unsupported_native_contract_is_rejected(field: str, value: str) -> None:
    source = native()
    source["record"][field] = value
    with pytest.raises(CaptureMigrationError):
        migrate_capture(source)


def test_corrupt_source_cannot_be_rehashed_into_a_valid_view() -> None:
    source = native()
    source["record"]["artifact"]["bytes"] += 1
    with pytest.raises(CaptureMigrationError, match="digest"):
        migrate_capture(source)
    view = migrate_capture(native())
    view["source"] = source
    view["view_sha256"] = sha256_json(view, omit_keys={"view_sha256"})
    with pytest.raises(CaptureMigrationError, match="digest"):
        recover_capture(view)


@pytest.mark.parametrize(
    "facets",
    [
        {"unknown": []},
        {"quality": []},
        {"source_rights": [{"uri": "x", "sha256": "wrong"}]},
        {"quality": [{"uri": " ", "sha256": "a" * 64}]},
        {"quality": [{}]},
    ],
)
def test_invalid_facets_are_rejected(facets: dict) -> None:
    with pytest.raises(CaptureMigrationError):
        migrate_capture(native(), facets=facets)


def test_failed_batch_never_replaces_source_or_destination(tmp_path: Path) -> None:
    source = tmp_path / "input.jsonl"
    target = tmp_path / "output.jsonl"
    source.write_text(json.dumps(native()) + '\n{"record": 1}\n')
    with pytest.raises(CaptureMigrationError):
        migrate_capture_jsonl(source, target)
    assert not target.exists()
    assert list(tmp_path.iterdir()) == [source]
    source.write_text(json.dumps(native()) + "\n")
    target.write_bytes(b"existing")
    with pytest.raises(CaptureMigrationError, match="conflicts"):
        migrate_capture_jsonl(source, target)
    assert target.read_bytes() == b"existing"
    with pytest.raises(CaptureMigrationError, match="must differ"):
        migrate_capture_jsonl(source, source)


def test_duplicate_json_fields_and_empty_batches_are_rejected(tmp_path: Path) -> None:
    source = tmp_path / "input.jsonl"
    target = tmp_path / "output.jsonl"
    for text, message in [
        ('{"record": {}, "record": {}}', "duplicate"),
        ("", "empty"),
        ("[]", "object"),
    ]:
        source.write_text(text)
        with pytest.raises(CaptureMigrationError, match=message):
            migrate_capture_jsonl(source, target)
        assert not target.exists()


@pytest.mark.parametrize(
    "field,value",
    [("schema_version", "9.0.0"), ("record_type", "other"), ("source", []), ("facets", [])],
)
def test_invalid_view_contract_is_rejected(field: str, value: object) -> None:
    view = migrate_capture(native())
    view[field] = value
    with pytest.raises(CaptureMigrationError):
        recover_capture(view)


def test_unknown_view_fields_are_not_silently_lost() -> None:
    view = migrate_capture(native())
    view["unexpected"] = "must not be discarded"
    with pytest.raises(CaptureMigrationError, match="fields"):
        recover_capture(view)


def test_recorded_migration_evidence_reproduces() -> None:
    from scripts.build_capture_migration_evidence import build_evidence

    assert build_evidence(Path(".")) == json.loads(
        Path("docs/archived-capture-migration-evidence-20260912.json").read_text()
    )


def test_interrupted_publication_leaves_no_partial_output_and_can_retry(
    tmp_path: Path, monkeypatch
) -> None:
    import riopa_provenance.capture_migration as migration

    source = tmp_path / "input.jsonl"
    target = tmp_path / "output.jsonl"
    source.write_text(json.dumps(native()) + "\n")
    original = source.read_bytes()
    link = migration.os.link

    def interrupted(*args):
        raise OSError("injected publication interruption")

    monkeypatch.setattr(migration.os, "link", interrupted)
    with pytest.raises(OSError, match="interruption"):
        migrate_capture_jsonl(source, target)
    assert sorted(tmp_path.iterdir()) == [source]
    assert source.read_bytes() == original
    monkeypatch.setattr(migration.os, "link", link)
    assert migrate_capture_jsonl(source, target) == 1
    assert recover_capture(json.loads(target.read_text())) == native()


@pytest.mark.parametrize("field", ["source_id", "quality", "source_rights"])
def test_schema_rejects_whitespace_identifiers(field: str) -> None:
    view = migrate_capture(native())
    if field == "source_id":
        view["source"]["record"]["source_id"] = " \t"
    else:
        view["facets"][field] = [{"uri": " \t", "sha256": "a" * 64}]
    schema = json.loads(Path("schemas/archived-capture-view.schema.json").read_text())
    assert not Draft202012Validator(schema).is_valid(view)
    with pytest.raises(CaptureMigrationError):
        recover_capture(view)
