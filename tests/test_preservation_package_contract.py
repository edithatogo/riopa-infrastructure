import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_preservation_package_contract_requires_fixity_and_successors() -> None:
    record = json.loads((ROOT / "docs/preservation-package-contract-20260822.json").read_text())
    package = record["package_format"]
    assert {"manifest.json", "SHA256SUMS", "methods.md"} <= set(package["required_members"])
    assert package["content_addressing"] == "sha256"
    assert package["failed_evidence_policy"] == "append-successor-never-overwrite"
    assert record["retention"]["fixity_cadence"] == "before-transfer-and-on-restore"


def test_preservation_package_contract_does_not_claim_deposit() -> None:
    record = json.loads((ROOT / "docs/preservation-package-contract-20260822.json").read_text())
    assert any("not an independent deposit receipt" in claim for claim in record["non_claims"])
