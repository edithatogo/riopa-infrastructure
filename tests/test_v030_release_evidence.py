import json
from pathlib import Path

from riopa_provenance.roadmap import release_readiness, validate_roadmap

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "conductor/release-evidence/0.3.0.json"


def test_v030_release_evidence_closes_only_experimental_m2_gates() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert evidence["release"] == "0.3.0"
    assert evidence["source_revision"] == "4c4214b348449ddf7f5d249ffa1d91f4eef7a59d"
    assert evidence["immutable_evidence_identifiers"] is False
    assert {gate["gate_id"] for gate in evidence["gates"]} == {
        "core-schema-conformance",
        "core-provenance-integrity",
        "core-security-baseline",
        "core-governance-baseline",
    }
    assert {gate["status"] for gate in evidence["gates"]} == {"passed"}
    assert all(gate["waiver"] is None for gate in evidence["gates"])
    assert evidence["metrics"] == {
        "agent_panel_analysts": 4,
        "clean_room_reproductions": 0,
        "external_reproductions": 0,
        "external_user_workflows": 0,
        "external_operator_workflows": 0,
        "operational_cycles": 0,
        "operational_evidence_days": 0,
        "release_candidate_soak_days": 0,
    }
    assert evidence["approvals"][0]["signed_decision_ref"] is None
    assert any("not a stable supported release" in item for item in evidence["known_limitations"])
    assert any("external reproduction" in item for item in evidence["known_limitations"])

    assert validate_roadmap(ROOT) == ()
    readiness = release_readiness(ROOT, "0.3.0")
    assert readiness.ready is True
    assert readiness.qualified_tracks == readiness.required_tracks == 5
    assert readiness.passed_gates == readiness.required_gates == 4
    assert readiness.blockers == ()


def test_later_release_gates_remain_fail_closed() -> None:
    for version in ("0.4.0", "0.5.0", "0.6.0", "0.7.0", "0.8.0", "0.9.0", "1.0.0"):
        readiness = release_readiness(ROOT, version)
        assert readiness.ready is False
        assert readiness.blockers
