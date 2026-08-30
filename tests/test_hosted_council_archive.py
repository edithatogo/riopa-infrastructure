from __future__ import annotations

import json
import runpy
import subprocess
import tarfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest

from riopa_provenance.capture import CapturePolicy, CaptureStore, HttpCaptureClient
from riopa_provenance.hashing import sha256_file, sha256_json

SCRIPT = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/hosted_council_archive.py")
)


def fixture_store(tmp_path: Path) -> Path:
    store = CaptureStore(tmp_path / "store")
    with httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, content=b"data"))
    ) as http:
        HttpCaptureClient(
            client=http, store=store, policy=CapturePolicy(allowed_hosts=frozenset({"example.org"}))
        ).capture("GET", "https://example.org/", source_id="source", endpoint_id="endpoint")
    return store.root


def test_packet_round_trip_and_deterministic_bytes(tmp_path: Path) -> None:
    store = fixture_store(tmp_path)
    run = {"source": "tasman", "acquisition_complete": False}
    first = SCRIPT["pack"](store, tmp_path / "one", run)
    second = SCRIPT["pack"](store, tmp_path / "two", run)
    assert first == second
    assert first["payload_visibility"] == "private"
    assert first["acquisition_complete"] is False
    SCRIPT["verify_packet"](tmp_path / "one/raw.tar", first)


@pytest.mark.parametrize("tamper", ["symlink", "bytes", "size", "digest"])
def test_corrupt_store_rejected(tmp_path: Path, tamper: str) -> None:
    store = fixture_store(tmp_path)
    capture = next((store / "captures").glob("*.json"))
    metadata = json.loads(capture.read_text())
    if tamper == "symlink":
        (store / "link").symlink_to(capture)
    elif tamper == "bytes":
        next((store / "objects/sha256").glob("*/*")).write_bytes(b"corrupt")
    else:
        metadata["object"]["size_bytes" if tamper == "size" else "sha256"] = (
            999 if tamper == "size" else "../bad"
        )
        capture.write_text(json.dumps(metadata))
    with pytest.raises((ValueError, RuntimeError)):
        SCRIPT["inventory"](store)


@pytest.mark.parametrize("name", ["../escape", "/absolute", "a/../b", "a\\b", "a//b"])
def test_unsafe_archive_paths(name: str) -> None:
    assert not SCRIPT["safe_path"](name)


@pytest.mark.parametrize("tamper", ["archive", "manifest", "member", "missing", "duplicate"])
def test_tampered_packet_rejected(tmp_path: Path, tamper: str) -> None:
    store = fixture_store(tmp_path)
    manifest = SCRIPT["pack"](store, tmp_path / "packet", {})
    archive = tmp_path / "packet/raw.tar"
    if tamper == "archive":
        archive.write_bytes(b"bad")
    elif tamper == "manifest":
        manifest["public_scope"] = "all"
    else:
        if tamper == "member":
            manifest["files"][0]["sha256"] = "0" * 64
        elif tamper == "missing":
            manifest["files"].pop()
        else:
            manifest["files"].append(manifest["files"][0])
        manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
    with pytest.raises(ValueError):
        SCRIPT["verify_packet"](archive, manifest)


def test_tar_symlink_rejected_even_with_rehashed_archive(tmp_path: Path) -> None:
    store = fixture_store(tmp_path)
    manifest = SCRIPT["pack"](store, tmp_path / "packet", {})
    archive = tmp_path / "packet/raw.tar"
    with tarfile.open(archive, "w") as tar:
        member = tarfile.TarInfo("escape")
        member.type = tarfile.SYMTYPE
        member.linkname = "/tmp/elsewhere"
        tar.addfile(member)
    manifest.update(archive_sha256=sha256_file(archive), archive_bytes=archive.stat().st_size)
    manifest["manifest_sha256"] = sha256_json(manifest, omit_keys={"manifest_sha256"})
    with pytest.raises(ValueError):
        SCRIPT["verify_packet"](archive, manifest)


