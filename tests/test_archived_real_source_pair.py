from __future__ import annotations

from pathlib import Path

from scripts.validate_archived_real_source_pair import build_packet


def test_archived_public_source_pair_is_content_bound_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    packet = build_packet(root)
    assert packet["status"] == "archived-inputs-validated-live-acceptance-pending"
    assert packet["promotion_allowed"] is False
    assert packet["sources"]["national"]["capture_record_count"] > 0
    assert packet["sources"]["council_planning"]["feature_count"] == 1
    assert len(packet["file_sha256"]) == 4
    assert any("preservation" in gate for gate in packet["open_gates"])
