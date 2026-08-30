from __future__ import annotations

import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from riopa_provenance.hashing import sha256_file

SCRIPT = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/publish_tasman_public_packet.py")
)


@pytest.mark.parametrize(
    "scenario",
    [
        "new",
        "resume",
        "recover",
        "wrong-checkpoint",
        "incomplete",
        "rebuild-fails",
        "anonymous-fails",
        "failure-save-fails",
        "resume-fails",
    ],
)
def test_publication_original_revision_and_checkpoint_order(tmp_path: Path, scenario: str) -> None:
    work = tmp_path / "work"
    commits = []
    original = {
        "source": "tasman",
        "run_id": "123",
        "acquisition_complete": scenario != "incomplete",
        "manifest_sha256": "a" * 64,
    }
    saved = {
        "private_manifest_sha256": "a" * 64,
        "packet_manifest_sha256": "b" * 64,
        "prefix": "snapshots/tasman-zones/" + "b" * 64,
        "public_revision": "c" * 40,
    }
    if scenario == "wrong-checkpoint":
        saved["packet_manifest_sha256"] = "d" * 64

    def control(_api: object, name: str, _work: Path, **_: object) -> dict | None:
        if name.startswith("campaigns/"):
            return {"prefix": "campaigns/123/tasman/1", "revision": "a" * 40}
        return saved if scenario in ("resume", "wrong-checkpoint", "resume-fails") else None

    def prepare(path: Path) -> dict:
        candidate = path / "tasman-public-candidate"
        candidate.mkdir()
        (candidate / "manifest.json").write_text(
            json.dumps(
                {
                    "source_id": "source",
                    "licence": "CC-BY-4.0",
                    "attribution": "fixture",
                    "rights_capture_id": "fixture",
                    "rights_object_sha256": "f" * 64,
                    "rights_licence_text": "fixture",
                    "capture_set_id": "fixture",
                    "files": [],
                }
            )
        )
        return {"manifest_sha256": "b" * 64}

    def commit(_api: object, repo: str, files: dict) -> str:
        if scenario == "failure-save-fails" and any("/attempts/" in name for name in files):
            raise RuntimeError("secondary SECRET private/path token")
        commits.append((repo, files))
        return "c" * 40

    checks = []

    def readback(*args: object) -> None:
        checks.append(args[-1])
        if scenario == "anonymous-fails":
            raise ValueError("SECRET token private/path")

    def rebuild(*args: object) -> dict:
        if scenario in ("rebuild-fails", "failure-save-fails", "resume-fails"):
            raise ValueError("SECRET token private/path")
        return {"builds": 2}

    api = SimpleNamespace(
        repo_info=lambda *a, **k: SimpleNamespace(sha="e" * 40),
        get_paths_info=lambda *a, **k: (
            [SimpleNamespace(last_commit=SimpleNamespace(oid="c" * 40))]
            if scenario == "recover"
            else []
        ),
    )
    hosted = {
        **SCRIPT["HOSTED"],
        "require_visibility": lambda _: None,
        "checked_manifest": lambda *a: original,
        "verify_public_checkpoint": lambda *a: None,
        "commit_files": commit,
    }
    with patch.dict(
        SCRIPT["publish"].__globals__,
        {
            "HOSTED": hosted,
            "control": control,
            "restore": lambda *a: None,
            "PREPARE": prepare,
            "verify_public_archive_packet": lambda *a, **k: None,
            "descriptor": lambda *a: a[-1],
            "readback": readback,
            "rebuild": rebuild,
        },
    ):
        if scenario in (
            "wrong-checkpoint",
            "incomplete",
            "rebuild-fails",
            "anonymous-fails",
            "failure-save-fails",
            "resume-fails",
        ):
            with pytest.raises(ValueError):
                SCRIPT["publish"](api, "123", work)
            assert not (work / "public/tasman-publication.json").exists()
            failure_path = work / "public/tasman-publication-failure.json"
            failure = json.loads(failure_path.read_bytes())
            assert failure["status"] == "failed"
            assert (
                "SECRET" not in failure_path.read_text()
                and "private/path" not in failure_path.read_text()
            )
            if scenario == "anonymous-fails":
                assert failure["stage"] == "anonymous-readback"
            if scenario in ("rebuild-fails", "failure-save-fails", "resume-fails"):
                assert failure["stage"] == "rebuild"
                assert failure["public_revision"] == "c" * 40
            if scenario == "failure-save-fails":
                assert failure["durable_failure_record"] is False
                assert failure["failure_record_error_class"] == "RuntimeError"
            if scenario == "resume-fails":
                assert all("/attempts/" in name for _, files in commits for name in files)
        else:
            result = SCRIPT["publish"](api, "123", work)
            assert result["public_revision"] == "c" * 40
            assert result["anonymous_full_packet_verified"]
            assert all(revision == "c" * 40 for revision in checks)
        public_commits = [c for c in commits if c[0] == SCRIPT["PUBLIC"]]
        assert len(public_commits) == (
            1
            if scenario in ("new", "rebuild-fails", "anonymous-fails", "failure-save-fails")
            else 0
        )


