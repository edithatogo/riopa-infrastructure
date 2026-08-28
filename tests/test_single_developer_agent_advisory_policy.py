import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs/single-developer-agent-advisory-policy-20260826.md"


def test_single_developer_policy_is_programme_wide_and_fail_closed() -> None:
    policy = POLICY.read_text(encoding="utf-8")
    tracks = (ROOT / "conductor/tracks.md").read_text(encoding="utf-8")
    workflow = (ROOT / "conductor/workflow.md").read_text(encoding="utf-8")

    assert "single-developer repository" in policy
    assert "No second human" in policy
    assert "advisory tools" in policy
    assert "No active or future track requires a second human" in policy
    assert "isolated clean-room reproduction requirements" in policy
    assert "Agents cannot establish" in policy
    assert "every active RIOPA Conductor track" in policy
    assert "single-developer-agent-advisory-policy-20260826.md" in tracks
    assert "This rule applies to every continuing track" in tracks
    assert "single-developer-agent-advisory-policy-20260826.md" in workflow


def test_active_track_language_does_not_treat_agents_as_independent_humans() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "conductor/tracks").glob("*/[a-z]*.md"))
    ).lower()

    assert "independent agent analyst" not in text
    assert "independent multi-agent" not in text
    assert "agent panel approves" not in text
    assert "agent-panel review and repository-owned" not in text


def test_panel_governance_preserves_external_fact_boundaries() -> None:
    decision = json.loads(
        (ROOT / "docs/sole-developer-panel-governance-20260827.json").read_text(encoding="utf-8")
    )
    rights = (ROOT / "docs/v0.4-source-rights-disposition-20260827.md").read_text(encoding="utf-8")

    assert decision["accountable_authority"] == "Sole repository owner"
    assert len(decision["required_panel_roles"]) == 5
    assert decision["operational_thresholds"] == {
        "beta_consecutive_days": 90,
        "beta_daily_hosted_observations": 90,
        "minimum_operational_cycles": 3,
        "failure_backfill_recovery_exercises": 1,
        "exact_candidate_soak_days": 30,
        "exact_candidate_daily_hosted_observations": 30,
    }
    assert "Churton Park Village Supermarket" in rights
    assert "no licence is declared" in " ".join(rights.split())
    assert "cannot grant a missing licence" in rights
