import hashlib
import json
from pathlib import Path

import pytest

from scripts.capture_wp010_public_sources import FetchResponse, capture


def test_capture_preserves_exact_raw_bytes_separately_from_canonical_json(tmp_path: Path) -> None:
    arcgis = b'{\n  "type": "FeatureCollection", "features": []\n}\n'
    overpass = b'{ "elements": [] }\n'

    def fetch(url: str, data: bytes | None) -> bytes:
        return overpass if data is not None else arcgis

    receipt = capture(tmp_path, fetch)

    for source, raw in zip(receipt["sources"], (arcgis, overpass), strict=True):
        raw_path = tmp_path / source["raw_file"]
        canonical_path = tmp_path / source["canonical_file"]
        assert raw_path.read_bytes() == raw
        assert source["raw_sha256"] == hashlib.sha256(raw).hexdigest()
        assert source["canonical_sha256"] == hashlib.sha256(canonical_path.read_bytes()).hexdigest()
        assert source["sha256"] == source["canonical_sha256"]
        assert raw_path.read_bytes() != canonical_path.read_bytes()


def test_capture_records_only_safe_bounded_response_metadata(tmp_path: Path) -> None:
    payloads = {
        "arcgis": b'{"features": [], "type": "FeatureCollection"}',
        "osm": b'{"elements": []}',
    }

    def fetch(url: str, data: bytes | None) -> FetchResponse:
        name = "osm" if data is not None else "arcgis"
        return FetchResponse(
            body=payloads[name],
            status=200,
            final_url=f"https://user:secret@example.test/{name}?token=secret#fragment",
            headers={
                "Content-Type": "application/json",
                "ETag": '"fixture"',
                "Authorization": "Bearer secret",
                "Set-Cookie": "session=secret",
            },
        )

    receipt = capture(tmp_path, fetch)

    for source, method in zip(receipt["sources"], ("GET", "POST"), strict=True):
        response = source["response"]
        assert response == {
            "method": method,
            "status": 200,
            "final_url": f"https://example.test/{'arcgis' if method == 'GET' else 'osm'}",
            "headers": {"content-type": "application/json", "etag": '"fixture"'},
        }
        assert "secret" not in json.dumps(response)


def test_content_addressed_raw_objects_are_reused_without_mutation(tmp_path: Path) -> None:
    arcgis = b'{"features": [], "type": "FeatureCollection"}'
    overpass = b'{"elements": []}'

    def fetch(url: str, data: bytes | None) -> bytes:
        return overpass if data is not None else arcgis

    first = capture(tmp_path, fetch)
    second = capture(tmp_path, fetch)

    assert [source["raw_file"] for source in first["sources"]] == [
        source["raw_file"] for source in second["sources"]
    ]
    assert sorted((tmp_path / "raw" / "sha256").iterdir()) == sorted(
        tmp_path / source["raw_file"] for source in first["sources"]
    )


def test_invalid_json_is_preserved_before_validation_fails(tmp_path: Path) -> None:
    invalid = b"<html>upstream failure</html>\n"

    def fetch(url: str, data: bytes | None) -> bytes:
        return invalid

    with pytest.raises(json.JSONDecodeError):
        capture(tmp_path, fetch)

    digest = hashlib.sha256(invalid).hexdigest()
    assert (tmp_path / "raw" / "sha256" / f"{digest}.bin").read_bytes() == invalid
