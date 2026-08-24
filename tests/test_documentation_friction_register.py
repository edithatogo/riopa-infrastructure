import json
from pathlib import Path


def test_documentation_friction_register_is_bounded() -> None:
    root = Path(__file__).resolve().parents[1]
    register = json.loads((root / "docs/documentation-friction-register-20260825.json").read_text())
    assert register["status"] == "anticipated-friction-not-external-study"
    assert len(register["items"]) == 3
    assert register["external_study_status"] == "not conducted"
    assert register["promotion_allowed"] is False
    assert any("external" in gate for gate in register["open_gates"])
