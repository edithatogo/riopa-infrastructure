#!/usr/bin/env python3
"""Offline per-field counts over verified canonical snapshots; no attribute values."""

from __future__ import annotations

import json
import runpy
from collections import Counter
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_bytes, sha256_json

ROOT = Path(__file__).resolve().parents[1]
COMPARATOR = runpy.run_path(str(ROOT / "scripts/compare_tasman_snapshots.py"))


def diagnose(
    before: Path,
    after: Path,
    before_sha256: str,
    after_sha256: str,
    comparison_sha256: str,
) -> dict[str, Any]:
    """Count changed top-level fields among shared identities, without source-cause inference."""
    comparison = COMPARATOR["compare"](before, after, before_sha256, after_sha256)
    if comparison["comparison_sha256"] != comparison_sha256:
        raise ValueError("diagnostic comparison binding mismatch")
    snapshots = []
    for path, checksum in ((before, before_sha256), (after, after_sha256)):
        # The comparator's load validates identity, lineage, time and geometry.
        # Recheck the exact bytes used for field inspection after that validation.
        body = path.read_bytes()
        if sha256_bytes(body) != checksum:
            raise ValueError("diagnostic canonical bytes changed")
        payload = json.loads(body, object_pairs_hook=COMPARATOR["object_pairs"])
        snapshots.append({row["_riopa_source_object_id"]: row for row in payload["rows"]})
    left, right = snapshots
    counts: Counter[str] = Counter()
    shared = sorted(left.keys() & right.keys(), key=int)
    for identity in shared:
        previous, current = left[identity], right[identity]
        fields = (previous.keys() | current.keys()) - {"geometry"}
        if len(fields) > 10_000 or any(len(field) > 1024 for field in fields):
            raise ValueError("diagnostic field budget exceeded")
        for field in fields:
            # Presence is separate from value: absent and explicit null differ.
            old = [field in previous, previous.get(field)]
            new = [field in current, current.get(field)]
            if sha256_json(old) != sha256_json(new):
                counts[field] += 1
    result = {
        "schema_version": "1.0.0",
        "record_type": "tasman_attribute_change_diagnostics",
        "before_canonical_sha256": before_sha256,
        "after_canonical_sha256": after_sha256,
        "comparison_sha256": comparison_sha256,
        "shared_feature_count": len(shared),
        "added_feature_count": len(comparison["added"]),
        "removed_feature_count": len(comparison["removed"]),
        "attribute_changed_feature_count": len(comparison["attribute_changed"]),
        "geometry_changed_feature_count": len(comparison["geometry_changed"]),
        "fields": [
            {
                "name": field,
                "classification": "riopa-prefixed"
                if field.startswith("_riopa_")
                else "source-field",
                "changed_feature_count": count,
                "included_in_attribute_comparison": field not in COMPARATOR["METADATA"],
            }
            for field, count in sorted(counts.items())
        ],
        "release_cycle_qualified": False,
        "non_claims": [
            "Only field names and counts are emitted; no values, full rows or feature IDs.",
            "The _riopa_ classification is a naming convention, not proof of field origin.",
            "Counts cover shared identities only; added and removed rows are counted separately.",
            "Nested changes count once at the top-level field; geometry is counted separately.",
            "No source-cause, operative-status, scheduled-cycle or recovery qualification.",
        ],
    }
    result["diagnostics_sha256"] = sha256_json(result)
    if len((json.dumps(result, indent=2) + "\n").encode()) > 2_000_000:
        raise ValueError("diagnostic output budget exceeded")
    return result
