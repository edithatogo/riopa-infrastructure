from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


def test_council_selection_is_heterogeneous_and_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "docs/nz-spatial-council-selection-20260825.json").read_text())
    councils = report["councils"]
    assert len(councils) == 4
    assert len({item["council"] for item in councils}) == 4
    assert len({item["mechanism"] for item in councils}) == 4
    assert report["promotion_allowed"] is False
    assert report["open_gates"]
    assert all(item["capture_status"] != "complete" for item in councils)
    for item in councils:
        source = urlparse(item["official_source"])
        assert source.scheme == "https"
        assert source.hostname is not None
        assert source.hostname.endswith(".govt.nz")


def test_council_selection_preserves_capture_and_authority_boundaries() -> None:
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / "docs/nz-spatial-council-selection-20260825.json").read_text())
    boundary = " ".join(report["non_claims"] + report["open_gates"]).lower()
    for required in ("rights", "legal", "complete", "external", "preservation"):
        assert required in boundary
