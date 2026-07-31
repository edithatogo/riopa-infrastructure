from __future__ import annotations

import json
from pathlib import Path

import pytest

from riopa_provenance.hashing import sha256_file, sha256_json
from riopa_provenance.linz_inventory import (
    LinzArchivePlanError,
    _estimated_size,
    _execution_contract,
    _matches,
    _rights_disposition,
    _validate_policy,
    build_backfill_batches,
    load_archive_plan,
    load_archive_policy,
    plan_catalog_archive,
    write_archive_plan_from_snapshot,
    write_backfill_batches,
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


def archive_policy() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "policy_id": "policy",
        "policy_version": "1",
        "rules": [
            {
                "id": "vector",
                "strategy": "wfs",
                "match": {"kinds": ["vector"], "service_any": ["wfs"]},
                "payload_methods": ["koordinates-export"],
                "format_profile_by_kind": {"vector": "vector"},
                "requires_size_estimate": True,
                "tier": "T1",
                "priority": "P1",
            }
        ],
        "fallback": {"id": "fallback", "strategy": "metadata-only"},
        "execution": {
            "automatic_export_limit_bytes": 10,
            "default_export_crs": "EPSG:2193",
            "format_profiles": {"vector": {"preferred": ["geoparquet", "fgb"]}},
        },
    }


def catalog_item(identifier: str = "one") -> dict[str, object]:
    return {
        "catalog_item_id": identifier,
        "source_catalog_id": "linz",
        "item_type": "layer",
        "kind": "vector",
        "name": "Roads",
        "url": "https://example.invalid/roads",
        "raw_sha256": "a" * 64,
        "size_bytes": 4,
        "license": "Creative Commons Attribution 4.0",
        "services": [{"type": "WFS"}, {"url": "https://example.invalid/export"}],
        "categories": ["Transport/Roads"],
        "raw": {},
    }


def test_matching_and_projection_helpers_cover_nested_and_invalid_shapes() -> None:
    nested = {
        "raw": {
            "kind": "grid",
            "services": {"download": {"type": "spatial-query-grid"}},
            "license": {"name": "Public-Domain"},
            "categories": "Imagery",
            "data": {"size_bytes": 0},
        }
    }
    assert _matches(
        nested,
        {
            "match": {
                "kinds": ["grid"],
                "service_any": ["spatial-query-grid"],
                "license_any": ["public-domain"],
                "category_prefixes": ["imag"],
            }
        },
    )
    assert _estimated_size(nested) == 0
    assert _estimated_size({"size_bytes": True, "raw": {"size_bytes": -1}}) is None
    assert _rights_disposition(nested, {}) == "candidate-permitted-review-required"
    assert _rights_disposition({}, {}) == "unresolved"
    assert _rights_disposition({"license": "proprietary"}, {}) == "review-required"
    assert _rights_disposition({}, {"rights_disposition": "prohibited"}) == "prohibited"
    with pytest.raises(LinzArchivePlanError, match="match must be an object"):
        _matches({}, {"id": "bad", "match": []})


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"schema_version": "2"}, "schema_version"),
        ({"rules": []}, "at least one rule"),
        ({"rules": ["bad"]}, "must be an object"),
        ({"rules": [{"strategy": "wfs"}]}, "has no id"),
        ({"rules": [{"id": "x"}]}, "has no strategy"),
        ({"fallback": {}}, "fallback strategy"),
        ({"execution": []}, "execution must be an object"),
        ({"execution": {"format_profiles": []}}, "format_profiles must be an object"),
    ],
)
def test_policy_validation_rejects_each_structural_failure(
    mutation: dict[str, object], message: str
) -> None:
    value = archive_policy()
    value.update(mutation)
    with pytest.raises(LinzArchivePlanError, match=message):
        _validate_policy(value)


def test_policy_validation_rejects_bad_kind_profile_and_accepts_valid_policy() -> None:
    value = archive_policy()
    _validate_policy(value)
    rule = value["rules"][0]  # type: ignore[index]
    rule["format_profile_by_kind"] = ["bad"]  # type: ignore[index]
    with pytest.raises(LinzArchivePlanError, match="format_profile_by_kind"):
        _validate_policy(value)


def test_execution_contract_normalises_preferences_and_invalid_limits() -> None:
    item = catalog_item()
    policy = archive_policy()
    contract = _execution_contract(item, policy["rules"][0], policy)  # type: ignore[index]
    assert contract == {
        "payload_methods": ["koordinates-export"],
        "format_profile": "vector",
        "format_preferences": {"preferred": ["geoparquet", "fgb"]},
        "export_crs": "EPSG:2193",
        "automatic_export_limit_bytes": 10,
    }
    policy["execution"] = {"automatic_export_limit_bytes": True, "format_profiles": []}
    assert _execution_contract(item, {}, policy)["automatic_export_limit_bytes"] is None


