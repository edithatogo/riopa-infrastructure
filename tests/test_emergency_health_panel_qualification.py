import json
from pathlib import Path


def test_emergency_health_panel_packet_is_bounded_and_fail_closed() -> None:
    packet = json.loads(
        Path("docs/emergency-health-panel-qualification-20260825.json").read_text(encoding="utf-8")
    )
    assert packet["status"] == "bounded-agent-panel-not-qualified"
    assert packet["promotion_allowed"] is False
    assert len(packet["lenses"]) == 4
    assert any("external operator" in gate for gate in packet["open_gates"])
    assert any("clinical" in gate for gate in packet["open_gates"])


def test_emergency_health_research_object_candidate_is_unpublished() -> None:
    packet = json.loads(
        Path("docs/emergency-health-research-object-candidate-20260825.json").read_text(
            encoding="utf-8"
        )
    )
    assert packet["status"] == "unpublished-candidate"
    assert packet["promotion_allowed"] is False
    assert "src/riopa_provenance/analysis.py" in packet["included_artifacts"]
    assert any("not a published" in claim for claim in packet["non_claims"])
