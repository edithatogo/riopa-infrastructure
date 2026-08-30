from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from riopa_provenance.hashing import sha256_bytes, sha256_json

SCRIPT = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/record_tasman_snapshot_comparison.py")
)


@pytest.fixture
def context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    for key, value in {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_REPOSITORY": SCRIPT["REPOSITORY"],
    }.items():
        monkeypatch.setenv(key, value)
    work = tmp_path / "work"
    (work / "public").mkdir(parents=True)
    (work / "derived-candidate").mkdir()
    capture = "urn:uuid:00000000-0000-4000-8000-000000000001"
    feature_id = "urn:riopa:feature:" + "f" * 64
    row = {
        "OBJECTID": 1,
        "zone": "residential",
        "_riopa_source_object_id": "1",
        "_riopa_feature_id": feature_id,
        "_riopa_capture_ids": json.dumps([capture]),
        "geometry": None,
    }
    canonical = {
        "record_type": "tasman_canonical_projected_rows",
        "valid_time": "unknown-not-imputed",
        "source_manifest_sha256": "a" * 64,
        "rows": [row],
        "canonical_features": [
            {
                "source_object_id": "1",
                "feature_id": feature_id,
                "capture_ids": [capture],
                "geometry_sha256": sha256_json(None),
                "valid_time": {"from": None, "to": None, "status": "unknown-not-imputed"},
                "recorded_time": {"at": "2026-08-31T00:00:00Z", "basis": "archive-capture-date"},
            }
        ],
    }
    body = json.dumps(canonical).encode()
    file_entry = {"sha256": sha256_bytes(body), "bytes": len(body)}
    identity = {
        "profile": "tasman-derived-v1",
        "source_revision": "b" * 40,
        "source_manifest_sha256": "a" * 64,
        "feature_count": 1,
        "geoparquet_sha256": "c" * 64,
        "canonical_sha256": sha256_json(canonical),
    }
    logical = sha256_json(identity)
    derived = {
        "status": "derivatives-published-and-verified",
        "state": "verified",
        "public_repository": SCRIPT["PUBLIC"],
        "licence": "CC-BY-4.0",
        "attribution": SCRIPT["ATTRIBUTION"],
        "identity": identity,
        "logical_sha256": logical,
        "prefix": f"derivatives/tasman-zones/{logical}",
        "public_revision": "d" * 40,
        "manifest_sha256": "e" * 64,
        "files": {"canonical.json": file_entry},
    }
    source = {
        "status": "public-packet-verified-and-rebuilt",
        "state": "verified",
        "anonymous_full_packet_verified": True,
        "source_id": "urn:riopa:source:tasman:geohub",
        "public_dataset_repository": SCRIPT["PUBLIC"],
        "licence": "CC-BY-4.0",
        "attribution": SCRIPT["ATTRIBUTION"],
        "packet_manifest_sha256": "a" * 64,
        "public_revision": "b" * 40,
        "reproduction": {"feature_count": 1, "geoparquet_sha256": "c" * 64},
    }
    manifest = {
        "record_type": "tasman_derived_public_packet",
        "identity": identity,
        "logical_sha256": logical,
        "licence": "CC-BY-4.0",
        "attribution": SCRIPT["ATTRIBUTION"],
        "files": {"canonical.json": file_entry},
    }
    baseline = tmp_path / "baseline.json"
    baseline.write_text(
        json.dumps(
            {
                "status": "hosted-derived-publication-and-replay-verified",
                "track": "nz_spatial_archive_mvp_20260718",
                "publication_receipt": copy.deepcopy(derived),
            }
        )
    )
    for path, value in [
        (work / "public/tasman-publication.json", source),
        (work / "public/tasman-derivatives.json", derived),
        (work / "derived-candidate/manifest.json", manifest),
    ]:
        path.write_text(json.dumps(value))
    (work / "derived-candidate/canonical.json").write_bytes(body)
    return {
        "work": work,
        "baseline": baseline,
        "body": body,
        "derived": derived,
        "downloads": [],
        "private": False,
        "remote_size": len(body),
        "remote_path": derived["prefix"] + "/canonical.json",
        "corrupt": False,
        "escape": False,
    }


def invoke(context: dict, *, main: bool = False) -> dict | int:
    def repo_info(repo: str, **kwargs: object) -> SimpleNamespace:
        assert repo == SCRIPT["PUBLIC"] and kwargs["token"] is False
        return SimpleNamespace(private=context["private"])

    def info(repo: str, names: list[str], **kwargs: object) -> list:
        assert repo == SCRIPT["PUBLIC"] and kwargs["token"] is False
        assert kwargs["revision"] == "d" * 40 and len(names) == 1
        return [SimpleNamespace(path=context["remote_path"], size=context["remote_size"])]

    def download(repo: str, name: str, **kwargs: object) -> str:
        assert repo == SCRIPT["PUBLIC"] and kwargs["token"] is False
        assert kwargs["revision"] == "d" * 40 and kwargs["force_download"] is True
        context["downloads"].append(name)
        target = Path(kwargs["local_dir"]) / name
        if context["escape"]:
            target = context["work"].parent / "outside.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x" * len(context["body"]) if context["corrupt"] else context["body"])
        return str(target)

    def client(*, token: bool) -> SimpleNamespace:
        assert token is False
        return SimpleNamespace(repo_info=repo_info, get_paths_info=info)

    with patch.dict(
        SCRIPT["record"].__globals__,
        {"BASELINE": context["baseline"], "HfApi": client, "hf_hub_download": download},
    ):
        if main:
            with patch("sys.argv", ["comparison", "--work", str(context["work"])]):
                return SCRIPT["main"]()
        return SCRIPT["record"](context["work"])


