import json
from pathlib import Path


def test_publication_version_coordination_covers_all_component_kinds() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (root / "docs/publication-version-coordination-20260825.json").read_text()
    )
    assert manifest["status"] == "candidate-coordination"
    assert {item["kind"] for item in manifest["components"]} == {
        "software",
        "schema",
        "ontology",
        "data",
        "model",
        "research-object",
    }
    assert all(item["version_source"] for item in manifest["components"])
    assert manifest["components"][4]["version"] == "not-applicable"
    assert any("preservation" in item for item in manifest["required_before_publication"])
    assert any("not a publication" in item for item in manifest["nonclaims"])
