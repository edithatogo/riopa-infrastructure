import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _campaign() -> dict:
    return json.loads((ROOT / "docs/remaining-gates-campaign-v3-20260802.json").read_text())


def test_campaign_v3_matches_current_hosted_snapshot() -> None:
    campaign = _campaign()
    assert campaign["schema"] == "riopa.remaining-gates-campaign.v3"
    assert campaign["mode"] == "single-developer-agent-panel"
    assert campaign["github"]["open_pull_requests"] == 0
    assert campaign["github"]["open_issues"] == 141
    assert campaign["github"]["open_track_parents"] == 28
    assert len(campaign["github"]["completed_phase_issues_closed_in_campaign"]) == 14
    assert campaign["github"]["continuous_integration"]["conclusion"] == "success"
    assert campaign["github"]["codeql"]["conclusion"] == "success"


def test_hugging_face_failure_is_fail_closed() -> None:
    hugging_face = _campaign()["hugging_face"]
    assert hugging_face["attempted_runner"]["result"] == "not-created"
    assert "402" in hugging_face["attempted_runner"]["error"]
    assert hugging_face["billable_job_created"] is False
    assert hugging_face["authoritative_nz_geospatial_workload_found"] is False


def test_every_remaining_gate_has_action_contingency_and_non_claim() -> None:
    campaign = _campaign()
    gates = {gate["id"]: gate for gate in campaign["gates"]}
    assert set(gates) == {
        "agent-panel-qualification",
        "operational-beta",
        "release-candidate-soak",
        "hosted-recovery",
        "national-scale-performance",
        "external-workflow-facts",
        "release-authority",
        "cross-track-implementation",
    }
    assert all(gate["next_action"] for gate in gates.values())
    assert all(gate["contingency"] for gate in gates.values())
    assert all(gate["non_claim"] for gate in gates.values())


def test_library_growth_remains_evidence_driven() -> None:
    decision = _campaign()["library_decision"]
    assert {"pyperf", "psutil"} == set(decision["benchmark_only_when_consumed"])
    assert {"huggingface_hub", "fsspec"} == set(decision["conditional_in_process_hub_access"])
    assert "datasets" in decision["not_recommended_now"]
