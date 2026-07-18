from pathlib import Path

from riopa_provenance.methods import generate_methods_markdown


def test_methods_are_generated_from_manifest() -> None:
    root = Path(__file__).resolve().parents[1]
    text = generate_methods_markdown(root / "examples/minimal/snapshot-manifest.json")
    assert "Citable methods statement" in text
    assert "not yet assigned" in text
    assert "LINZ Data Service" in text
    assert "semantic reconstruction is expected" in text
    assert "No council plan or legal operative status" in text
