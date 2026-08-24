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


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("status", "running", "status is unsupported"),
        ("final_disposition", "approved", "final_disposition is unsupported"),
        ("non_assertive", False, "non_assertive must be true"),
        ("reports", {}, "reports must be an array"),
    ],
)
def test_panel_packet_rejects_unsupported_control_values(
    field: str, value: object, message: str
) -> None:
    packet = build_panel_rerun_packet(source_revision="a" * 40)
    packet[field] = value
    assert message in validate_panel_rerun_packet(packet)


def test_panel_packet_rejects_malformed_reports_and_missing_complete_roles() -> None:
    packet = build_panel_rerun_packet(source_revision="a" * 40)
    packet["status"] = "complete"
    packet["final_disposition"] = "qualified"
    packet["reports"] = [
        None,
        {
            "role": "unknown",
            "source_revision": "b" * 40,
            "report_id": "",
            "sha256": "Z" * 64,
            "findings": {},
        },
        {
            "role": "reproducer",
            "source_revision": "a" * 40,
            "report_id": "reproducer-1",
            "sha256": "d" * 64,
            "findings": [],
        },
        {
            "role": "reproducer",
            "source_revision": "a" * 40,
            "report_id": "reproducer-2",
            "sha256": "e" * 64,
            "findings": [],
        },
    ]
    packet["synthesis"] = {"sha256": "not-a-digest"}
    errors = validate_panel_rerun_packet(packet)
    assert "each report must be an object" in errors
    assert "report role is unsupported" in errors
    assert "report roles must be unique" in errors
    assert "report_id is required" in errors
    assert "report sha256 must be a lowercase digest" in errors
    assert "report findings must be an array" in errors
    assert "complete packet requires all three panel roles" in errors
    assert "synthesis sha256 must be a lowercase digest" in errors


def test_panel_packet_rejects_missing_required_fields() -> None:
    errors = validate_panel_rerun_packet({})
    assert "batch_id is required" in errors
    assert "source_revision is required" in errors
    assert "status is required" in errors
    assert "final_disposition is required" in errors
