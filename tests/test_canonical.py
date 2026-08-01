import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from riopa_provenance.canonical import (
    build_crosswalk,
    canonical_entity_id,
    canonical_version_id,
    validate_crosswalk_semantics,
)


def test_entity_id_is_stable_and_label_independent() -> None:
    assert canonical_entity_id("facility", "NZ-01") == "urn:riopa:entity:facility:NZ-01"


def test_version_id_changes_with_representation() -> None:
    base = canonical_entity_id("facility", "NZ-01")
    first = canonical_version_id(
        base, valid_from="2026-01-01", valid_to=None, representation={"name": "A"}
    )
    second = canonical_version_id(
        base, valid_from="2026-01-01", valid_to=None, representation={"name": "B"}
    )
    assert first != second
    assert first.startswith(base + ":version:")


def test_crosswalk_preserves_source_and_uncertainty() -> None:
    record = build_crosswalk(
        source_id="council:one",
        source_label="Urgent care",
        canonical_id="urn:riopa:concept:service:urgent-care",
        method="manual-review",
        confidence="disputed",
        reviewer="reviewer@example.org",
        valid_from="2026-01-01",
    )
    assert record["source_assertion"]["label"] == "Urgent care"
    assert record["confidence"] == "disputed"


def test_crosswalk_builder_output_matches_normative_schema() -> None:
    record = build_crosswalk(
        source_id="council:one", source_label="Urgent care",
        canonical_id="urn:riopa:concept:service:urgent-care", method="manual",
        confidence="medium", reviewer="reviewer", valid_from="2026-01-01",
    )
    schema = json.loads(Path("schemas/canonical-crosswalk.schema.json").read_text())
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record))
    assert not errors
    assert validate_crosswalk_semantics(record) == ()


def test_crosswalk_semantics_fail_closed_for_reversed_time() -> None:
    record = build_crosswalk(
        source_id="s", source_label="x", canonical_id="urn:riopa:concept:x",
        method="manual", confidence="medium", reviewer="r", valid_from="2026-02-01",
        valid_to="2026-01-01",
    )
    assert "valid_time.to must not precede valid_time.from" in validate_crosswalk_semantics(record)
