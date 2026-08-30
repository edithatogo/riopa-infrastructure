from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path

import pytest
from shapely import Point, to_wkb

from riopa_provenance.hashing import sha256_file, sha256_json

SCRIPT = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/compare_tasman_snapshots.py")
)
CAPTURE = "urn:uuid:00000000-0000-4000-8000-000000000001"


def payload(ids: tuple[int, ...] = (1, 2)) -> dict:
    rows, features = [], []
    for number in ids:
        identity = f"urn:riopa:feature:{number:064x}"
        geometry = to_wkb(Point(number, 2)).hex()
        rows.append(
            {
                "_riopa_source_object_id": str(number),
                "_riopa_feature_id": identity,
                "_riopa_capture_ids": json.dumps([CAPTURE]),
                "OBJECTID": number,
                "NAME": "zone",
                "geometry": geometry,
            }
        )
        features.append(
            {
                "feature_id": identity,
                "source_object_id": str(number),
                "capture_ids": [CAPTURE],
                "geometry_sha256": sha256_json(geometry),
                "valid_time": {"from": None, "to": None, "status": "unknown-not-imputed"},
                "recorded_time": {"at": "2026-08-31T00:00:00Z", "basis": "archive-capture-date"},
            }
        )
    return {
        "record_type": "tasman_canonical_projected_rows",
        "rows": rows,
        "canonical_features": features,
        "valid_time": "unknown-not-imputed",
        "source_manifest_sha256": "a" * 64,
    }


def save(path: Path, value: dict) -> str:
    path.write_text(json.dumps(value))
    return sha256_file(path)


def test_new_capture_metadata_does_not_imply_change(tmp_path: Path) -> None:
    before = payload()
    after = copy.deepcopy(before)
    after["source_manifest_sha256"] = "b" * 64
    for row, feature in zip(after["rows"], after["canonical_features"], strict=True):
        capture = CAPTURE[:-1] + "2"
        row["_riopa_capture_ids"] = json.dumps([capture])
        row["_riopa_feature_id"] = "urn:riopa:feature:" + f"{100 + row['OBJECTID']:064x}"
        feature["feature_id"] = row["_riopa_feature_id"]
        feature["capture_ids"] = [capture]
        feature["recorded_time"]["at"] = "2026-09-01T00:00:00Z"
    a, b = tmp_path / "before", tmp_path / "after"
    result = SCRIPT["compare"](a, b, save(a, before), save(b, after))
    assert not any(result[k] for k in ("added", "removed", "attribute_changed", "geometry_changed"))
    assert (
        result["before"]["comparison_content_sha256"]
        == result["after"]["comparison_content_sha256"]
    )


def test_exact_attribute_geometry_and_membership_changes(tmp_path: Path) -> None:
    before, after = payload((1, 2, 10)), payload((1, 2, 3))
    after["rows"][0]["NAME"] = "changed"
    after["rows"][1]["geometry"] = to_wkb(Point(5, 5), byte_order=0).hex()
    after["canonical_features"][1]["geometry_sha256"] = sha256_json(after["rows"][1]["geometry"])
    a, b = tmp_path / "before", tmp_path / "after"
    result = SCRIPT["compare"](a, b, save(a, before), save(b, after))
    assert result["added"] == ["3"] and result["removed"] == ["10"]
    assert result["attribute_changed"] == ["1"] and result["geometry_changed"] == ["2"]
    assert sha256_json(result, omit_keys={"comparison_sha256"}) == result["comparison_sha256"]


def test_other_prefixed_source_attributes_remain_meaningful(tmp_path: Path) -> None:
    before, after = payload((1,)), payload((1,))
    before["rows"][0]["_riopa_source_geometry_sha256"] = "a"
    after["rows"][0]["_riopa_source_geometry_sha256"] = "b"
    a, b = tmp_path / "before", tmp_path / "after"
    assert SCRIPT["compare"](a, b, save(a, before), save(b, after))["attribute_changed"] == ["1"]


