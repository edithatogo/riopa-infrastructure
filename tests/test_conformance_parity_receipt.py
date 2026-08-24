import json
from pathlib import Path

from scripts.verify_conformance_parity import build_receipt


def test_bounded_conformance_receipt_matches_python_and_node() -> None:
    root = Path(__file__).resolve().parents[1]
    receipt = build_receipt(root)
    assert receipt["case_count"] > 0
    assert receipt["python_passed"] is True
    assert receipt["node_passed"] is True
    assert receipt["parity"] is True
    corpus_version = json.loads((root / "conformance/v1/corpus.json").read_text())["corpus_version"]
    assert corpus_version == receipt["corpus_version"]


def test_preserved_parity_receipt_is_bounded_and_non_assertive() -> None:
    root = Path(__file__).resolve().parents[1]
    receipt = json.loads(
        (root / "docs/ontology/canonical-cross-language-parity-20260824.json").read_text()
    )
    assert receipt["parity"] is True
    assert receipt["scope"] == "bounded canonical-hash and schema-outcome corpus"
    assert any("SHACL" in claim for claim in receipt["non_claims"])


def test_provenance_plan_closes_bounded_conformance_without_signed_release_claim() -> None:
    root = Path(__file__).resolve().parents[1]
    plan = (root / "conductor/tracks/provenance_profile_v1_20260718/plan.md").read_text()
    assert "[x] 3.2 Emit and validate bounded PROV" in plan
    assert "[x] 3.3 Run the bounded positive" in plan
    assert "trusted signed attestation remains release-gated" in plan