@pytest.mark.parametrize("scenario", ["ok", "extra", "size", "bytes", "workers", "existing"])
def test_anonymous_clean_packet_download(tmp_path: Path, scenario: str) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "manifest.json").write_bytes(b"{}")
    target = tmp_path / "download"
    if scenario == "existing":
        target.mkdir()
    files = [SimpleNamespace(path="snapshot/manifest.json", size=3 if scenario == "size" else 2)]
    if scenario == "extra":
        files.append(SimpleNamespace(path="snapshot/extra", size=1))
    api = SimpleNamespace(list_repo_tree=lambda *a, **k: iter(files))
    binding = SimpleNamespace(packet_path="snapshot", packet_revision="a" * 40)

    def download(*args: object, **kwargs: object) -> str:
        assert kwargs["token"] is False and kwargs["revision"] == "a" * 40
        path = tmp_path / "cached-file"
        path.write_bytes(b"xx" if scenario == "bytes" else b"{}")
        return str(path)

    with patch.dict(
        SCRIPT["readback"].__globals__,
        {"hf_hub_download": download, "verify_public_archive_packet": lambda *a, **k: None},
    ):
        if scenario != "ok":
            with pytest.raises(ValueError):
                SCRIPT["readback"](
                    api,
                    candidate,
                    target,
                    tmp_path / "cache",
                    binding,
                    workers=5 if scenario == "workers" else 2,
                )
        else:
            SCRIPT["readback"](api, candidate, target, tmp_path / "cache", binding)
            assert sorted(p.name for p in target.iterdir()) == ["manifest.json"]
            assert sha256_file(target / "manifest.json") == sha256_file(candidate / "manifest.json")


@pytest.mark.parametrize(
    "changed", [None, "canonical_features", "geoparquet", "duckdb", "feature_count"]
)
def test_rebuild_compares_semantics_not_duckdb_file(tmp_path: Path, changed: str | None) -> None:
    count = 0

    def materialize(*args: object, **kwargs: object) -> SimpleNamespace:
        nonlocal count
        count += 1
        path = tmp_path / f"evidence-{count}.json"
        value = {
            "canonical_features": [],
            "geoparquet": {"sha256": "a"},
            "duckdb": {"semantic_sha256": "b"},
            "feature_count": 0,
        }
        if count == 2 and changed:
            value[changed] = "different"
        path.write_text(json.dumps(value))
        return SimpleNamespace(evidence_path=path)

    with patch.dict(
        SCRIPT["rebuild"].__globals__, {"materialize_public_arcgis_packet": materialize}
    ):
        if changed:
            with pytest.raises(ValueError):
                SCRIPT["rebuild"](tmp_path, None, tmp_path / "build")
        else:
            assert SCRIPT["rebuild"](tmp_path, None, tmp_path / "build")["builds"] == 2


