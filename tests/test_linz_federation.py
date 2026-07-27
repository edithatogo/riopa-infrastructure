from __future__ import annotations

import json
from pathlib import Path

import pytest

from riopa_provenance.hashing import sha256_file, sha256_json
from riopa_provenance.linz_federation import (
    LinzFederationError,
    _load_snapshot_manifest,
    classify_family,
    load_federation_policy,
)


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
        "items": {"path": items.name, "sha256": sha256_file(items), "size_bytes": items.stat().st_size},
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
