import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_facility_panel_frame_is_digest_bound_and_promotion_disabled() -> None:
    packet = json.loads(
        (ROOT / "docs/facility-panel-frame-qualification-20260825.json").read_text()
    )
    assert packet["schema"] == "riopa.facility-panel-frame-qualification.v1"
    assert packet["input_frame"]["total_sample_size"] == 741
    assert len(packet["input_frame"]["selection_frame_sha256"]) == 64
    assert packet["decisions"]["reviewed_matches"] == 0
    assert packet["decisions"]["promotion_allowed"] is False
    assert len(packet["panel"]) == 4
    assert "factual review" in packet["open_gates"][0]
