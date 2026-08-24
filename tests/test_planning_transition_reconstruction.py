import json
from pathlib import Path

from riopa_provenance.transitions import validate_transition


def test_synthetic_reconstruction_covers_authority_and_plan_cases() -> None:
    root = Path(__file__).resolve().parents[1]
    packet = json.loads((root / "fixtures/planning-transition-reconstruction.json").read_text())
    assert packet["status"] == "synthetic-reconstruction"
    assert {case["reconstruction_type"] for case in packet["cases"]} == {
        "authority-reorganisation",
        "plan-replacement",
    }
    assert all(validate_transition(case["transition"]) == () for case in packet["cases"])
    assert all(case["evidence_class"] == "synthetic-reference" for case in packet["cases"])
