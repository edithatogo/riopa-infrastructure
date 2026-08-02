#!/usr/bin/env python3
"""Run deterministic, non-authoritative matching for OSM and Marlborough packets."""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

from riopa_provenance.facility_registry import FacilityAssertion, reconcile

BASE = "https://huggingface.co/datasets/edithatogo/riopa-public-data-archive/resolve"
PACKETS = {
    "osm-new-zealand-food-service": "d834601efedada86be03dee2ff7a90d0fa37c0a2",
    "marlborough-food-premise-licences": "b31703eb0dbdaa6aa05b6a84df5fe46e57e37ee0",
}


def load(source_id: str, revision: str) -> object:
    url = f"{BASE}/{revision}/snapshots/{source_id}/payload"
    with urllib.request.urlopen(url, timeout=120) as response:
        return json.loads(response.read())


def assertions() -> tuple[tuple[FacilityAssertion, ...], tuple[FacilityAssertion, ...]]:
    osm = load("osm-new-zealand-food-service", PACKETS["osm-new-zealand-food-service"])
    council = load(
        "marlborough-food-premise-licences",
        PACKETS["marlborough-food-premise-licences"],
    )
    left = tuple(
        FacilityAssertion(
            assertion_id=f"osm:{item['meta_osm_id']}",
            source_id="osm-new-zealand-food-service",
            facility_type="food-premise",
            name=str(item.get("name") or "unnamed"),
            latitude=float(item["meta_geo_point"]["lat"]),
            longitude=float(item["meta_geo_point"]["lon"]),
            authority="community-reference",
            licence="ODbL-1.0",
        )
        for item in osm
        if item.get("meta_geo_point")
    )
    right = tuple(
        FacilityAssertion(
            assertion_id=f"marlborough:{item['id']}",
            source_id="marlborough-food-premise-licences",
            facility_type="food-premise",
            name=str(item["properties"].get("Name") or "unnamed"),
            latitude=float(item["geometry"]["coordinates"][1]),
            longitude=float(item["geometry"]["coordinates"][0]),
            authority="official-reference",
            licence="council-terms",
        )
        for item in council["features"]
        if item.get("geometry")
    )
    return left, right


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    left, right = assertions()
    results = reconcile(left, right)
    candidates = [item for item in results if item.disposition == "candidate-match"]
    report = {
        "evidence_id": "facility-food-reconciliation-20260803",
        "status": "candidate-matches-not-adjudicated",
        "method": "riopa-name-distance-v1",
        "source_packets": PACKETS,
        "counts": {
            "osm_spatial_assertions": len(left),
            "marlborough_spatial_assertions": len(right),
            "candidate_matches": len(candidates),
            "source_only": sum(item.disposition == "source-only" for item in results),
        },
        "limitations": [
            "Candidate matches are not adjudicated facility identities.",
            "Hamilton is excluded because its packet has null geometry for every record.",
            "The result does not estimate national completeness or source accuracy.",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