def test_plan_archive_is_deterministic_and_reports_actionable_blockers() -> None:
    policy = archive_policy()
    ready = catalog_item("ready")
    ready["license"] = "permitted"
    policy["rules"][0]["rights_disposition"] = "permitted"  # type: ignore[index]
    missing_size = catalog_item("missing")
    missing_size.pop("size_bytes")
    missing_size["services"] = ["wfs"]
    oversize = catalog_item("oversize")
    oversize["size_bytes"] = 11
    unsupported = catalog_item("unsupported")
    unsupported["kind"] = "table"
    unsupported["services"] = []
    plan = plan_catalog_archive(
        [unsupported, oversize, missing_size, ready],
        policy,
        catalog_snapshot_id="snapshot",
        catalog_items_sha256="b" * 64,
        catalogue_complete=False,
    )
    assert [entry["catalog_item_id"] for entry in plan["dispositions"]] == [
        "missing",
        "oversize",
        "ready",
        "unsupported",
    ]
    by_id = {entry["catalog_item_id"]: entry for entry in plan["dispositions"]}
    assert by_id["ready"]["payload_status"] == "ready"
    assert by_id["missing"]["blockers"] == ["export-service-unavailable", "size-assessment"]
    assert by_id["oversize"]["blockers"] == ["automatic-export-size-limit"]
    assert by_id["unsupported"]["payload_status"] == "review-required"
    assert plan["scope"]["catalogue_complete"] is False
    assert plan["scope"]["unclassified_count"] == 1
    assert plan["plan_sha256"] == sha256_json(plan, omit_keys={"plan_sha256"})


def test_plan_rejects_duplicate_catalogue_identities() -> None:
    with pytest.raises(LinzArchivePlanError, match="duplicate catalogue identities"):
        plan_catalog_archive(
            [catalog_item(), catalog_item()],
            archive_policy(),
            catalog_snapshot_id="snapshot",
            catalog_items_sha256="x",
            catalogue_complete=True,
        )


def _write_snapshot(tmp_path: Path, *, enriched: bool = True) -> tuple[Path, Path]:
    items = tmp_path / "items.jsonl"
    items.write_text(json.dumps(catalog_item()) + "\n", encoding="utf-8")
    csv = tmp_path / "items.csv"
    csv.write_text("catalog_item_id\none\n", encoding="utf-8")
    manifest: dict[str, object] = {
        "record_type": "linz_catalog_enriched_snapshot" if enriched else "linz_catalog_snapshot",
        "snapshot_id": "snapshot",
        "items": {
            "path": items.name,
            "sha256": sha256_file(items),
            "size_bytes": items.stat().st_size,
        },
        "csv": {"path": csv.name, "sha256": sha256_file(csv), "size_bytes": csv.stat().st_size},
        "completeness": {"unfiltered_published_catalogue": True},
        "detail_coverage": {"complete": True},
        "service_coverage": {"complete": True},
    }
    manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path, items


def test_archive_plan_file_round_trip_and_batches(tmp_path: Path) -> None:
    manifest, _items = _write_snapshot(tmp_path)
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(archive_policy()), encoding="utf-8")
    assert load_archive_policy(policy_path)["policy_id"] == "policy"
    yaml_path = tmp_path / "policy.yaml"
    yaml_path.write_text("schema_version: 1.0.0\n", encoding="utf-8")
    assert load_archive_policy(yaml_path)["schema_version"] == "1.0.0"

    plan_path = tmp_path / "plan.json"
    summary = write_archive_plan_from_snapshot(manifest, policy_path, plan_path)
    assert summary.item_count == 1
    assert load_archive_plan(plan_path)["scope"]["planning_inputs_complete"] is True

    batches_path = tmp_path / "batches.json"
    assert write_backfill_batches(plan_path, batches_path) == batches_path
    batches = json.loads(batches_path.read_text(encoding="utf-8"))
    assert batches["document_sha256"] == sha256_json(batches, omit_keys={"document_sha256"})
    tampered = load_archive_plan(plan_path)
    tampered["plan_id"] = "tampered"
    plan_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(LinzArchivePlanError, match="hash mismatch"):
        load_archive_plan(plan_path)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda value: value.update(record_type="other"), "not a LINZ"),
        (lambda value: value.update(manifest_sha256="bad"), "manifest hash"),
        (lambda value: value.pop("items"), "no items descriptor"),
    ],
)
def test_snapshot_plan_rejects_invalid_manifest(
    tmp_path: Path, mutate: object, message: str
) -> None:
    manifest, _items = _write_snapshot(tmp_path)
    value = json.loads(manifest.read_text(encoding="utf-8"))
    mutate(value)  # type: ignore[operator]
    if "manifest_sha256" in value and value["manifest_sha256"] != "bad":
        value["manifest_sha256"] = sha256_json(value, omit_keys={"manifest_sha256"})
    manifest.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzArchivePlanError, match=message):
        write_archive_plan_from_snapshot(manifest, tmp_path / "policy", tmp_path / "plan")


def test_snapshot_plan_rejects_payload_hash_and_size_mismatch(tmp_path: Path) -> None:
    manifest, items = _write_snapshot(tmp_path)
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(archive_policy()), encoding="utf-8")
    items.write_text("{}\n", encoding="utf-8")
    with pytest.raises(LinzArchivePlanError, match="items hash mismatch"):
        write_archive_plan_from_snapshot(manifest, policy_path, tmp_path / "plan")

    manifest, items = _write_snapshot(tmp_path)
    value = json.loads(manifest.read_text(encoding="utf-8"))
    value["items"]["size_bytes"] += 1
    value["manifest_sha256"] = sha256_json(value, omit_keys={"manifest_sha256"})
    manifest.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzArchivePlanError, match="items size mismatch"):
        write_archive_plan_from_snapshot(manifest, policy_path, tmp_path / "plan")


def test_loaders_reject_non_object_policy_and_non_plan(tmp_path: Path) -> None:
    path = tmp_path / "value.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(LinzArchivePlanError, match="root must be an object"):
        load_archive_policy(path)
    with pytest.raises(LinzArchivePlanError, match="not a LINZ archive plan"):
        load_archive_plan(path)
    missing = tmp_path / "missing.json"
    with pytest.raises(LinzArchivePlanError, match="cannot load catalogue snapshot"):
        write_archive_plan_from_snapshot(missing, path, tmp_path / "plan")
