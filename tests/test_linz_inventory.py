from __future__ import annotations

import pytest

from riopa_provenance.linz_inventory import (
    LinzArchivePlanError,
    _matches,
    _validate_policy,
    build_backfill_batches,
)


def test_inventory_matching_uses_type_services_and_categories() -> None:
    item = {
        "item_type": "layer",
        "kind": "vector",
        "services": ["WFS", "export"],
        "categories": ["Transport/Roads"],
        "license": "CC-BY",
    }
    assert _matches(item, {"match": {"item_types": ["layer"], "service_any": ["wfs"]}})
    assert _matches(item, {"match": {"category_prefixes": ["transport"]}})
    assert not _matches(item, {"match": {"service_none": ["wfs"]}})


def test_inventory_policy_validation_rejects_duplicates_and_missing_profiles() -> None:
    base = {
        "schema_version": "1.0.0",
        "rules": [{"id": "one", "strategy": "wfs", "format_profile": "missing"}],
        "fallback": {"id": "fallback", "strategy": "metadata-only"},
        "execution": {"format_profiles": {}},
    }
    with pytest.raises(LinzArchivePlanError, match="unknown format profiles"):
        _validate_policy(base)
    duplicate = {
        **base,
        "rules": [
            {"id": "one", "strategy": "wfs"},
            {"id": "one", "strategy": "export"},
        ],
        "execution": {"format_profiles": {}},
    }
    with pytest.raises(LinzArchivePlanError, match="duplicate"):
        _validate_policy(duplicate)


def test_backfill_batches_isolate_unknown_and_oversize_jobs() -> None:
    plan = {
        "dispositions": [
            {
                "job_key": "known",
                "strategy": "wfs",
                "estimated_size_bytes": 4,
                "tier": "hot",
                "priority": 1,
            },
            {
                "job_key": "unknown",
                "strategy": "export",
                "estimated_size_bytes": None,
                "tier": "hot",
                "priority": 2,
            },
            {
                "job_key": "oversize",
                "strategy": "export",
                "estimated_size_bytes": 20,
                "tier": "hot",
                "priority": 3,
            },
            {
                "job_key": "metadata",
                "strategy": "metadata-only",
                "estimated_size_bytes": 1,
                "tier": "cold",
                "priority": 1,
            },
        ]
    }
    batches = build_backfill_batches(plan, maximum_items=2, maximum_estimated_bytes=10)
    assert [batch["jobs"][0]["job_key"] for batch in batches] == ["known", "unknown", "oversize"]
    assert batches[1]["limit_reasons"] == ["unknown-estimated-size"]
    assert batches[2]["limit_reasons"] == ["estimated-size-exceeds-batch-limit"]
    with pytest.raises(ValueError, match="batch limits"):
        build_backfill_batches(plan, maximum_items=0)
