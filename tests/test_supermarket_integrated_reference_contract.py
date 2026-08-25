import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/supermarket-integrated-reference-contract-20260825.json"


def test_integrated_reference_contract_binds_implementation_and_negative_tests() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert contract["track_id"] == "supermarket_health_pilot_20260718"
    assert contract["promotion_allowed"] is False
    assert {item["control"] for item in contract["implemented_controls"]} == {
        "access-health-binding",
        "planning-alternatives-binding",
    }
    assert "tampered planning-rule digest" in contract["validation"]["negative_cases"]


def test_integrated_reference_contract_preserves_empirical_and_authority_gates() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    gates = " ".join(contract["remaining_gates"])
    assert "five blocking dependency tracks" in gates
    assert "rights-cleared" in gates
    assert "operative planning provisions" in gates
    assert "empirical ecological-health" in gates
    assert "agent-panel and independent reproduction" in gates
    assert "publication and release authority" in gates
    assert any("does not acquire data" in item for item in contract["nonclaims"])
