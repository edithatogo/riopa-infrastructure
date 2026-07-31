from __future__ import annotations

import json
from pathlib import Path

import pytest

from riopa_provenance.hashing import sha256_file, sha256_json
from riopa_provenance.linz_federation import (
    LinzFederationError,
    _analytical_rows,
    _dataset_card,
    _json_text,
    _load_snapshot_manifest,
    _write_checksums,
    _write_publication_crosswalk,
    build_federation_manifest,
    classify_family,
    load_federation_policy,
    stage_federation,
)
from riopa_provenance.linz_inventory import plan_catalog_archive


def policy() -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "policy_id": "policy",
        "policy_version": "1",
        "repositories": {
            "github_control_plane": "owner/control",
            "hugging_face_umbrella": "owner/data",
            "zenodo_concept": "concept",
        },
        "families": [
            {"id": "transport", "repository": "owner/transport", "match_any": ["road"]},
        ],
        "fallback": {"id": "other", "repository": "owner/other"},
        "publication": {
            "github_role": "control",
            "hugging_face_role": "living",
            "zenodo_role": "preservation",
            "zenodo_deposit_mode": "reviewed",
        },
    }


def test_family_classification_is_case_insensitive_with_fallback() -> None:
    value = policy()
    assert classify_family({"name": "Road centrelines"}, value) == (
        "transport",
        "owner/transport",
    )
    assert classify_family({"name": "Schools"}, value) == ("other", "owner/other")


def test_policy_loader_rejects_missing_and_duplicate_family_repositories(tmp_path: Path) -> None:
    path = tmp_path / "policy.json"
    path.write_text('{"schema_version":"1.0.0"}', encoding="utf-8")
    with pytest.raises(LinzFederationError, match="missing"):
        load_federation_policy(path)
    invalid = policy()
    invalid["families"] = [
        {"id": "one", "repository": "owner/same"},
        {"id": "two", "repository": "owner/same"},
    ]
    path.write_text(json.dumps(invalid), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="duplicate federation repository"):
        load_federation_policy(path)


def test_snapshot_manifest_checks_hashes_sizes_and_root_containment(tmp_path: Path) -> None:
    items = tmp_path / "items.jsonl"
    csv = tmp_path / "items.csv"
    items.write_text('{"catalog_item_id":"one"}\n', encoding="utf-8")
    csv.write_text("catalog_item_id\none\n", encoding="utf-8")
    manifest: dict[str, object] = {
        "record_type": "linz_catalog_snapshot",
        "snapshot_id": "snapshot",
        "items": {
            "path": items.name,
            "sha256": sha256_file(items),
            "size_bytes": items.stat().st_size,
        },
        "csv": {"path": csv.name, "sha256": sha256_file(csv), "size_bytes": csv.stat().st_size},
    }
    manifest["manifest_sha256"] = sha256_json(manifest)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert _load_snapshot_manifest(path)["snapshot_id"] == "snapshot"

    manifest["items"] = {"path": "../outside.jsonl", "sha256": "x", "size_bytes": 1}
    manifest["manifest_sha256"] = sha256_json(manifest)
    path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="escapes snapshot root"):
        _load_snapshot_manifest(path)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ([], "root must be an object"),
        ({"schema_version": "1.0.0"}, "missing"),
        ({**policy(), "schema_version": "2.0.0"}, "schema_version"),
        ({**policy(), "repositories": []}, "repositories must be an object"),
        (
            {
                **policy(),
                "repositories": {
                    "github_control_plane": "",
                    "hugging_face_umbrella": "owner/data",
                    "zenodo_concept": "concept",
                },
            },
            "no github_control_plane",
        ),
        ({**policy(), "families": []}, "at least one family"),
        ({**policy(), "families": ["bad"]}, "family must be an object"),
        (
            {**policy(), "families": [{"id": "", "repository": "owner/repo"}]},
            "requires id and repository",
        ),
        (
            {
                **policy(),
                "families": [
                    {"id": "same", "repository": "owner/a"},
                    {"id": "same", "repository": "owner/b"},
                ],
            },
            "duplicate federation family id",
        ),
        ({**policy(), "fallback": {}}, "fallback requires"),
    ],
)
def test_policy_loader_rejects_structural_failures(
    tmp_path: Path, value: object, message: str
) -> None:
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzFederationError, match=message):
        load_federation_policy(path)


