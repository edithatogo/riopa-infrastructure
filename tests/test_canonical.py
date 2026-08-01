import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from riopa_provenance.canonical import (
    build_crosswalk,
    canonical_entity_id,
    canonical_version_id,
    validate_conformance_manifest,
    validate_crosswalk_contract,
    validate_crosswalk_semantics,
)
from riopa_provenance.hashing import sha256_json


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


def test_ontology_context_declares_canonical_terms() -> None:
    context = json.loads(Path("docs/ontology/canonical-context.jsonld").read_text())
    terms = context["@context"]
    assert terms["riopa"] == "https://w3id.org/riopa/ontology/"
    assert {"entity", "mapping", "canonicalConcept"}.issubset(terms)


def test_golden_fixture_has_stable_canonical_digest() -> None:
    fixture = json.loads(Path("fixtures/canonical-crosswalk-golden.json").read_text())
    assert validate_crosswalk_semantics(fixture) == ()
    assert sha256_json(fixture) == (
        "51765ecf4129f0cfb7c5045a77977c999894e978a74cb84346f0a68ee8c0f828"
    )
    assert validate_crosswalk_contract(fixture) == ()


def test_crosswalk_contract_rejects_missing_id_and_evidence() -> None:
    errors = validate_crosswalk_contract(
        {"confidence": "disputed", "valid_time": {"from": "2026-01-01", "to": None}}
    )
    assert any("missing required field: mapping_id" in error for error in errors)
    assert any("uncertain mappings require at least one evidence" in error for error in errors)


def test_versioned_migration_fixture_is_explicit_and_bounded() -> None:
    migration = json.loads(
        Path("docs/ontology/migrations/canonical-crosswalk-1.0.0-to-1.1.0.json").read_text()
    )
    assert migration["from_version"] == "1.0.0"
    assert migration["to_version"] == "1.1.0"
    assert migration["compatibility"] == "backward-compatible"
    assert migration["automated"] is True
    assert migration["notes"].startswith("Fixture documents")


def test_ontology_release_descriptor_is_versioned_and_unpublished() -> None:
    descriptor = json.loads(
        Path("docs/ontology/canonical-ontology-release-1.0.0.json").read_text()
    )
    assert descriptor["version"] == "1.0.0"
    assert descriptor["status"] == "repository-fixture"
    assert descriptor["publication"]["persistent_identifier"] is None
    assert len(descriptor["artifacts"]) == 3


def test_conformance_manifest_reports_unmet_external_checks() -> None:
    manifest = json.loads(
        Path("docs/ontology/canonical-conformance-manifest-1.0.0.json").read_text()
    )
    assert manifest["status"] == "bounded-pending"
    assert manifest["checks"]["shacl"]["status"] == "not-run"
    assert manifest["checks"]["cross_language_round_trip"]["status"] == "not-run"
    assert manifest["publication"]["persistent_identifier"] is None
    assert validate_conformance_manifest(manifest, root=".") == ()
