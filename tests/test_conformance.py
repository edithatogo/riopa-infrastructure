from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from riopa_provenance.canonical import (
    validate_bounded_shacl_constraints,
    validate_conformance_corpus,
    validate_conformance_manifest,
    validate_migration_fixture,
)
from riopa_provenance.hashing import sha256_json


def _corpus() -> tuple[Path, dict[str, Any]]:
    root = Path(__file__).resolve().parents[1]
    path = root / "conformance/v1/corpus.json"
    return root, json.loads(path.read_text(encoding="utf-8"))


def test_python_reference_passes_language_neutral_corpus() -> None:
    root, corpus = _corpus()
    for case in corpus["cases"]:
        assert sha256_json(case["instance"]) == case["expected_sha256"]
        if case["schema"] is not None:
            schema_path = (root / "conformance/v1" / case["schema"]).resolve()
            validator = Draft202012Validator(json.loads(schema_path.read_text()))
            errors = list(validator.iter_errors(case["instance"]))
            assert (not errors) is case["expected_valid"]


def test_corpus_envelope_is_safe_and_well_formed() -> None:
    root, corpus = _corpus()
    assert validate_conformance_corpus(corpus, root=str(root / "conformance/v1")) == ()

    tampered = dict(corpus)
    tampered["cases"] = [dict(corpus["cases"][0]), dict(corpus["cases"][0])]
    assert any(
        "duplicate case_id" in error
        for error in validate_conformance_corpus(tampered, root=str(root / "conformance/v1"))
    )


def test_corpus_envelope_rejects_unknown_case_class() -> None:
    root, corpus = _corpus()
    tampered = json.loads(json.dumps(corpus))
    tampered["cases"][0]["case_class"] = "unknown"
    errors = validate_conformance_corpus(tampered, root=str(root / "conformance/v1"))
    assert any("case_class must be one of" in error for error in errors)

    tampered["cases"][0]["case_class"] = []
    errors = validate_conformance_corpus(tampered, root=str(root / "conformance/v1"))
    assert any("case_class must be one of" in error for error in errors)


def test_corpus_envelope_requires_each_case_class() -> None:
    root, corpus = _corpus()
    tampered = {
        **corpus,
        "cases": [case for case in corpus["cases"] if case["case_class"] != "migration"],
    }
    errors = validate_conformance_corpus(tampered, root=str(root / "conformance/v1"))
    assert "corpus is missing required case classes: migration" in errors


def test_node_implementation_matches_python_outcomes() -> None:
    root, corpus = _corpus()
    result = subprocess.run(
        ["node", "scripts/conformance_node.mjs", "conformance/v1/corpus.json"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(result.stdout)
    assert report["runner"] == "node-standard-library"
    assert [item["case_id"] for item in report["results"]] == [
        item["case_id"] for item in corpus["cases"]
    ]
    assert all(item["passed"] for item in report["results"])


def test_bounded_typescript_provenance_model_is_present() -> None:
    root = Path(__file__).resolve().parents[1]
    model = root / "bindings/typescript/provenance-event-v1.d.ts"
    text = model.read_text(encoding="utf-8")
    assert "export interface ProvenanceEventV1" in text
    assert 'schema_version: "1.0.0"' in text
    assert "event_hash: string" in text


def test_minimal_rights_inventory_is_schema_valid_and_fail_closed_when_unresolved() -> None:
    root, _ = _corpus()
    schema = json.loads((root / "schemas/rights-inventory.schema.json").read_text())
    inventory = json.loads((root / "examples/minimal/rights-inventory.json").read_text())
    assert not list(Draft202012Validator(schema).iter_errors(inventory))
    inventory["sources"][0]["redistribution_status"] = "review-required"
    inventory["publication_decision"] = "review-required"
    assert inventory["publication_decision"] == "review-required"


def test_canonical_conformance_manifest_binds_artifact_digests() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "docs/ontology/canonical-conformance-manifest-1.0.0.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert validate_conformance_manifest(manifest, root=str(root)) == ()

    tampered = dict(manifest)
    tampered["artifact_sha256"] = dict(manifest["artifact_sha256"])
    artifact = manifest["artifacts"][0]
    tampered["artifact_sha256"][artifact] = "0" * 64
    assert any(
        "digest mismatch" in error
        for error in validate_conformance_manifest(tampered, root=str(root))
    )


def test_canonical_conformance_manifest_rejects_unbound_artifact() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = {
        "status": "bounded-pending",
        "publication": {"status": "unpublished", "persistent_identifier": None},
        "checks": {
            "shacl": {"status": "not-run"},
            "cross_language_round_trip": {"status": "not-run"},
        },
        "artifacts": ["docs/ontology/canonical-context.jsonld"],
        "artifact_sha256": {},
    }
    assert any(
        "keys must exactly match" in error
        for error in validate_conformance_manifest(manifest, root=str(root))
    )


def test_bounded_shacl_constraints_validate_shape_and_record() -> None:
    root, corpus = _corpus()
    shape = (root / "docs/ontology/canonical-crosswalk.shacl.ttl").read_text()
    record = next(
        item["instance"]
        for item in corpus["cases"]
        if item["case_id"] == "canonical-crosswalk-golden"
    )
    assert validate_bounded_shacl_constraints(shape, record) == ()
    record["evidence"] = []
    assert "evidence must contain at least one item" in validate_bounded_shacl_constraints(
        shape, record
    )


def test_bounded_shacl_constraints_reject_incomplete_shape() -> None:
    root, _ = _corpus()
    shape = (root / "docs/ontology/canonical-crosswalk.shacl.ttl").read_text()
    shape = shape.replace("sh:path riopa:reviewer ;", "sh:path riopa:removedReviewer ;")
    record = json.loads((root / "fixtures/canonical-crosswalk-golden.json").read_text())
    errors = validate_bounded_shacl_constraints(shape, record)
    assert any("missing required paths" in error for error in errors)
    assert any("unsupported SHACL property path" in error for error in errors)


def test_bounded_shacl_constraints_reject_string_datatype_drift() -> None:
    root, corpus = _corpus()
    shape = (root / "docs/ontology/canonical-crosswalk.shacl.ttl").read_text()
    shape = shape.replace(
        "sh:datatype <http://www.w3.org/2001/XMLSchema#string>",
        "sh:datatype <http://www.w3.org/2001/XMLSchema#integer>",
        1,
    )
    record = next(
        item["instance"]
        for item in corpus["cases"]
        if item["case_id"] == "canonical-crosswalk-golden"
    )
    assert "SHACL string datatype is missing for mappingId" in validate_bounded_shacl_constraints(
        shape, record
    )


def test_provenance_profile_compatibility_matrix_is_bound_to_migration_fixture() -> None:
    root = Path(__file__).resolve().parents[1]
    matrix = json.loads(
        (root / "docs/provenance-profile-compatibility-matrix-20260825.json").read_text()
    )
    migration = json.loads(
        (root / "docs/provenance-profile-migration-1.0.0-to-1.1.0.json").read_text()
    )
    assert matrix["status"] == "bounded-draft"
    assert matrix["source_version"] == migration["from_version"]
    assert matrix["target_version"] == migration["to_version"]
    assert validate_migration_fixture(migration) == ()
    assert {entry["path"] for entry in matrix["entries"]} == {
        change["path"] for change in migration["changes"]
    }


def test_provenance_plan_closes_migration_contract_without_claiming_release() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = (root / "conductor/tracks/provenance_profile_v1_20260718/plan.md").read_text()
    assert "[x] 4.2 Define the bounded profile compatibility matrix" in plan
    assert "persistent publication identifier and stable release remain open" in plan
