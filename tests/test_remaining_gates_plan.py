import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_remaining_gates_plan_is_fail_closed() -> None:
    plan = json.loads((ROOT / "docs/remaining-gates-autonomous-plan-20260802.json").read_text())
    gates = {gate["id"]: gate for gate in plan["gates"]}
    assert {
        "hosted-recovery",
        "operational-cycles-and-rc-soak",
        "national-scale-performance",
        "external-operator-and-user-workflows",
        "panel-qualification",
        "release-authority",
        "cross-track-completion",
    } == set(gates)
    assert all(gate["non_claim"] for gate in gates.values())
    assert plan["remote_actions"]["hugging_face_job_submitted"] is False
    assert plan["remote_actions"]["hugging_face_dataset_created"] is False


def test_conductor_review_roles_are_agent_panel_lenses() -> None:
    forbidden = ("human review", "external reviewers", "Scientific reviewer")
    for path in (ROOT / "conductor" / "tracks").rglob("metadata.json"):
        metadata = json.loads(path.read_text())
        assert all(not role.endswith(" reviewer") for role in metadata["review_roles"]), path
    for path in (ROOT / "conductor").rglob("*"):
        if (
            path.is_file()
            and path.suffix in {".json", ".md"}
            and "release-evidence/artifacts" not in path.as_posix()
        ):
            assert not any(term in path.read_text() for term in forbidden), path


def test_runtime_dependency_decision_is_conservative() -> None:
    plan = json.loads((ROOT / "docs/remaining-gates-autonomous-plan-20260802.json").read_text())
    assert "duckdb" in plan["library_decision"]["retain"]
    assert "huggingface_hub" in plan["library_decision"]["conditional"]
    assert "Do not add runtime dependencies" in plan["library_decision"]["decision"]
