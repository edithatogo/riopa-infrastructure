#!/usr/bin/env python3
"""Offline, exact-byte geometry comparison of verified Tasman canonical projections."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from shapely import from_wkb

from riopa_provenance.hashing import sha256_bytes, sha256_json

MAX_BYTES = 512_000_000
MAX_ROWS = 100000
METADATA = frozenset({"_riopa_feature_id", "_riopa_capture_ids", "_riopa_source_object_id"})
SHA = re.compile(r"[0-9a-f]{64}")
UUID = re.compile(r"urn:uuid:[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")


def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError("non-finite JSON value")


def safe(path: Path) -> None:
    if any(parent.is_symlink() for parent in (path, *path.parents)) or ".." in path.parts:
        raise ValueError("symlink or traversing path")


def load(path: Path, expected_sha256: str) -> tuple[dict[str, Any], dict[str, Any]]:
    safe(path)
    if (
        not SHA.fullmatch(expected_sha256)
        or not path.is_file()
        or not 0 < path.stat().st_size <= MAX_BYTES
    ):
        raise ValueError("invalid input digest, file or size")
    body = path.read_bytes()
    if sha256_bytes(body) != expected_sha256:
        raise ValueError("canonical file digest mismatch")
    payload = json.loads(body, object_pairs_hook=object_pairs, parse_constant=reject_constant)
    if (
        not isinstance(payload, dict)
        or payload.get("record_type") != "tasman_canonical_projected_rows"
        or payload.get("valid_time") != "unknown-not-imputed"
        or not isinstance(payload.get("source_manifest_sha256"), str)
        or not SHA.fullmatch(payload["source_manifest_sha256"])
    ):
        raise ValueError("unsupported canonical source/profile")
    rows, features = payload.get("rows"), payload.get("canonical_features")
    if (
        not isinstance(rows, list)
        or not isinstance(features, list)
        or len(rows) != len(features)
        or len(rows) > MAX_ROWS
    ):
        raise ValueError("canonical row/feature count mismatch")
    features_by_id = {}
    for feature in features:
        if (
            not isinstance(feature, dict)
            or not isinstance(feature.get("source_object_id"), str)
            or feature["source_object_id"] in features_by_id
        ):
            raise ValueError("invalid or duplicate canonical identity")
        features_by_id[feature["source_object_id"]] = feature
    by_id: dict[str, Any] = {}
    recorded_times = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("canonical row must be an object")
        identity = row.get("_riopa_source_object_id")
        if (
            not isinstance(identity, str)
            or not re.fullmatch(r"-?(?:0|[1-9][0-9]{0,19})", identity)
            or identity in by_id
        ):
            raise ValueError("missing or duplicate stable source identity")
        if type(row.get("OBJECTID")) is not int or str(row["OBJECTID"]) != identity:
            raise ValueError("source OBJECTID binding mismatch")
        feature = features_by_id.get(identity)
        if (
            feature is None
            or feature.get("feature_id") != row.get("_riopa_feature_id")
            or not isinstance(feature.get("feature_id"), str)
            or not re.fullmatch(r"urn:riopa:feature:[0-9a-f]{64}", feature["feature_id"])
        ):
            raise ValueError("canonical feature alignment mismatch")
        captures = json.loads(row["_riopa_capture_ids"], object_pairs_hook=object_pairs)
        if (
            not isinstance(captures, list)
            or not captures
            or any(not isinstance(c, str) or not UUID.fullmatch(c) for c in captures)
            or len(set(captures)) != len(captures)
            or captures != feature.get("capture_ids")
        ):
            raise ValueError("capture lineage binding mismatch")
        geometry = row.get("geometry")
        if "geometry" not in row or (
            geometry is not None
            and (not isinstance(geometry, str) or not re.fullmatch(r"(?:[0-9a-f]{2})+", geometry))
        ):
            raise ValueError("geometry must be canonical lowercase WKB hex or null")
        if geometry is not None:
            from_wkb(bytes.fromhex(geometry), on_invalid="raise")
        if feature.get("geometry_sha256") != sha256_json(geometry):
            raise ValueError("canonical geometry digest mismatch")
        if feature.get("valid_time") != {"from": None, "to": None, "status": "unknown-not-imputed"}:
            raise ValueError("unexpected imputed valid time")
        recorded = feature.get("recorded_time", {})
        if recorded.get("basis") != "archive-capture-date" or not isinstance(
            recorded.get("at"), str
        ):
            raise ValueError("invalid capture-time basis")
        timestamp = datetime.fromisoformat(recorded["at"])
        if timestamp.tzinfo is None:
            raise ValueError("capture time requires timezone")
        recorded_times.append(recorded["at"])
        attributes = {
            key: value for key, value in row.items() if key not in METADATA and key != "geometry"
        }
        by_id[identity] = {
            "attributes_sha256": sha256_json(attributes),
            "geometry_sha256": sha256_json(geometry),
        }
    if set(by_id) != set(features_by_id):
        raise ValueError("canonical feature closure mismatch")
    info = {
        "canonical_sha256": expected_sha256,
        "source_manifest_sha256": payload["source_manifest_sha256"],
        "feature_count": len(by_id),
        "recorded_capture_times": sorted(set(recorded_times)),
        "comparison_content_sha256": sha256_json(by_id),
    }
    return info, by_id


def compare(before: Path, after: Path, before_sha256: str, after_sha256: str) -> dict[str, Any]:
    previous, left = load(before, before_sha256)
    current, right = load(after, after_sha256)
    shared = sorted(set(left) & set(right), key=int)
    added = sorted(set(right) - set(left), key=int)
    removed = sorted(set(left) - set(right), key=int)
    attributes = [
        i for i in shared if left[i]["attributes_sha256"] != right[i]["attributes_sha256"]
    ]
    geometry = [i for i in shared if left[i]["geometry_sha256"] != right[i]["geometry_sha256"]]
    changed = sorted(set(added + removed + attributes + geometry), key=int)
    result = {
        "schema_version": "1.0.0",
        "record_type": "tasman_observed_snapshot_comparison",
        "before": previous,
        "after": current,
        "added": added,
        "removed": removed,
        "attribute_changed": attributes,
        "geometry_changed": geometry,
        "change_hashes": {i: {"before": left.get(i), "after": right.get(i)} for i in changed},
        "semantics": {
            "identity": "_riopa_source_object_id",
            "ignored_metadata": sorted(METADATA),
            "geometry": "original projected WKB bytes, without reserialization or tolerance",
        },
        "release_cycle_qualified": False,
        "non_claims": [
            "Capture-time comparison only; no legal valid-time or operative-status inference.",
            "Differences may reflect acquisition/transformation; no causal source-change claim.",
            "No scheduled-cycle or recovery qualification.",
        ],
    }
    result["comparison_sha256"] = sha256_json(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--before-sha256", required=True)
    parser.add_argument("--after-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        safe(args.output)
        if args.output.exists() or args.output.resolve() in (
            args.before.resolve(),
            args.after.resolve(),
        ):
            raise ValueError("output must be fresh and cannot overwrite inputs")
        result = compare(args.before, args.after, args.before_sha256, args.after_sha256)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as handle:
            handle.write(json.dumps(result, indent=2) + "\n")
    except Exception as error:
        print(json.dumps({"status": "failed", "error_class": type(error).__name__[:128]}))
        return 1
    print(json.dumps({"comparison_sha256": result["comparison_sha256"], "status": "compared"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
