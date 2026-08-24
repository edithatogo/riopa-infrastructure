import pytest

from riopa_provenance.security_panel import (
    SecurityPanelPacketError,
    build_panel_rerun_packet,
    validate_panel_rerun_packet,
)


def test_panel_rerun_packet_starts_pending_and_non_assertive() -> None:
    packet = build_panel_rerun_packet(source_revision="a" * 40)
    assert packet["status"] == "pending"
    assert packet["non_assertive"] is True
    assert validate_panel_rerun_packet(packet) == ()


def test_complete_panel_packet_requires_distinct_digest_bound_roles() -> None:
    packet = build_panel_rerun_packet(source_revision="a" * 40)
    packet["status"] = "complete"
    packet["final_disposition"] = "not-qualified"
    packet["reports"] = [
        {
            "role": role,
            "source_revision": "a" * 40,
            "report_id": f"{role}-1",
            "sha256": "b" * 64,
            "findings": [],
        }
        for role in packet["required_roles"]
    ]
    packet["synthesis"] = {"sha256": "c" * 64}
    assert validate_panel_rerun_packet(packet) == ()
    packet["reports"][0]["source_revision"] = "d" * 40
    assert any("source revisions" in error for error in validate_panel_rerun_packet(packet))
    with pytest.raises(SecurityPanelPacketError, match="source revision"):
        build_panel_rerun_packet(source_revision="")