@pytest.mark.parametrize(
    "tamper",
    [
        "duplicate",
        "missing-id",
        "unaligned",
        "count",
        "geometry-hash",
        "geometry-bytes",
        "capture",
        "time",
        "valid-time",
        "source",
        "objectid",
    ],
)
def test_invalid_canonical_binding_rejected(tmp_path: Path, tamper: str) -> None:
    value = payload()
    row, feature = value["rows"][0], value["canonical_features"][0]
    if tamper == "duplicate":
        value["rows"][1] = copy.deepcopy(row)
    elif tamper == "missing-id":
        row.pop("_riopa_source_object_id")
    elif tamper == "unaligned":
        feature["feature_id"] = "urn:riopa:feature:" + "f" * 64
    elif tamper == "count":
        value["canonical_features"].pop()
    elif tamper == "geometry-hash":
        feature["geometry_sha256"] = "0" * 64
    elif tamper == "geometry-bytes":
        row["geometry"] = "not-wkb"
    elif tamper == "capture":
        feature["capture_ids"] = []
    elif tamper == "time":
        feature["recorded_time"]["at"] = "2026-08-31"
    elif tamper == "valid-time":
        feature["valid_time"]["from"] = "2026-01-01"
    elif tamper == "source":
        value["source_manifest_sha256"] = "bad"
    else:
        row["OBJECTID"] = 99
    path = tmp_path / "bad"
    digest = save(path, value)
    with pytest.raises(ValueError):
        SCRIPT["load"](path, digest)


def test_corruption_and_restored_retry(tmp_path: Path) -> None:
    path = tmp_path / "canonical"
    digest = save(path, payload())
    original = path.read_bytes()
    expected = SCRIPT["compare"](path, path, digest, digest)
    path.write_bytes(original + b" ")
    with pytest.raises(ValueError, match="digest mismatch"):
        SCRIPT["compare"](path, path, digest, digest)
    path.write_bytes(original)
    assert SCRIPT["compare"](path, path, digest, digest) == expected


@pytest.mark.parametrize("body", [b'{"x":1,"x":2}', b'{"x":NaN}'])
def test_ambiguous_json_rejected(tmp_path: Path, body: bytes) -> None:
    path = tmp_path / "canonical"
    path.write_bytes(body)
    with pytest.raises(ValueError):
        SCRIPT["load"](path, sha256_file(path))


def test_symlink_budget_and_output_protection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "canonical"
    digest = save(path, payload())
    link = tmp_path / "link"
    link.symlink_to(path)
    with pytest.raises(ValueError):
        SCRIPT["load"](link, digest)
    monkeypatch.setattr(
        "sys.argv",
        [
            "compare",
            "--before",
            str(path),
            "--after",
            str(path),
            "--before-sha256",
            digest,
            "--after-sha256",
            digest,
            "--output",
            str(path),
        ],
    )
    assert SCRIPT["main"]() == 1
    assert sha256_file(path) == digest
    monkeypatch.setitem(SCRIPT["load"].__globals__, "MAX_BYTES", 1)
    with pytest.raises(ValueError):
        SCRIPT["load"](path, digest)


def test_actual_canonical_producer_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    previous = runpy.run_path(str(Path(__file__).with_name("test_tasman_derivatives.py")))
    previous["test_real_source_projection_prepare_and_anonymous_replay"](tmp_path, monkeypatch)
    path = tmp_path / "work/derived-candidate/canonical.json"
    digest = sha256_file(path)
    result = SCRIPT["compare"](path, path, digest, digest)
    assert result["before"]["feature_count"] == 1 and not result["geometry_changed"]


def test_wkb_encoding_change_is_not_normalized_away(tmp_path: Path) -> None:
    before, after = payload((1,)), payload((1,))
    after["rows"][0]["geometry"] = to_wkb(Point(1, 2), byte_order=0).hex()
    after["canonical_features"][0]["geometry_sha256"] = sha256_json(after["rows"][0]["geometry"])
    a, b = tmp_path / "before", tmp_path / "after"
    result = SCRIPT["compare"](a, b, save(a, before), save(b, after))
    assert result["geometry_changed"] == ["1"] and not result["attribute_changed"]


def test_cli_metadata_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "canonical"
    digest = save(path, payload())
    output = tmp_path / "comparison.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "compare",
            "--before",
            str(path),
            "--after",
            str(path),
            "--before-sha256",
            digest,
            "--after-sha256",
            digest,
            "--output",
            str(output),
        ],
    )
    assert SCRIPT["main"]() == 0
    result = json.loads(output.read_bytes())
    assert not result["release_cycle_qualified"] and result["change_hashes"] == {}