def test_safe_restore_preserves_bytes(tmp_path: Path) -> None:
    store = tmp_path / "store"
    store.mkdir()
    (store / "data").write_bytes(b"original")
    manifest = SCRIPT["HOSTED"]["pack"](store, tmp_path / "packet", {})
    target = tmp_path / "restored"
    SCRIPT["restore"](tmp_path / "packet/raw.tar", manifest, target)
    assert (target / "data").read_bytes() == b"original"
    with pytest.raises(ValueError):
        SCRIPT["restore"](tmp_path / "packet/raw.tar", manifest, target)


@pytest.mark.parametrize("scenario", ["ok", "missing", "oversize", "array"])
def test_bounded_pinned_private_control(tmp_path: Path, scenario: str) -> None:
    def info(*args: object, **kwargs: object) -> list:
        assert kwargs["revision"] == "a" * 40
        return (
            []
            if scenario == "missing"
            else [SimpleNamespace(size=999999 if scenario == "oversize" else 2)]
        )

    api = SimpleNamespace(
        token="fixture",
        repo_info=lambda *a, **k: SimpleNamespace(sha="a" * 40),
        get_paths_info=info,
    )
    path = tmp_path / "checkpoint"
    path.write_text("[]" if scenario == "array" else "{}")
    with patch.dict(SCRIPT["control"].__globals__, {"hf_hub_download": lambda *a, **k: str(path)}):
        if scenario in ("oversize", "array"):
            with pytest.raises(ValueError):
                SCRIPT["control"](api, "checkpoint", tmp_path)
        else:
            assert SCRIPT["control"](api, "checkpoint", tmp_path, missing=True) == (
                None if scenario == "missing" else {}
            )


@pytest.mark.parametrize("run", ["../bad", "", "123"])
def test_run_identity_and_fresh_workspace(tmp_path: Path, run: str) -> None:
    with pytest.raises(ValueError):
        SCRIPT["publish"](None, run, tmp_path)


