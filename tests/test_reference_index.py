import json
from pathlib import Path


def test_reference_index_is_versioned_and_points_to_existing_surfaces() -> None:
    root = Path(__file__).resolve().parents[1]
    index = json.loads((root / "docs/reference-index-20260825.json").read_text(encoding="utf-8"))
    assert index["python"] == "3.14"
    assert index["scope"] == "bounded-regional-public-preview"
    for relative in (
        index["surfaces"]["schemas"]["directory"],
        index["surfaces"]["ontology"]["context"],
        index["surfaces"]["ontology"]["release"],
        index["surfaces"]["ontology"]["migration_directory"],
    ):
        assert (root / relative).exists()
    assert set(index["controls"]["disabled_claims"]) == {
        "network",
        "timetable",
        "facility",
        "national",
        "clinical",
        "dispatch",
    }
