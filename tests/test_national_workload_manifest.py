from __future__ import annotations

import json
from pathlib import Path

from riopa_provenance.hashing import sha256_json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/national-workload-manifest-20260803.json"


def test_national_workload_manifest_is_content_addressed_and_bounded() -> None:
    value = json.loads(MANIFEST.read_text())
    assert value["schema"] == "riopa.national-workload-manifest.v1"
    assert value["manifest_sha256"] == sha256_json(value, omit_keys={"manifest_sha256"})
    assert value["scope"]["live_endpoints_contacted"] is False
    assert value["scope"]["bulk_payloads_committed"] is False
    assert len(value["snapshots"]) == 2

    geography, population = value["snapshots"]
    assert geography["feature_count"] == 57575
    assert geography["page_count"] == 231
    assert geography["geometry_repairs"] == 0
    assert population["workbook_sha256"] == (
        "001e8a896cfb50f5ed17836dc815b235e3bcca55ee91c9869a2afaeb054b50a6"
    )
    assert population["workbook_bytes"] == 97990
    assert population["reference_dates"] == [
        "30 June 2023",
        "30 June 2024",
        "30 June 2025",
    ]

    alignment = value["workload_contract"]["alignment"]
    assert alignment["status"] == "reference-only"
    assert "assign regional or territorial population to Meshblocks" in alignment["prohibited"]
    assert "claim national completeness from these two snapshots alone" in alignment["prohibited"]