@pytest.mark.parametrize("failure", [False, True])
def test_capture_failure_still_packages_attempt_without_credentials(
    tmp_path: Path, failure: bool
) -> None:
    outcome = (
        subprocess.TimeoutExpired("capture", 600) if failure else subprocess.CompletedProcess([], 1)
    )
    with (
        patch(
            "subprocess.run", side_effect=outcome if failure else None, return_value=outcome
        ) as execute,
        patch.dict("os.environ", {"HF_TOKEN": "not-a-real-secret"}),
    ):
        SCRIPT["capture"]("qldc", tmp_path, "123", "1", "a" * 40)
    assert "HF_TOKEN" not in execute.call_args.kwargs["env"]
    manifest = json.loads((tmp_path / "packet/manifest.json").read_text())
    assert manifest["acquisition_complete"] is False
    assert manifest["capture_exit_code"] == (124 if failure else 1)
    assert manifest["scope"] == "route-qualification-only"


def test_workflow_parallelism_and_credential_isolation() -> None:
    policy = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "scripts/check_workflow_policy.py")
    )
    import yaml

    root = Path(__file__).resolve().parents[1]
    workflow = yaml.load(
        (root / ".github/workflows/council-archive.yml").read_text(),
        Loader=policy["Yaml12SafeLoader"],
    )
    job = workflow["jobs"]["capture"]
    assert job["strategy"] == {
        "fail-fast": False,
        "max-parallel": 3,
        "matrix": {"source": ["tasman", "npdc", "qldc"]},
    }
    capture_step = next(s for s in job["steps"] if s["name"].startswith("Capture source"))
    assert "HF_TOKEN" not in capture_step.get("env", {})
    assert "HF_TOKEN" not in job["env"]
    assert job["env"]["WORK"] == ".riopa-local/hosted-council"
    assert all("runner." not in str(value) for value in job["env"].values())
    assert workflow["permissions"] == {"contents": "read"}
    assert job["concurrency"] == {
        "group": "council-source-${{ matrix.source }}",
        "cancel-in-progress": False,
    }
    assert "github.run_id" in workflow["concurrency"]["group"]
    assert job["steps"][-1]["with"]["path"].endswith("/public/")
    assert job["steps"][-1]["with"]["path"] == job["env"]["WORK"] + "/public/"


