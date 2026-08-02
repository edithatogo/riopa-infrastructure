import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_hugging_face_runner_remains_staged_and_fail_closed() -> None:
    plan = json.loads((ROOT / "docs/hugging-face-evidence-runner-plan-20260802.json").read_text())
    assert plan["status"] == "staged-not-submitted"
    assert plan["observed_jobs"] == []
    assert (
        plan["dataset_search_observations"]["authoritative_nz_geospatial_workload_found"] is False
    )
    assert len(plan["non_claims"]) >= 4


def test_operational_observation_schedule_is_daily_and_read_only() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/evidence-campaign.yml").read_text())
    triggers = workflow.get("on", workflow.get(True))
    assert triggers["schedule"] == [{"cron": "17 14 * * *"}]
    assert workflow["permissions"] == {"actions": "read", "contents": "read"}
    steps = workflow["jobs"]["observe"]["steps"]
    assert any(step.get("name") == "Build cumulative fail-closed campaign ledger" for step in steps)


def test_normative_track_sources_use_agent_panel_qualification() -> None:
    forbidden = (
        "independent review",
        "scientific review",
        "human review",
        "public and maintainer review",
    )
    for path in (ROOT / "conductor" / "tracks").rglob("*"):
        if path.is_file() and path.suffix in {".json", ".md"}:
            text = path.read_text().lower()
            assert not any(term in text for term in forbidden), path


def test_machine_readable_gate_uses_agent_panel_metric() -> None:
    gate = json.loads((ROOT / "conductor/v1-gate.json").read_text())
    evidence = json.loads(
        (ROOT / "conductor/release-evidence/1.0.0.template.json.example").read_text()
    )
    assert gate["evidence_policy"]["minimum_agent_panel_analysts"] == 2
    assert "minimum_independent_reviewers" not in gate["evidence_policy"]
    assert "agent_panel_analysts" in evidence["metrics"]


def test_programme_mirrors_match_normative_conductor_contracts() -> None:
    for name in ("maturity-model.json", "releases.json", "v1-gate.json"):
        assert (ROOT / "programme" / name).read_bytes() == (ROOT / "conductor" / name).read_bytes()


def test_generated_issue_bodies_do_not_reintroduce_human_review_gates() -> None:
    issues = yaml.safe_load((ROOT / "project/issues.yaml").read_text())["issues"]
    bodies = "\n".join(issue["body"].lower() for issue in issues)
    assert "independent reviewer" not in bodies
    assert "scientific review" not in bodies
    assert "human review" not in bodies
