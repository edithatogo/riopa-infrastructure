from __future__ import annotations

import json
from pathlib import Path

import pytest

from riopa_provenance.linz_federation import LinzFederationError, classify_family, load_federation_policy


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
