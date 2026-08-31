from __future__ import annotations

import json
from pathlib import Path

from riopa_provenance.hashing import sha256_bytes, sha256_json


def test_hosted_fixed_baseline_comparison_acceptance() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads(
        (root / "docs/tasman-feature-comparison-acceptance-20260831.json").read_bytes()
    )
    receipt = evidence["comparison_receipt"]
    assert evidence["hosted_execution"]["conclusion"] == "success"
    assert evidence["hosted_execution"]["event"] == "workflow_dispatch"
    assert evidence["hosted_execution"]["producer_revision"] == (
        "3b28c8764ec2fcddc9a04e9885c4c03f9cf8bfb6"
    )
    assert evidence["hosted_execution"]["receipt_sha256"] == sha256_bytes(
        (json.dumps(receipt, indent=2) + "\n").encode()
    )
    assert receipt["status"] == "compared"
    assert receipt["baseline_role"] == "fixed-initial-accepted-packet-not-previous-cycle"
    assert receipt["release_cycle_qualified"] is False
    comparison = receipt["comparison"]
    assert comparison["release_cycle_qualified"] is False
    assert comparison["before"]["feature_count"] == comparison["after"]["feature_count"] == 3655
    assert comparison["before"] == comparison["after"]
    for field in ("added", "removed", "attribute_changed", "geometry_changed"):
        assert comparison[field] == []
    assert comparison["change_hashes"] == {}
    assert (
        sha256_json(comparison, omit_keys={"comparison_sha256"}) == comparison["comparison_sha256"]
    )
    baseline_path = root / "docs/tasman-derived-acceptance-20260831.json"
    assert receipt["baseline_acceptance_sha256"] == sha256_bytes(baseline_path.read_bytes())
    baseline = json.loads(baseline_path.read_bytes())["publication_receipt"]
    assert receipt["baseline_public_revision"] == baseline["public_revision"]
    assert receipt["derived_public_revision"] == baseline["public_revision"]
    assert receipt["baseline_canonical_sha256"] == baseline["files"]["canonical.json"]["sha256"]
    assert receipt["current_canonical_sha256"] == receipt["baseline_canonical_sha256"]
