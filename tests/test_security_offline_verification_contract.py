import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_offline_verification_contract_is_explicit_and_fail_closed() -> None:
    record = json.loads(
        (ROOT / "docs/security-offline-verification-contract-20260822.json").read_text()
    )
    names = {item["name"] for item in record["verification_commands"]}
    assert names == {"checksum", "github-attestation"}
    assert "exact release asset" in record["required_inputs"]
    assert any("not evidence" in claim for claim in record["non_claims"])