def test_policy_loader_supports_yaml_and_classification_searches_raw_fields(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.yaml"
    path.write_text(
        """
schema_version: 1.0.0
policy_id: policy
policy_version: "1"
repositories:
  github_control_plane: owner/control
  hugging_face_umbrella: owner/data
  zenodo_concept: concept
families:
  - id: transport
    repository: owner/transport
    match_any: [highway]
fallback:
  id: other
  repository: owner/other
""",
        encoding="utf-8",
    )
    loaded = load_federation_policy(path)
    assert classify_family(
        {
            "categories": 42,
            "tags": "not-a-sequence",
            "raw": {"description": "National HIGHWAY network"},
        },
        loaded,
    ) == ("transport", "owner/transport")


def _catalog_item(identifier: str, name: str) -> dict[str, object]:
    return {
        "catalog_item_id": identifier,
        "source_catalog_id": "linz",
        "item_type": "layer",
        "kind": "vector",
        "name": name,
        "url": f"https://example.invalid/{identifier}",
        "raw_sha256": identifier * 16,
        "size_bytes": 4,
        "license": "CC-BY",
        "services": ["wfs"],
        "categories": ["Transport"],
        "raw": {"description": name},
    }


def _federation_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    items = tmp_path / "items.jsonl"
    records = [_catalog_item("one", "Road centrelines"), _catalog_item("two", "Schools")]
    items.write_text(
        "".join(json.dumps(item, sort_keys=True) + "\n" for item in records),
        encoding="utf-8",
    )
    csv = tmp_path / "items.csv"
    csv.write_text("catalog_item_id\none\ntwo\n", encoding="utf-8")
    snapshot: dict[str, object] = {
        "record_type": "linz_catalog_snapshot",
        "snapshot_id": "snapshot",
        "items": {
            "path": items.name,
            "sha256": sha256_file(items),
            "size_bytes": items.stat().st_size,
        },
        "csv": {"path": csv.name, "sha256": sha256_file(csv), "size_bytes": csv.stat().st_size},
        "completeness": {"unfiltered_published_catalogue": True},
    }
    snapshot["manifest_sha256"] = sha256_json(snapshot, omit_keys={"manifest_sha256"})
    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text(json.dumps(snapshot), encoding="utf-8")

    archive_policy = {
        "schema_version": "1.0.0",
        "policy_id": "archive",
        "policy_version": "1",
        "rules": [{"id": "vector", "strategy": "wfs", "match": {"kinds": ["vector"]}}],
        "fallback": {"id": "fallback", "strategy": "metadata-only"},
        "execution": {"format_profiles": {}},
    }
    plan = plan_catalog_archive(
        records,
        archive_policy,
        catalog_snapshot_id="snapshot",
        catalog_items_sha256=sha256_file(items),
        catalogue_complete=True,
        planning_inputs_complete=True,
    )
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    policy_path = tmp_path / "federation-policy.json"
    policy_path.write_text(json.dumps(policy()), encoding="utf-8")
    return snapshot_path, plan_path, policy_path


def test_build_manifest_binds_every_identity_and_stages_all_targets(tmp_path: Path) -> None:
    snapshot, plan, federation_policy = _federation_inputs(tmp_path)
    manifest_path = tmp_path / "federation.json"
    assert (
        build_federation_manifest(
            snapshot,
            plan,
            federation_policy,
            manifest_path,
            created_at="2026-07-31T00:00:00Z",
        )
        == manifest_path.resolve()
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["coverage"]["catalogue_item_count"] == 2
    assert manifest["coverage"]["families"] == {"other": 1, "transport": 1}
    assert manifest["manifest_sha256"] == sha256_json(manifest, omit_keys={"manifest_sha256"})

    stage = stage_federation(snapshot, plan, manifest_path, tmp_path / "stage")
    assert stage.item_count == 2
    assert stage.family_count == 2
    assert stage.manifest_path.is_file()
    assert (stage.github_path / "control-plane" / "checksums.sha256").is_file()
    umbrella = stage.hugging_face_path / "owner__data"
    assert (umbrella / "catalogue-index.parquet").is_file()
    assert (umbrella / "nz-spatial-archive.duckdb").is_file()
    assert (stage.zenodo_path / "linz-catalogue-release" / "CITATION.cff").is_file()

    # Reconciliation is deterministic and replaces stale stage content.
    stale = stage.root / "stale.txt"
    stale.write_text("old", encoding="utf-8")
    second = stage_federation(snapshot, plan, manifest_path, stage.root)
    assert not stale.exists()
    assert second.manifest_path.read_bytes() == stage.manifest_path.read_bytes()


def test_build_manifest_rejects_incomplete_or_mismatched_inputs(tmp_path: Path) -> None:
    snapshot, plan_path, federation_policy = _federation_inputs(tmp_path)
    snapshot_value = json.loads(snapshot.read_text(encoding="utf-8"))
    snapshot_value["completeness"] = {"unfiltered_published_catalogue": False}
    snapshot_value["manifest_sha256"] = sha256_json(snapshot_value, omit_keys={"manifest_sha256"})
    snapshot.write_text(json.dumps(snapshot_value), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="unfiltered"):
        build_federation_manifest(
            snapshot, plan_path, federation_policy, tmp_path / "out", created_at="now"
        )

    snapshot, plan_path, federation_policy = _federation_inputs(tmp_path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["scope"]["catalogue_complete"] = False
    plan["plan_sha256"] = sha256_json(plan, omit_keys={"plan_sha256"})
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="catalogue_complete"):
        build_federation_manifest(
            snapshot, plan_path, federation_policy, tmp_path / "out", created_at="now"
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda plan: plan.update(catalog_snapshot_id="other"), "different catalogue"),
        (lambda plan: plan.update(catalog_items_sha256="bad"), "different catalogue items"),
        (lambda plan: plan.update(dispositions=None), "no dispositions"),
        (
            lambda plan: plan.update(dispositions=["invalid"]),
            "disposition is not an object",
        ),
        (
            lambda plan: plan["dispositions"].append(dict(plan["dispositions"][0])),
            "duplicate or empty",
        ),
        (
            lambda plan: plan["dispositions"].pop(),
            "identity mismatch",
        ),
    ],
)
def test_build_manifest_rejects_plan_binding_failures(
    tmp_path: Path, mutation: object, message: str
) -> None:
    snapshot, plan_path, federation_policy = _federation_inputs(tmp_path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    mutation(plan)  # type: ignore[operator]
    plan["plan_sha256"] = sha256_json(plan, omit_keys={"plan_sha256"})
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(LinzFederationError, match=message):
        build_federation_manifest(
            snapshot, plan_path, federation_policy, tmp_path / "out", created_at="now"
        )


def test_snapshot_manifest_rejects_descriptor_file_and_integrity_failures(
    tmp_path: Path,
) -> None:
    snapshot, _plan, _policy = _federation_inputs(tmp_path)
    value = json.loads(snapshot.read_text(encoding="utf-8"))
    value["items"] = []
    value["manifest_sha256"] = sha256_json(value, omit_keys={"manifest_sha256"})
    snapshot.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="no items file"):
        _load_snapshot_manifest(snapshot)

    snapshot, _plan, _policy = _federation_inputs(tmp_path)
    value = json.loads(snapshot.read_text(encoding="utf-8"))
    value["items"]["path"] = "missing"
    value["manifest_sha256"] = sha256_json(value, omit_keys={"manifest_sha256"})
    snapshot.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="file is missing"):
        _load_snapshot_manifest(snapshot)

    snapshot, _plan, _policy = _federation_inputs(tmp_path)
    value = json.loads(snapshot.read_text(encoding="utf-8"))
    value["items"]["sha256"] = "bad"
    value["manifest_sha256"] = sha256_json(value, omit_keys={"manifest_sha256"})
    snapshot.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="hash mismatch"):
        _load_snapshot_manifest(snapshot)

    snapshot, _plan, _policy = _federation_inputs(tmp_path)
    value = json.loads(snapshot.read_text(encoding="utf-8"))
    value["items"]["size_bytes"] += 1
    value["manifest_sha256"] = sha256_json(value, omit_keys={"manifest_sha256"})
    snapshot.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="size mismatch"):
        _load_snapshot_manifest(snapshot)

    snapshot, _plan, _policy = _federation_inputs(tmp_path)
    value = json.loads(snapshot.read_text(encoding="utf-8"))
    value["manifest_sha256"] = "bad"
    snapshot.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="manifest hash mismatch"):
        _load_snapshot_manifest(snapshot)


