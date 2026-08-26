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
    assert "independent external reproduction" in policy
    assert "cannot by itself" in policy
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
