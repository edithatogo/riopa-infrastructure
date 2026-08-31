from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path

import pytest

from riopa_provenance.hashing import sha256_file, sha256_json

ROOT = Path(__file__).resolve().parents[1]
DIAGNOSTIC = runpy.run_path(str(ROOT / "scripts/diagnose_tasman_attribute_changes.py"))
FIXTURE = runpy.run_path(str(ROOT / "tests/test_tasman_snapshot_comparison.py"))


def run_diagnostic(tmp_path: Path, before: dict, after: dict) -> tuple[dict, tuple]:
    a, b = tmp_path / "before.json", tmp_path / "after.json"
    hashes = FIXTURE["save"](a, before), FIXTURE["save"](b, after)
    comparison = FIXTURE["SCRIPT"]["compare"](a, b, *hashes)
    inputs = a, b, *hashes, comparison["comparison_sha256"]
    original = a.read_bytes(), b.read_bytes()
    result = DIAGNOSTIC["diagnose"](*inputs)
    assert (a.read_bytes(), b.read_bytes()) == original
    assert result == DIAGNOSTIC["diagnose"](*inputs)
    assert result["diagnostics_sha256"] == sha256_json(result, omit_keys={"diagnostics_sha256"})
    return result, inputs


def test_field_counts_separate_membership_nested_values_and_generated_names(tmp_path: Path) -> None:
    before, after = FIXTURE["payload"]((1, 2, 10)), FIXTURE["payload"]((1, 2, 3))
    for row in before["rows"]:
        row["details"] = {"nested": [1, 2]}
        row["_riopa_source_geometry_sha256"] = "old-value-must-not-leak"
    for row in after["rows"]:
        row["details"] = {"nested": [2, 1]}
        row["_riopa_source_geometry_sha256"] = "new-value-must-not-leak"
    after["rows"][0]["NAME"] = "SECRET-sensitive-value"
    after["rows"][1]["nullable"] = None
    result, _ = run_diagnostic(tmp_path, before, after)
    fields = {entry["name"]: entry for entry in result["fields"]}
    assert {name: entry["changed_feature_count"] for name, entry in fields.items()} == {
        "NAME": 1,
        "_riopa_source_geometry_sha256": 2,
        "details": 2,
        "nullable": 1,
    }
    assert fields["_riopa_source_geometry_sha256"]["classification"] == "riopa-prefixed"
    assert fields["NAME"]["classification"] == "source-field"
    assert result["shared_feature_count"] == result["attribute_changed_feature_count"] == 2
    assert result["added_feature_count"] == result["removed_feature_count"] == 1
    assert result["geometry_changed_feature_count"] == 0
    assert result["release_cycle_qualified"] is False
    assert all(value not in json.dumps(result) for value in ("SECRET", "old-value", "new-value"))


def test_ignored_capture_fields_are_visible_but_not_attribute_changes(tmp_path: Path) -> None:
    before = FIXTURE["payload"]((1,))
    after = copy.deepcopy(before)
    capture = "urn:uuid:00000000-0000-4000-8000-000000000002"
    after["rows"][0]["_riopa_capture_ids"] = json.dumps([capture])
    after["canonical_features"][0]["capture_ids"] = [capture]
    result, _ = run_diagnostic(tmp_path, before, after)
    assert result["attribute_changed_feature_count"] == 0
    assert result["fields"] == [
        {
            "name": "_riopa_capture_ids",
            "classification": "riopa-prefixed",
            "changed_feature_count": 1,
            "included_in_attribute_comparison": False,
        }
    ]


@pytest.mark.parametrize("fault", ["digest", "comparison", "changed-bytes", "invalid-lineage"])
def test_invalid_bindings_fail_closed(tmp_path: Path, fault: str) -> None:
    value = FIXTURE["payload"]()
    _, inputs = run_diagnostic(tmp_path, value, value)
    args = list(inputs)
    if fault == "digest":
        args[2] = "0" * 64
    elif fault == "comparison":
        args[4] = "0" * 64
    elif fault == "changed-bytes":
        args[0].write_text("{}")
    else:
        value["canonical_features"][0]["capture_ids"] = []
        args[2] = FIXTURE["save"](args[0], value)
    with pytest.raises(ValueError):
        DIAGNOSTIC["diagnose"](*args)


def test_actual_archiver_projection_fixture_is_accepted(tmp_path: Path, monkeypatch) -> None:
    previous = runpy.run_path(str(ROOT / "tests/test_tasman_derivatives.py"))
    previous["test_real_source_projection_prepare_and_anonymous_replay"](tmp_path, monkeypatch)
    path = tmp_path / "work/derived-candidate/canonical.json"
    checksum = sha256_file(path)
    comparison = FIXTURE["SCRIPT"]["compare"](path, path, checksum, checksum)
    result = DIAGNOSTIC["diagnose"](path, path, checksum, checksum, comparison["comparison_sha256"])
    assert result["shared_feature_count"] == 1 and result["fields"] == []


def test_recorder_writes_separate_diagnostic_without_extra_download(
    tmp_path: Path, monkeypatch
) -> None:
    runner = runpy.run_path(str(ROOT / "tests/test_tasman_snapshot_comparison_runner.py"))
    context = runner["context"].__wrapped__(tmp_path, monkeypatch)
    comparison = runner["invoke"](context)
    path = context["work"] / "public/tasman-attribute-diagnostics.json"
    diagnostic = json.loads(path.read_bytes())
    assert diagnostic["comparison_sha256"] == comparison["comparison"]["comparison_sha256"]
    assert diagnostic["before_canonical_sha256"] == comparison["baseline_canonical_sha256"]
    assert diagnostic["after_canonical_sha256"] == comparison["current_canonical_sha256"]
    assert diagnostic["fields"] == [] and len(context["downloads"]) == 1
    assert "diagnostics" not in comparison


def test_existing_diagnostic_is_preserved_and_prevents_recorder_side_effects(
    tmp_path: Path, monkeypatch
) -> None:
    runner = runpy.run_path(str(ROOT / "tests/test_tasman_snapshot_comparison_runner.py"))
    context = runner["context"].__wrapped__(tmp_path, monkeypatch)
    path = context["work"] / "public/tasman-attribute-diagnostics.json"
    path.write_text("original evidence")
    with pytest.raises(ValueError, match="fresh"):
        runner["invoke"](context)
    assert path.read_text() == "original evidence"
    assert not (path.parent / "tasman-snapshot-comparison.json").exists()
    assert context["downloads"] == []
