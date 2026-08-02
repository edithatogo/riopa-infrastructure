import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_hosted_recovery_packet_is_fail_closed() -> None:
    packet = json.loads((ROOT / "docs/hosted-recovery-readiness-20260802.json").read_text())
    assert packet["status"] == "ready-pending-hosted-execution"
    assert packet["hosted_execution"]["status"] == "pending"
    assert packet["hosted_execution"]["promotion_effect"] == "blocking"
    assert "raw-log" in packet["required_artifacts"]


def test_regional_performance_packet_rejects_national_claim() -> None:
    packet = json.loads((ROOT / "docs/regional-performance-evidence-20260802.json").read_text())
    assert packet["status"] == "synthetic-regional-only"
    assert packet["regional"]["checksum"] == 2665628609
    assert packet["national"]["classification"] == "projection-not-measurement"
    assert packet["national"]["claim_supported"] is False
