import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_sdk_support_surface_and_unsigned_report_boundary_are_explicit() -> None:
    guidance = (ROOT / "docs/interoperability-v1-sdk-support-and-reporting-20260825.md").read_text()
    contract = json.loads(
        (ROOT / "docs/interoperability-v1-sdk-support-contract-20260825.json").read_text()
    )
    assert "riopa_provenance.sdk" in guidance
    assert "rust/riopa-conformance" in guidance
    assert contract["support_owner"] == "single repository maintainer"
    assert contract["agent_panel_role"] == "evidence assessment and findings only"
    assert "external producer/consumer reproduction" in guidance
    assert "unsigned repository evidence" in guidance
    assert contract["promotion_allowed"] is False
