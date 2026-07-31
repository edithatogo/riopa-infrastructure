import json
from pathlib import Path

from scripts.capture_wp010_public_sources import capture


def test_capture_keeps_authority_and_rights_distinct(tmp_path: Path) -> None:
    arcgis = json.dumps(
        {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "properties": {"category": "Ambulance"}, "geometry": None}
            ],
        }
    ).encode()
    overpass = json.dumps(
        {
            "elements": [
                {"type": "node", "id": 1, "tags": {"shop": "supermarket"}},
                {"type": "node", "id": 2, "tags": {"emergency": "ambulance_station"}},
            ]
        }
    ).encode()

    def fetch(url: str, data: bytes | None) -> bytes:
        return overpass if data is not None else arcgis

    receipt = capture(tmp_path, fetch)
    assert receipt["operational_status"] == "exploratory-non-operational"
    assert receipt["sources"][0]["record_count"] == 1
    assert receipt["sources"][0]["authority"] == "regional-council-reference"
    assert receipt["sources"][1]["classification_counts"] == {
        "supermarket": 1,
        "ambulance_station": 1,
    }
    assert receipt["sources"][1]["authority"] == "community-non-authoritative"
    assert (tmp_path / "rangitikei-ambulance.geojson").is_file()
    assert (tmp_path / "osm-regional-pois.json").is_file()


def test_capture_canonicalises_source_bytes(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    responses = {
        "arcgis": b'{"features": [], "type": "FeatureCollection"}',
        "osm": b'{"elements": []}',
    }

    def fetch(url: str, data: bytes | None) -> bytes:
        return responses["osm" if data is not None else "arcgis"]

    left = capture(first, fetch)
    right = capture(second, fetch)
    assert [source["sha256"] for source in left["sources"]] == [
        source["sha256"] for source in right["sources"]
    ]
    assert (first / "rangitikei-ambulance.geojson").read_bytes() == (
        second / "rangitikei-ambulance.geojson"
    ).read_bytes()
