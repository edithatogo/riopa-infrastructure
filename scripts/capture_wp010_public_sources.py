#!/usr/bin/env python3
"""Capture bounded WP-010 public-source evidence into an ignored local directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ARCGIS_URL = (
    "https://services8.arcgis.com/rH83DoI7Xdq2nG28/arcgis/rest/services/"
    "CIVIC_civic_facilities_viewing_view/FeatureServer/3/query"
)
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_QUERY = """[out:json][timeout:60];
(
  nwr[\"shop\"=\"supermarket\"](-40.30,175.15,-39.50,176.10);
  nwr[\"emergency\"=\"ambulance_station\"](-40.30,175.15,-39.50,176.10);
  nwr[\"amenity\"=\"ambulance_station\"](-40.30,175.15,-39.50,176.10);
);
out center tags;
"""

SAFE_RESPONSE_HEADERS = frozenset(
    {"content-length", "content-type", "date", "etag", "last-modified"}
)


@dataclass(frozen=True)
class FetchResponse:
    """Fetched bytes plus a deliberately bounded set of transport metadata."""

    body: bytes
    status: int | None
    final_url: str
    headers: dict[str, str]


type FetchResult = bytes | FetchResponse
type Fetch = Callable[[str, bytes | None], FetchResult]


def _fetch(url: str, data: bytes | None = None) -> FetchResponse:
    request = urllib.request.Request(
        url,
        data=data,
        headers={"User-Agent": "riopa-wp010-evidence/1.0 (research; contact via repository)"},
        method="POST" if data is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=90) as response:  # nosec B310
        return FetchResponse(
            body=bytes(response.read()),
            status=response.status,
            final_url=response.geturl(),
            headers={key: value for key, value in response.headers.items()},
        )


def _safe_url(url: str) -> str:
    """Remove credentials, query parameters and fragments from receipt URLs."""
    parsed = urllib.parse.urlsplit(url)
    hostname = parsed.hostname or ""
    if ":" in hostname:
        hostname = f"[{hostname}]"
    netloc = f"{hostname}:{parsed.port}" if parsed.port is not None else hostname
    return urllib.parse.urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))


def _safe_header_value(value: str) -> str:
    cleaned = "".join(character if ord(character) >= 32 else " " for character in value)
    return cleaned[:512]


def _coerce_response(result: FetchResult, *, requested_url: str) -> FetchResponse:
    if isinstance(result, bytes):
        return FetchResponse(body=result, status=None, final_url=requested_url, headers={})
    return result


def _response_metadata(response: FetchResponse, *, method: str) -> dict[str, Any]:
    headers = {
        key.lower(): _safe_header_value(value)
        for key, value in response.headers.items()
        if key.lower() in SAFE_RESPONSE_HEADERS
    }
    return {
        "method": method,
        "status": response.status,
        "final_url": _safe_url(response.final_url),
        "headers": dict(sorted(headers.items())),
    }


def _preserve_raw(output: Path, payload: bytes) -> tuple[str, str]:
    """Persist exact response bytes at a content-addressed, append-safe path."""
    digest = hashlib.sha256(payload).hexdigest()
    relative_path = Path("raw") / "sha256" / f"{digest}.bin"
    destination = output / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.read_bytes() != payload:
            raise ValueError(f"content-addressed raw object mismatch: {relative_path}")
    else:
        destination.write_bytes(payload)
    return relative_path.as_posix(), digest


def _capture_json(
    output: Path,
    *,
    url: str,
    data: bytes | None,
    fetch: Fetch,
) -> tuple[bytes, dict[str, Any], str, str, dict[str, Any]]:
    response = _coerce_response(fetch(url, data), requested_url=url)
    raw_file, raw_digest = _preserve_raw(output, response.body)
    canonical_bytes, parsed = _canonical_json(response.body)
    metadata = _response_metadata(response, method="POST" if data is not None else "GET")
    return canonical_bytes, parsed, raw_file, raw_digest, metadata


def _canonical_json(payload: bytes) -> tuple[bytes, dict[str, Any]]:
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("source response must be a JSON object")
    return (
        json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(),
        parsed,
    )


def capture(output: Path, fetch: Fetch = _fetch) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    arcgis_query = urllib.parse.urlencode(
        {
            "f": "geojson",
            "where": "upper(category) like '%AMBULANCE%'",
            "outFields": "OBJECTID,category,town,label,GlobalID",
            "returnGeometry": "true",
            "outSR": "4326",
        }
    )
    arcgis_bytes, arcgis, arcgis_raw_file, arcgis_raw_digest, arcgis_response = _capture_json(
        output,
        url=f"{ARCGIS_URL}?{arcgis_query}",
        data=None,
        fetch=fetch,
    )
    overpass_bytes, overpass, overpass_raw_file, overpass_raw_digest, overpass_response = (
        _capture_json(
            output,
            url=OVERPASS_URL,
            data=urllib.parse.urlencode({"data": OVERPASS_QUERY}).encode(),
            fetch=fetch,
        )
    )
    (output / "rangitikei-ambulance.geojson").write_bytes(arcgis_bytes)
    (output / "osm-regional-pois.json").write_bytes(overpass_bytes)

    features = arcgis.get("features", [])
    elements = overpass.get("elements", [])
    osm_counts = {"supermarket": 0, "ambulance_station": 0}
    for element in elements if isinstance(elements, list) else []:
        tags = element.get("tags", {}) if isinstance(element, dict) else {}
        if tags.get("shop") == "supermarket":
            osm_counts["supermarket"] += 1
        if (
            tags.get("emergency") == "ambulance_station"
            or tags.get("amenity") == "ambulance_station"
        ):
            osm_counts["ambulance_station"] += 1

    receipt = {
        "schema_version": "1.0.0",
        "record_type": "wp010_public_source_receipt",
        "captured_at": datetime.now(UTC).isoformat(),
        "operational_status": "exploratory-non-operational",
        "sources": [
            {
                "source_id": "urn:riopa:source:rangitikei:public-facilities",
                "local_file": "rangitikei-ambulance.geojson",
                "sha256": hashlib.sha256(arcgis_bytes).hexdigest(),
                "canonical_file": "rangitikei-ambulance.geojson",
                "canonical_sha256": hashlib.sha256(arcgis_bytes).hexdigest(),
                "raw_file": arcgis_raw_file,
                "raw_sha256": arcgis_raw_digest,
                "response": arcgis_response,
                "record_count": len(features) if isinstance(features, list) else 0,
                "licence": "CC-BY-4.0",
                "authority": "regional-council-reference",
            },
            {
                "source_id": "urn:riopa:source:osm:nz-regional-pilot-pois",
                "local_file": "osm-regional-pois.json",
                "sha256": hashlib.sha256(overpass_bytes).hexdigest(),
                "canonical_file": "osm-regional-pois.json",
                "canonical_sha256": hashlib.sha256(overpass_bytes).hexdigest(),
                "raw_file": overpass_raw_file,
                "raw_sha256": overpass_raw_digest,
                "response": overpass_response,
                "record_count": len(elements) if isinstance(elements, list) else 0,
                "classification_counts": osm_counts,
                "licence": "ODbL-1.0",
                "authority": "community-non-authoritative",
            },
        ],
        "limitations": [
            "The regional council layer was manually captured in June 2023.",
            "OpenStreetMap completeness, tagging and currency are not guaranteed.",
            "No source is suitable for operational dispatch or national completeness claims.",
        ],
    }
    (output / "receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".riopa-local/wp010/public-source-capture"),
    )
    args = parser.parse_args()
    receipt = capture(args.output.resolve())
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
