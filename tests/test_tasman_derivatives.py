from __future__ import annotations

import json
import runpy
import shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import duckdb
import pytest

from riopa_provenance.hashing import sha256_file

SCRIPT = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/publish_tasman_derivatives.py")
)


def test_real_source_projection_prepare_and_anonymous_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from riopa_provenance import tasman_public_packet

    previous = runpy.run_path(str(Path(__file__).with_name("test_tasman_publication.py")))
    previous["test_real_restore_prepare_public_packet_and_two_rebuilds"](tmp_path, monkeypatch)
    with patch.dict(
        SCRIPT["prepare"].__globals__, {"LICENCE_SHA256": tasman_public_packet.LICENCE_SHA256}
    ):
        candidate, manifest = SCRIPT["prepare"](tmp_path / "work")
    assert manifest["identity"]["feature_count"] == 1
    canonical = json.loads((candidate / "canonical.json").read_bytes())
    assert canonical["canonical_features"][0]["recorded_time"]
    assert canonical["rows"][0]["geometry"]
    api = SimpleNamespace(
        list_repo_tree=lambda *a, **k: [
            SimpleNamespace(path="prefix/" + p.name, size=p.stat().st_size)
            for p in candidate.iterdir()
        ]
    )

    def download(repo: str, name: str, **kwargs: object) -> str:
        assert kwargs["token"] is False and kwargs["revision"] == "a" * 40
        return str(candidate / name.split("/")[-1])

    # Expected fresh DuckDB bytes may differ; original published bytes remain authoritative.
    fresh = json.loads(json.dumps(manifest))
    fresh_database = tmp_path / "fresh.duckdb"
    shutil.copyfile(candidate / "features.duckdb", fresh_database)
    with duckdb.connect(str(fresh_database)) as connection:
        connection.execute("CREATE TABLE additional_storage_metadata(value INTEGER)")
    fresh["files"]["features.duckdb"]["sha256"] = sha256_file(fresh_database)
    fresh["files"]["features.duckdb"]["bytes"] = fresh_database.stat().st_size
    assert sha256_file(fresh_database) != manifest["files"]["features.duckdb"]["sha256"]
    assert SCRIPT["rows"](fresh_database, database=True) == canonical["rows"]
    with patch.dict(SCRIPT["verify_remote"].__globals__, {"hf_hub_download": download}):
        verified = SCRIPT["verify_remote"](
            api,
            "prefix",
            "a" * 40,
            fresh,
            tmp_path / "readback",
            sha256_file(candidate / "manifest.json"),
        )
    assert (
        verified["files"]["features.duckdb"]["sha256"]
        == manifest["files"]["features.duckdb"]["sha256"]
    )


@pytest.mark.parametrize(
    "scenario", ["new", "replay", "recover", "corrupt", "save-fails", "visibility"]
)
def test_publication_preserves_revision_and_failure_evidence(tmp_path: Path, scenario: str) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "manifest.json").write_text("{}")
    for name in SCRIPT["NAMES"] - {"manifest.json"}:
        (candidate / name).write_bytes(b"fixture")
    manifest = {"logical_sha256": "a" * 64, "identity": {}, "files": {}}
    checkpoint = {
        "logical_sha256": "a" * 64,
        "prefix": "derivatives/tasman-zones/" + "a" * 64,
        "public_revision": "b" * 40,
        "manifest_sha256": "c" * 64,
    }
    commits = []

    def commit(api: object, repo: str, files: dict) -> str:
        if scenario == "save-fails" and any("attempts/" in n for n in files):
            raise OSError("SECRET")
        commits.append((repo, files))
        return "b" * 40

    def verify(*args: object) -> dict:
        if scenario in ("corrupt", "save-fails"):
            raise ValueError("SECRET failure path")
        assert args[2] == "b" * 40
        return {**manifest, "_manifest_sha256": "c" * 64}

    def visibility(api: object) -> None:
        if scenario == "visibility":
            raise ValueError("SECRET private repo public")

    hosted = {**SCRIPT["HOSTED"], "commit_files": commit, "require_visibility": visibility}
    publisher = {
        **SCRIPT["PUBLISHER"],
        "control": lambda *a, **k: checkpoint if scenario == "replay" else None,
    }
    api = SimpleNamespace(
        get_paths_info=lambda *a, **k: (
            [SimpleNamespace(last_commit=SimpleNamespace(oid="b" * 40))]
            if scenario == "recover"
            else []
        )
    )
    with patch.dict(
        SCRIPT["publish"].__globals__,
        {
            "HOSTED": hosted,
            "PUBLISHER": publisher,
            "prepare": lambda _: (candidate, manifest),
            "verify_remote": verify,
        },
    ):
        if scenario in ("corrupt", "save-fails", "visibility"):
            with pytest.raises(ValueError):
                SCRIPT["publish"](api, tmp_path)
            path = tmp_path / "public/tasman-derivatives-failure.json"
            assert "SECRET" not in path.read_text()
            if scenario == "save-fails":
                assert json.loads(path.read_bytes())["durable_error_class"] == "OSError"
        else:
            result = SCRIPT["publish"](api, tmp_path)
            assert result["public_revision"] == "b" * 40
    assert len([c for c in commits if c[0] == SCRIPT["PUBLIC"]]) == (
        1 if scenario in ("new", "corrupt", "save-fails") else 0
    )


@pytest.mark.parametrize("scenario", ["extra", "oversize", "badrevision", "metadata", "digest"])
def test_remote_integrity_guards(tmp_path: Path, scenario: str) -> None:
    data = {
        "logical_sha256": "a" * 64,
        "identity": {},
        "licence": "CC-BY-4.0",
        "attribution": SCRIPT["ATTRIBUTION"],
        "files": {},
    }
    path = tmp_path / "manifest"
    path.write_text(json.dumps(data))
    names = SCRIPT["NAMES"] | ({"extra"} if scenario == "extra" else set())
    api = SimpleNamespace(
        list_repo_tree=lambda *a, **k: [
            SimpleNamespace(
                path="prefix/" + n,
                size=999999999 if scenario == "oversize" else path.stat().st_size,
            )
            for n in names
        ]
    )
    expected = {**data, "attribution": "wrong"} if scenario == "metadata" else data
    with (
        patch.dict(
            SCRIPT["verify_remote"].__globals__, {"hf_hub_download": lambda *a, **k: str(path)}
        ),
        pytest.raises(ValueError),
    ):
        SCRIPT["verify_remote"](
            api,
            "prefix",
            "bad" if scenario == "badrevision" else "b" * 40,
            expected,
            tmp_path / "download",
            "0" * 64 if scenario == "digest" else None,
        )


def test_input_path_bounds(tmp_path: Path) -> None:
    path = tmp_path / "data"
    path.write_bytes(b"data")
    link = tmp_path / "link"
    link.symlink_to(path)
    with pytest.raises(ValueError):
        SCRIPT["checked"](link, tmp_path)
    with pytest.raises(ValueError):
        SCRIPT["checked"](tmp_path / "missing", tmp_path)


def test_main_rejects_local_execution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr("sys.argv", ["derivatives", "--work", str(tmp_path)])
    with pytest.raises(SystemExit):
        SCRIPT["main"]()
