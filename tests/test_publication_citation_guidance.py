import json
from pathlib import Path


def test_publication_citation_guidance_remains_preview_bounded() -> None:
    root = Path(__file__).resolve().parents[1]
    guidance = json.loads((root / "docs/publication-citation-guidance-20260825.json").read_text())
    assert guidance["status"] == "preview-guidance-not-stable-publication"
    assert guidance["persistent_identifier"]["status"] == "pending-for-stable-publication"
    assert "archived packet" in guidance["data_citation"]["live_endpoint_policy"]
    assert guidance["promotion_allowed"] is False
    assert any("external" in gate for gate in guidance["open_gates"])
