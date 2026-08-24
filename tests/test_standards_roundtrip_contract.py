from __future__ import annotations

import json
from pathlib import Path

from riopa_provenance.attestation import (
    build_dsse_envelope,
    build_in_toto_statement,
    decode_dsse_payload,
)
from riopa_provenance.crate import (
    build_research_object,
    validate_provenance_projections,
    verify_research_object,
)


def test_bounded_standards_round_trips_preserve_projection_contracts(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = root / "examples/minimal/snapshot-manifest.json"
    output = build_research_object(manifest, tmp_path / "research-object")
    assert verify_research_object(output).valid
    prov = json.loads((output / "prov.jsonld").read_text(encoding="utf-8"))
    openlineage = json.loads((output / "openlineage-events.json").read_text(encoding="utf-8"))
    assert validate_provenance_projections(prov, openlineage) == ()
    assert any(item.get("@type") == "prov:Activity" for item in prov["@graph"])
    assert openlineage["events"]

    statement = build_in_toto_statement(
        [{"name": "research-object", "digest": {"sha256": "a" * 64}}],
        predicate_type="https://example.test/riopa/bounded",
        predicate={"scope": "synthetic"},
    )
    envelope = build_dsse_envelope(statement)
    assert decode_dsse_payload(envelope) == statement
    assert envelope["signatures"] == []


def test_standards_roundtrip_contract_remains_non_assertive() -> None:
    root = Path(__file__).resolve().parents[1]
    contract = json.loads(
        (root / "docs/interoperability-standards-roundtrip-contract-20260825.json").read_text()
    )
    assert contract["promotion_allowed"] is False
    assert "external producer/consumer interoperability" in contract["open_gates"]