def test_staging_rejects_manifest_integrity_binding_and_optional_input_failures(
    tmp_path: Path,
) -> None:
    snapshot, plan, federation_policy = _federation_inputs(tmp_path)
    manifest_path = build_federation_manifest(
        snapshot, plan, federation_policy, tmp_path / "manifest", created_at="now"
    )
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    value["record_type"] = "other"
    manifest_path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="not a LINZ federation"):
        stage_federation(snapshot, plan, manifest_path, tmp_path / "stage")

    manifest_path = build_federation_manifest(
        snapshot, plan, federation_policy, tmp_path / "manifest", created_at="now"
    )
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    value["manifest_sha256"] = "bad"
    manifest_path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(LinzFederationError, match="manifest hash mismatch"):
        stage_federation(snapshot, plan, manifest_path, tmp_path / "stage")

    manifest_path = build_federation_manifest(
        snapshot, plan, federation_policy, tmp_path / "manifest", created_at="now"
    )
    with pytest.raises(LinzFederationError, match="control-plane input is missing"):
        stage_federation(
            snapshot,
            plan,
            manifest_path,
            tmp_path / "stage",
            source_registry_path=tmp_path / "missing",
        )


def test_rendering_helpers_are_content_bound_and_null_safe(tmp_path: Path) -> None:
    assert _json_text(None) is None
    assert _json_text({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    card = _dataset_card(
        title="Title",
        scope="Scope",
        snapshot_id="snapshot",
        item_count=1,
        catalogue_complete=False,
        payload_note="Payload note.",
    )
    assert "documented family subset" in card

    item = _catalog_item("one", "Roads")
    disposition = {
        "catalog_item_id": "one",
        "strategy": "wfs",
        "payload_methods": ["wfs"],
        "blockers": [],
    }
    assignment = {"catalog_item_id": "one", "family_id": "transport"}
    catalogue, dispositions = _analytical_rows([item], {"one": disposition}, {"one": assignment})
    assert catalogue[0]["catalog_item_id"] == "one"
    assert dispositions[0]["payload_methods_json"] == '["wfs"]'

    crosswalk = tmp_path / "crosswalk.json"
    _write_publication_crosswalk(
        crosswalk,
        federation_id="f",
        snapshot_id="s",
        archive_plan_id="p",
        github_repository="g",
        hugging_face_repository="h",
        zenodo_concept="z",
    )
    value = json.loads(crosswalk.read_text(encoding="utf-8"))
    assert value["remote_publication_performed"] is False
    assert value["crosswalk_sha256"] == sha256_json(value, omit_keys={"crosswalk_sha256"})
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    checksums = _write_checksums(tmp_path)
    first = checksums.read_text(encoding="utf-8")
    _write_checksums(tmp_path)
    assert checksums.read_text(encoding="utf-8") == first
