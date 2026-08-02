import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_operational_lanes_link_existing_readiness_artifacts() -> None:
    campaign = json.loads((ROOT / "docs/operational-evidence-campaign-20260802.json").read_text())
    lanes = {lane["id"]: lane for lane in campaign["lanes"]}
    for lane_id in ("public-source-packets", "recovery-rollback", "regional-performance"):
        artifact = lanes[lane_id].get("artifact") or lanes[lane_id].get("readiness_artifact")
        assert artifact and (ROOT / artifact).exists()
    assert (
        lanes["recovery-rollback"]["status"]
        == "hosted-technical-preview-passed-production-dr-pending"
    )
    assert lanes["regional-performance"]["status"] == "synthetic-regional-only"


def test_release_packet_tracks_campaign_and_pending_authority() -> None:
    packet = json.loads((ROOT / "docs/release-packet-readiness-20260802.json").read_text())
    campaign = json.loads((ROOT / packet["campaign_manifest"]).read_text())
    assert packet["release_ready"] is False
    assert packet["release_authority"] == "pending"
    assert campaign["campaign_id"] == "operational-evidence-20260802"
    assert "accountable release-authority decision" in packet["pending_gates"]
