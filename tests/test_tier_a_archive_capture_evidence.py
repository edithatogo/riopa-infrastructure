import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_tier_a_capture_evidence_is_bounded_and_fail_closed() -> None:
    evidence = json.loads((ROOT / "docs/tier-a-archive-capture-evidence-20260829.json").read_text())
    assert evidence["status"] == "locally-captured-publication-pending"
    assert evidence["publication_gate"]["status"] == "pending"
    assert evidence["publication_gate"]["promotion_allowed"] is False
    assert len(evidence["sources"]) == 3
    for source in evidence["sources"]:
        assert re.fullmatch(r"[0-9a-f]{64}", source["manifest_sha256"])
        assert source["capture_window_utc"][0] <= source["capture_window_utc"][1]
        assert source["capture_set"].startswith(".riopa-local/publication/")
        assert source["licence"] in {"CC-BY-3.0-NZ", "CC-BY-4.0"}
