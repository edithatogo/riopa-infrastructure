import json
from pathlib import Path


def test_v1_closeout_packet_links_existing_bounded_evidence() -> None:
    root = Path(__file__).resolve().parents[1]
    packet = json.loads(
        (root / "docs/v1-release-closeout-evidence-20260825.json").read_text(encoding="utf-8")
    )
    assert packet["status"] == "bounded-candidate-not-promoted"
    assert packet["promotion_allowed"] is False
    for group in ("implementation", "tests_and_review", "migration_and_release"):
        assert packet[group]
        assert all((root / path).exists() for path in packet[group])
    assert any("90-day" in gate for gate in packet["open_gates"])
    assert any("accountable" in gate for gate in packet["open_gates"])