def test_cli_rejects_non_actions(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr("sys.argv", ["publish", "--source-run", "123", "--work", str(tmp_path)])
    with pytest.raises(SystemExit):
        SCRIPT["main"]()


def test_real_restore_prepare_public_packet_and_two_rebuilds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import huggingface_hub

    from riopa_provenance.hashing import sha256_json

    fixtures = runpy.run_path(str(Path(__file__).with_name("test_tasman_public_packet.py")))
    source, capture_set, rights = fixtures["inputs"].__wrapped__(tmp_path / "fixture", monkeypatch)
    selected_set = json.loads(capture_set.read_bytes())
    fixtures["replace_payload"](
        source,
        selected_set["page_capture_ids"][0],
        {
            "spatialReference": {"wkid": 4326},
            "features": [
                {
                    "attributes": {"OBJECTID": 1},
                    "geometry": {
                        "rings": [
                            [
                                [174.8, -41.2],
                                [174.81, -41.2],
                                [174.81, -41.19],
                                [174.8, -41.19],
                                [174.8, -41.2],
                            ]
                        ]
                    },
                }
            ],
        },
    )
    rights_record = json.loads(
        (source / "captures" / f"{rights.removeprefix('urn:uuid:')}.json").read_bytes()
    )
    receipt = {
        "source_id": fixtures["builder"].SOURCE,
        "status": "captured",
        "zones": {
            "manifest_path": capture_set.name,
            "manifest_sha256": sha256_file(capture_set),
            "feature_count": 1,
        },
        "selected_item": {
            "rights_capture_id": rights,
            "rights_object_sha256": rights_record["object"]["sha256"],
        },
    }
    digest = sha256_json(receipt)
    receipt["semantic_sha256"] = digest
    (source / f"tasman-receipt-{digest}.json").write_text(json.dumps(receipt))
    packet = tmp_path / "raw-packet"
    manifest = SCRIPT["HOSTED"]["pack"](
        source, packet, {"source": "tasman", "run_id": "123", "acquisition_complete": True}
    )
    prefix = "campaigns/123/tasman/1"
    original_checkpoint = {
        "prefix": prefix,
        "revision": "a" * 40,
        "manifest_sha256": manifest["manifest_sha256"],
    }
    remote = {
        (SCRIPT["PRIVATE"], f"{prefix}/{name}"): (packet / name).read_bytes()
        for name in ("manifest.json", "raw.tar")
    }
    remote[SCRIPT["PRIVATE"], "campaigns/123/tasman/checkpoint.json"] = json.dumps(
        original_checkpoint
    ).encode()

    def paths(repo: str, names: list[str], **kwargs: object) -> list:
        return [
            SimpleNamespace(path=name, size=len(remote[repo, name]))
            for name in names
            if (repo, name) in remote
        ]

    def tree(repo: str, path_in_repo: str, **kwargs: object) -> list:
        assert kwargs["token"] is False
        return [
            SimpleNamespace(path=name, size=len(body))
            for (owner, name), body in remote.items()
            if owner == repo and name.startswith(path_in_repo + "/")
        ]

    def download(repo: str, name: str, **kwargs: object) -> str:
        if repo == SCRIPT["PUBLIC"]:
            assert kwargs["token"] is False
        root = Path(kwargs.get("local_dir", kwargs.get("cache_dir")))
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(remote[repo, name])
        return str(target)

    def commit(api: object, repo: str, files: dict) -> str:
        for name, value in files.items():
            remote[repo, name] = value.read_bytes() if isinstance(value, Path) else value
        return "c" * 40

    api = SimpleNamespace(
        token="fixture",
        repo_info=lambda repo, **kw: SimpleNamespace(
            sha="a" * 40, private=repo == SCRIPT["PRIVATE"]
        ),
        get_paths_info=paths,
        list_repo_tree=tree,
    )
    hosted = {
        **SCRIPT["HOSTED"],
        "commit_files": commit,
        "verify_public_checkpoint": lambda *a: None,
    }
    with (
        patch.object(huggingface_hub, "hf_hub_download", side_effect=download),
        patch.dict(SCRIPT["publish"].__globals__, {"HOSTED": hosted, "hf_hub_download": download}),
    ):
        result = SCRIPT["publish"](api, "123", tmp_path / "work")
    assert result["reproduction"]["feature_count"] == 1
    assert result["reproduction"]["builds"] == 2
    assert result["anonymous_full_packet_verified"] is True
    assert all(not name.endswith(".duckdb") for repo, name in remote if repo == SCRIPT["PUBLIC"])


@pytest.mark.parametrize("scenario", ["visibility", "local-save", "normal"])
def test_failure_record_preserves_original_exception_and_unique_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, scenario: str
) -> None:
    monkeypatch.setenv("GITHUB_RUN_ID", "unsafe/SECRET")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    original = ValueError("SECRET must never enter evidence")
    commits = []

    def fail(api: object, source: str, work: Path, progress: dict) -> None:
        progress.update(
            stage="anonymous-readback",
            visibility_verified=scenario != "visibility",
            public_revision="c" * 40,
        )
        raise original

    def commit(api: object, repo: str, files: dict) -> str:
        commits.append(files)
        return "d" * 40

    hosted = {**SCRIPT["HOSTED"], "commit_files": commit}
    # Keep the original writer outside the patched mapping to avoid recursion.
    original_writer = hosted["write_json"]

    def write_local(path: Path, value: dict) -> None:
        if scenario == "local-save":
            raise OSError("SECRET filesystem error")
        original_writer(path, value)

    hosted["write_json"] = write_local
    with patch.dict(SCRIPT["publish"].__globals__, {"_publish": fail, "HOSTED": hosted}):
        for number in (1, 2):
            with pytest.raises(ValueError) as caught:
                SCRIPT["publish"](None, "123", tmp_path / str(number))
            assert caught.value is original
    if scenario == "visibility":
        assert commits == []
    else:
        assert len(commits) == 2 and set(commits[0]) != set(commits[1])
        serialized = json.dumps(commits[0], default=lambda value: value.decode())
        assert "SECRET" not in serialized and "unsafe" not in serialized
        assert "github_run_attempt" in serialized and "github_run_id" not in serialized
