import json
from pathlib import Path


def test_documentation_contract_is_bounded_and_references_existing_files() -> None:
    root = Path(__file__).resolve().parents[1]
    contract = json.loads((root / "docs/documentation-contract-20260824.json").read_text())
    for key in ("audience_inventory", "tutorial_conventions"):
        assert (root / contract[key]).is_file()
    assert contract["python"] == "3.14"
    assert "no-credentials-or-live-payloads" in contract["required_controls"]
    assert set(contract["disabled_claims"]) == {
        "network",
        "timetable",
        "facility",
        "national",
        "clinical",
        "dispatch",
    }
