import json
from pathlib import Path


def test_template_adapter_examples_cover_four_additive_roles() -> None:
    root = Path(__file__).resolve().parents[1]
    fixture = json.loads(
        (root / "examples/template-adapters/adapter-examples.json").read_text(encoding="utf-8")
    )
    assert fixture["status"] == "example"
    assert {item["role"] for item in fixture["adapters"]} == {
        "connector",
        "archive",
        "transformation",
        "analytics",
    }
    for item in fixture["adapters"]:
        assert item["input"] and item["output"] and item["controls"]
    assert any("live endpoint" in claim for claim in fixture["nonclaims"])
