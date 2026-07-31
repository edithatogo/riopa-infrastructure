from __future__ import annotations

import json
from pathlib import Path

import pytest

from riopa_provenance.adapters import (
    AdapterMappingError,
    cross_repository_mapping_report,
    load_adapter_mapping,
)


def _mapping(repository: str = "edithatogo/example") -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "repository": repository,
        "source_revision": "a" * 40,
        "profile_version": "1.0.0-candidate",
        "mappings": [
            {
                "native_field": f"native.{classification}",
                "riopa_field": (
                    f"riopa.{classification}"
                    if classification in {"exact", "approximate", "extension-only"}
                    else None
                ),
                "classification": classification,
                "rationale": f"Fixture rationale for {classification}",
                "evidence_fixture": "fixtures/native.json",
            }
            for classification in ("exact", "approximate", "extension-only", "unmapped")
        ],
    }


def test_adapter_mapping_requires_all_semantic_classes(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    path = tmp_path / "mapping.json"
    mapping = _mapping()
    path.write_text(json.dumps(mapping), encoding="utf-8")
    loaded = load_adapter_mapping(path, schema_path=root / "schemas/adapter-mapping.schema.json")
    assert loaded["repository"] == "edithatogo/example"
    assert len(loaded["mapping_sha256"]) == 64

    mapping["mappings"] = mapping["mappings"][:-1]  # type: ignore[index]
    path.write_text(json.dumps(mapping), encoding="utf-8")
    with pytest.raises(AdapterMappingError, match="omits classifications"):
        load_adapter_mapping(path, schema_path=root / "schemas/adapter-mapping.schema.json")


def test_adapter_mapping_rejects_false_exact_equivalence(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    mapping = _mapping()
    mapping["mappings"][0]["riopa_field"] = None  # type: ignore[index]
    path = tmp_path / "mapping.json"
    path.write_text(json.dumps(mapping), encoding="utf-8")
    with pytest.raises(AdapterMappingError, match="riopa_field"):
        load_adapter_mapping(path, schema_path=root / "schemas/adapter-mapping.schema.json")


def test_cross_repository_report_is_sorted_and_rejects_duplicates(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    loaded = []
    for repository in ("edithatogo/zeta", "edithatogo/alpha"):
        path = tmp_path / f"{repository.rsplit('/', 1)[1]}.json"
        path.write_text(json.dumps(_mapping(repository)), encoding="utf-8")
        loaded.append(
            load_adapter_mapping(path, schema_path=root / "schemas/adapter-mapping.schema.json")
        )
    report = cross_repository_mapping_report(loaded)
    assert [item["repository"] for item in report["repositories"]] == [
        "edithatogo/alpha",
        "edithatogo/zeta",
    ]
    assert report["repositories"][0]["classification_counts"] == {
        "exact": 1,
        "approximate": 1,
        "extension-only": 1,
        "unmapped": 1,
    }
    with pytest.raises(AdapterMappingError, match="unique"):
        cross_repository_mapping_report([loaded[0], loaded[0]])


def test_committed_cross_repository_profiles_match_report() -> None:
    root = Path(__file__).resolve().parents[1]
    profile_dir = root / "conformance/adapters"
    mappings = [
        load_adapter_mapping(path, schema_path=root / "schemas/adapter-mapping.schema.json")
        for path in sorted(profile_dir.glob("fyi-*.json"))
    ]
    assert [mapping["repository"] for mapping in mappings] == [
        "edithatogo/fyi-archive",
        "edithatogo/fyi-cli",
    ]
    report = cross_repository_mapping_report(mappings)
    assert report == json.loads((profile_dir / "report.json").read_text(encoding="utf-8"))
