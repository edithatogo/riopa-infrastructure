"""Build a deterministic, bounded review sample from reconciliation counts.

This creates a sampling frame only. It does not adjudicate identities or promote
any source to authoritative status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _sample_count(total: int, fraction: int, minimum: int = 1) -> int:
    if total <= 0:
        return 0
    return min(total, max(minimum, (total + fraction - 1) // fraction))


def build_sample(reconciliation: dict[str, Any], *, sample_divisor: int = 20) -> dict[str, Any]:
    counts = reconciliation["counts"]
    strata = [
        {
            "id": "candidate-matches",
            "population": counts["candidate_matches"],
            "sample_size": counts["candidate_matches"],
            "selection": "include-all-candidate-pairs",
            "review_questions": ["same facility", "classification", "coordinate plausibility"],
        },
        {
            "id": "osm-only",
            "population": counts["osm_spatial_assertions"],
            "sample_size": _sample_count(counts["osm_spatial_assertions"], sample_divisor),
            "selection": "stable-sha256-rank-of-source-assertion-id",
            "review_questions": ["classification", "coordinate plausibility", "duplicate risk"],
        },
        {
            "id": "marlborough-only",
            "population": counts["marlborough_spatial_assertions"],
            "sample_size": _sample_count(counts["marlborough_spatial_assertions"], sample_divisor),
            "selection": "stable-sha256-rank-of-source-assertion-id",
            "review_questions": ["classification", "coordinate plausibility", "duplicate risk"],
        },
    ]
    canonical = json.dumps(strata, sort_keys=True, separators=(",", ":")).encode()
    return {
        "evidence_id": "facility-stratified-review-sample-20260803",
        "source_evidence": reconciliation["evidence_id"],
        "method": "sha256-ranked-bounded-strata-v1",
        "sample_divisor": sample_divisor,
        "strata": strata,
        "total_population": sum(item["population"] for item in strata),
        "total_sample_size": sum(item["sample_size"] for item in strata),
        "selection_frame_sha256": hashlib.sha256(canonical).hexdigest(),
        "status": "pending-agent-panel-disposition",
        "limitations": [
            "The frame contains counts, not source payload identifiers or adjudications.",
            "Panel review is required before identity, classification or authority claims.",
            "Hamilton remains excluded because its archived packet has null geometry.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=Path("docs/facility-food-reconciliation-20260803.json")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("docs/facility-stratified-review-sample-20260803.json")
    )
    args = parser.parse_args()
    result = build_sample(json.loads(args.input.read_text()), sample_divisor=20)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
