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


def test_hugging_face_runner_v2_is_pinned_and_fail_closed() -> None:
    plan = json.loads(
        (ROOT / "docs/hugging-face-evidence-runner-plan-v2-20260802.json").read_text()
    )
    assert plan["status"] == "submission-blocked-prepaid-credit"
    assert plan["job_spec"]["image"].startswith("python:3.13-slim@sha256:")
    assert plan["job_spec"]["secrets"] == []
    assert plan["job_spec"]["maximum_cost_usd_at_timeout"] <= 0.002
    assert plan["submission_attempt"]["billable_job_created"] is False


def test_operational_observation_schedule_is_daily_and_read_only() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/evidence-campaign.yml").read_text())
    triggers = workflow.get("on", workflow.get(True))
    assert triggers["schedule"] == [{"cron": "17 14 * * *"}]
    assert workflow["permissions"] == {"actions": "read", "contents": "read"}
    steps = workflow["jobs"]["observe"]["steps"]
    assert any(step.get("name") == "Build cumulative fail-closed campaign ledger" for step in steps)
    inputs = triggers["workflow_dispatch"]["inputs"]
    candidate = "26bc0b49bcd84f409bf24b527e1049fd396c94a6"
    assert inputs["campaign_id"]["default"] == "operational-beta-20260825-26bc0b4"
    assert inputs["candidate_revision"]["default"] == candidate
    assert inputs["qualification_epoch"]["default"] == "beta-epoch-20260825-26bc0b4"
    environment = workflow["jobs"]["observe"]["env"]
    assert candidate in inputs["candidate_revision"]["default"]
    assert "github.sha" in environment["EVIDENCE_CANDIDATE_REVISION"]
    assert "format('operational-beta-{0}', github.sha)" in environment["EVIDENCE_CAMPAIGN_ID"]
    assert "format('beta-epoch-{0}', github.sha)" in environment["EVIDENCE_QUALIFICATION_EPOCH"]


def test_rc_soak_checks_out_the_content_addressed_candidate_revision() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/evidence-campaign.yml").read_text())
    steps = workflow["jobs"]["observe"]["steps"]
    checkout = next(step for step in steps if step.get("name") == "Check out exact revision")
    assert checkout["with"]["ref"] == "${{ env.EVIDENCE_CANDIDATE_REVISION || github.sha }}"
    assert any(step.get("name") == "Verify exact RC candidate checkout" for step in steps)


def test_campaign_concurrency_isolated_by_campaign_lane_and_rc_candidate() -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/evidence-campaign.yml").read_text())
    group = workflow["concurrency"]["group"]
    assert "campaign_id" in group
    assert "lane" in group
    assert "candidate_revision" in group
    assert workflow["concurrency"]["cancel-in-progress"] is True


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
    assert gate["evidence_policy"]["minimum_agent_panel_analysts"] == 5
    assert "minimum_independent_reviewers" not in gate["evidence_policy"]
    assert "minimum_external_reproductions" not in gate["evidence_policy"]
    assert gate["release_authority"]["required_roles"] == ["Sole repository owner"]
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
