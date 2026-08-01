#!/usr/bin/env python3
"""Summarise the bounded WP-010 council/OSM facility comparison without coordinates."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from riopa_provenance.facility_registry import FacilityAssertion, reconcile


def _load(path: Path) -> tuple[dict[str, Any], str]:
    payload = path.read_bytes()
    value = json.loads(payload)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    canonical = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return value, hashlib.sha256(canonical).hexdigest()


def compare(council_path: Path, osm_path: Path) -> dict[str, Any]:
    council, council_hash = _load(council_path)
    osm, osm_hash = _load(osm_path)
    council_assertions = tuple(
        FacilityAssertion(
            assertion_id=f"rangitikei:{feature['properties']['GlobalID']}",
            source_id="urn:riopa:source:rangitikei:public-facilities",
            facility_type="ambulance-station",
            name=str(feature["properties"]["label"]),
            latitude=float(feature["geometry"]["coordinates"][1]),
            longitude=float(feature["geometry"]["coordinates"][0]),
            authority="official-reference",
            licence="CC-BY-4.0",
        )
        for feature in council.get("features", [])
    )
    osm_assertions = []
    for element in osm.get("elements", []):
        tags = element.get("tags", {})
        if not (
            tags.get("emergency") == "ambulance_station"
            or tags.get("amenity") == "ambulance_station"
        ):
            continue
        coordinates = element.get("center", element)
        osm_assertions.append(
            FacilityAssertion(
                assertion_id=f"osm:{element['type']}:{element['id']}",
                source_id="urn:riopa:source:osm:nz-regional-pilot-pois",
                facility_type="ambulance-station",
                name=str(tags.get("name", "unnamed ambulance station")),
                latitude=float(coordinates["lat"]),
                longitude=float(coordinates["lon"]),
                authority="community-reference",
                licence="ODbL-1.0",
            )
        )
    results = reconcile(council_assertions, tuple(osm_assertions))
    matches = [item for item in results if item.disposition == "candidate-match"]
    return {
        "schema_version": "1.0.0",
        "record_type": "wp010_non_authoritative_facility_comparison",
        "method": "riopa-name-distance-v1",
        "thresholds": {"maximum_distance_m": 250.0, "minimum_name_similarity": 0.5},
        "source_hashes": {"council": council_hash, "osm": osm_hash},
        "counts": {
            "council_assertions": len(council_assertions),
            "osm_assertions": len(osm_assertions),
            "candidate_matches": len(matches),
            "source_only": sum(item.disposition == "source-only" for item in results),
        },
        "candidate_distances_m": sorted(item.distance_m for item in matches),
        "limitations": [
            "Candidate matches are not adjudicated or authoritative registry records.",
            "The comparison is spatially bounded and does not measure national completeness.",
            "Coordinates and raw source payloads are intentionally omitted from this summary.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("council", type=Path)
    parser.add_argument("osm", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(compare(args.council, args.osm), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