def test_real_comparator_anonymous_fixed_baseline(context: dict) -> None:
    result = invoke(context)
    assert result["status"] == "compared"
    assert result["baseline_role"] == "fixed-initial-accepted-packet-not-previous-cycle"
    assert result["comparison"]["added"] == []
    assert result["comparison"]["attribute_changed"] == []
    assert result["comparison"]["before"]["feature_count"] == 1
    assert not result["release_cycle_qualified"]
    assert len(context["downloads"]) == 1
    assert result["derived_public_revision"] == context["derived"]["public_revision"]


@pytest.mark.parametrize(
    "scenario",
    [
        "private",
        "oversize",
        "remote-path",
        "corrupt",
        "escape",
        "current-digest",
        "receipt-state",
        "receipt-path",
        "manifest",
        "symlink",
        "bad-baseline",
    ],
)
def test_invalid_inputs_never_emit_success(context: dict, scenario: str) -> None:
    if scenario == "private":
        context["private"] = True
    elif scenario == "oversize":
        context["remote_size"] = SCRIPT["LIMIT"] + 1
    elif scenario == "remote-path":
        context["remote_path"] = "../outside.json"
    elif scenario in ("corrupt", "escape"):
        context[scenario] = True
    elif scenario == "current-digest":
        (context["work"] / "derived-candidate/canonical.json").write_bytes(b"bad")
    elif scenario == "symlink":
        path = context["work"] / "derived-candidate/canonical.json"
        other = context["work"].parent / "other.json"
        path.rename(other)
        path.symlink_to(other)
    else:
        path = (
            context["baseline"]
            if scenario == "bad-baseline"
            else context["work"]
            / (
                "derived-candidate/manifest.json"
                if scenario == "manifest"
                else "public/tasman-derivatives.json"
            )
        )
        value = json.loads(path.read_bytes())
        if scenario == "receipt-state":
            value["state"] = "pending"
        elif scenario == "receipt-path":
            value["prefix"] = "../escape"
        elif scenario == "manifest":
            value["identity"] = {}
        else:
            value["status"] = "pending"
        path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        invoke(context)
    assert not (context["work"] / "public/tasman-snapshot-comparison.json").exists()
    if scenario in ("private", "oversize", "remote-path"):
        assert not context["downloads"]


def test_corrupt_download_then_verified_retry(
    context: dict, capsys: pytest.CaptureFixture[str]
) -> None:
    context["corrupt"] = True
    assert invoke(context, main=True) == 1
    assert not (context["work"] / "public/tasman-snapshot-comparison.json").exists()
    context["corrupt"] = False
    assert invoke(context, main=True) == 0
    assert len(context["downloads"]) == 2
    assert (context["work"] / "public/tasman-snapshot-comparison-failure.json").exists()
    assert (context["work"] / "public/tasman-snapshot-comparison.json").exists()
    assert "Traceback" not in capsys.readouterr().out


def test_context_guard_precedes_network(context: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_REPOSITORY", "wrong/repo")
    with pytest.raises(ValueError):
        invoke(context)
    assert not context["downloads"]


@pytest.mark.parametrize(
    "field,value",
    [("canonical_sha256", "0" * 64), ("source_manifest_sha256", "1" * 64), ("feature_count", 2)],
)
def test_baseline_content_must_match_receipt_identity(
    context: dict, field: str, value: object
) -> None:
    path = context["baseline"]
    document = json.loads(path.read_bytes())
    receipt = document["publication_receipt"]
    receipt["identity"][field] = value
    receipt["logical_sha256"] = sha256_json(receipt["identity"])
    receipt["prefix"] = f"derivatives/tasman-zones/{receipt['logical_sha256']}"
    context["remote_path"] = receipt["prefix"] + "/canonical.json"
    path.write_text(json.dumps(document))
    with pytest.raises(ValueError, match="canonical semantics"):
        invoke(context)
    assert len(context["downloads"]) == 1
    assert not (context["work"] / "public/tasman-snapshot-comparison.json").exists()


def test_bool_feature_count_rejected(context: dict) -> None:
    value = copy.deepcopy(context["derived"])
    value["identity"]["feature_count"] = True
    value["logical_sha256"] = sha256_json(value["identity"])
    value["prefix"] = f"derivatives/tasman-zones/{value['logical_sha256']}"
    with pytest.raises(ValueError, match="feature count"):
        SCRIPT["derived_receipt"](value)


def test_failure_message_is_sanitized(context: dict, capsys: pytest.CaptureFixture[str]) -> None:
    with (
        patch.dict(
            SCRIPT["main"].__globals__,
            {"record": lambda _: (_ for _ in ()).throw(ValueError("SECRET token/path"))},
        ),
        patch("sys.argv", ["comparison", "--work", str(context["work"])]),
    ):
        assert SCRIPT["main"]() == 1
    assert "SECRET" not in capsys.readouterr().out
    assert (
        "SECRET"
        not in (context["work"] / "public/tasman-snapshot-comparison-failure.json").read_text()
    )