@pytest.mark.parametrize("failure", [None, "raw-public", "anonymous", "oversize", "manifest"])
def test_publication_boundaries_and_checkpoint_order(tmp_path: Path, failure: str | None) -> None:
    import huggingface_hub

    store = fixture_store(tmp_path)
    manifest = SCRIPT["pack"](
        store,
        tmp_path / "packet",
        {
            "source": "tasman",
            "run_id": "123",
            "attempt": "1",
            "code_revision": "a" * 40,
            "acquisition_complete": True,
            "scope": "bounded-source-capture",
        },
    )
    remote: dict[tuple[str, str], bytes] = {}
    commits: list[tuple[str, list[str]]] = []
    downloads: list[tuple[str, str, object]] = []

    def commit(_api: object, repo: str, files: dict[str, Path | bytes]) -> str:
        commits.append((repo, list(files)))
        for name, value in files.items():
            remote[repo, name] = value.read_bytes() if isinstance(value, Path) else value
        return "b" * 40 if repo == SCRIPT["PRIVATE_REPO"] else "c" * 40

    def download(repo: str, name: str, **kwargs: object) -> str:
        downloads.append((repo, name, kwargs.get("token")))
        path = Path(str(kwargs["local_dir"])) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = remote[repo, name]
        if failure == "anonymous" and repo == SCRIPT["PUBLIC_REPO"]:
            payload += b"tampered"
        if failure == "manifest" and name.endswith("manifest.json"):
            payload = payload.replace(b'"private"', b'"changed"')
        path.write_bytes(payload)
        return str(path)

    def paths(repo: str, names: list[str], **kwargs: object) -> list[SimpleNamespace]:
        assert kwargs["revision"] == ("b" * 40 if repo == SCRIPT["PRIVATE_REPO"] else "c" * 40)
        return [
            SimpleNamespace(
                path=name,
                size=(
                    SCRIPT["MAX_TAR_BYTES"] + 1
                    if failure == "oversize" and name.endswith("raw.tar")
                    else len(remote[repo, name])
                ),
            )
            for name in names
            if (repo, name) in remote
        ]

    api = SimpleNamespace(
        token="test-credential",
        get_paths_info=paths,
        repo_info=lambda repo, **_: SimpleNamespace(
            private=repo == SCRIPT["PRIVATE_REPO"] and failure != "raw-public"
        ),
    )
    with (
        patch.dict(SCRIPT["publish"].__globals__, {"commit_files": commit}),
        patch.object(huggingface_hub, "hf_hub_download", side_effect=download),
    ):
        if failure:
            with pytest.raises(ValueError):
                SCRIPT["publish"](api, tmp_path, manifest)
            assert not any(
                name.endswith("checkpoint.json") for _, names in commits for name in names
            )
            if failure in ("oversize", "manifest"):
                assert not any(name.endswith("raw.tar") for _, name, _ in downloads)
        else:
            SCRIPT["publish"](api, tmp_path, manifest)
            assert commits[-1][1] == ["campaigns/123/tasman/checkpoint.json"]
            report = json.loads((tmp_path / "public/preservation.json").read_text())
            assert report["anonymous_evidence_verified"] is True
            assert report["public_payload"] is False
            public_names = [
                name for repo, names in commits if repo == SCRIPT["PUBLIC_REPO"] for name in names
            ]
            assert all(
                name.endswith(("manifest.json", "preservation.json")) for name in public_names
            )
            assert all(
                token is False for repo, _, token in downloads if repo == SCRIPT["PUBLIC_REPO"]
            )
            checkpoint = json.loads(
                remote[SCRIPT["PRIVATE_REPO"], "campaigns/123/tasman/checkpoint.json"]
            )
            assert checkpoint["public_revision"] == "c" * 40
            before = len(commits)
            assert SCRIPT["resume"](api, "tasman", "123", "a" * 40, tmp_path / "resumed")
            assert len(commits) == before  # Recheck original public revision, do not republish.
            with pytest.raises(ValueError, match="source/run/code"):
                SCRIPT["resume"](api, "tasman", "123", "d" * 40, tmp_path / "other")
            del remote[SCRIPT["PUBLIC_REPO"], "campaigns/123/tasman/1/preservation.json"]
            with pytest.raises(ValueError, match="public checkpoint files missing"):
                SCRIPT["resume"](api, "tasman", "123", "a" * 40, tmp_path / "lost-public")
            assert len(commits) == before
            api.repo_info = lambda *args, **kwargs: SimpleNamespace(private=False)
            with pytest.raises(ValueError, match="raw destination must be private"):
                SCRIPT["resume"](api, "tasman", "123", "a" * 40, tmp_path / "raw-now-public")


def test_commit_conflict_retries_are_bounded(tmp_path: Path) -> None:
    from huggingface_hub.errors import HfHubHTTPError

    calls = 0

    def commit(**kwargs: object) -> SimpleNamespace:
        nonlocal calls
        calls += 1
        if calls < 3:
            raise HfHubHTTPError(
                "conflict",
                response=httpx.Response(
                    409, request=httpx.Request("POST", "https://huggingface.co/")
                ),
            )
        return SimpleNamespace(oid="b" * 40)

    api = SimpleNamespace(
        repo_info=lambda *a, **k: SimpleNamespace(sha="a" * 40), create_commit=commit
    )
    with patch("time.sleep") as sleep:
        assert SCRIPT["commit_files"](api, "owner/repo", {"manifest.json": b"{}"}) == "b" * 40
    assert calls == 3 and sleep.call_count == 2
