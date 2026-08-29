import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_wp010_closeout_uses_agent_panel_without_human_substitution() -> None:
    record = json.loads((ROOT / "docs/wp010-single-developer-closeout-20260829.json").read_text())

    assert record["work_package"] == "WP-010"
    assert record["status"] == "complete-bounded-repository-scope"
    assert all(value.startswith("passed") for value in record["acceptance"].values())
    assert "external person/operator" in record["supersedes"]["obsolete_requirement"]
    assert any("No other human" in claim for claim in record["non_claims"])
    assert any("elapsed beta" in gate for gate in record["remaining_track_gates"])


def test_live_wp010_register_no_longer_requires_external_operator() -> None:
    register = (ROOT / "docs/external-dependency-register.md").read_text()
    completion = (ROOT / "docs/evidence-completion-plan.md").read_text()

    assert "Closed for the bounded work package" in register
    assert "Complete for the bounded work package" in completion
    assert "Independent operator, clean-room logs" not in completion
