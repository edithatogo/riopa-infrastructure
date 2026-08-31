from __future__ import annotations

import copy
import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest
from huggingface_hub.errors import HfHubHTTPError

from riopa_provenance.hashing import sha256_bytes

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = runpy.run_path(str(ROOT / "scripts/preserve_tasman_cycle_ledger.py"))


class Hub:
    def __init__(self) -> None:
        self.sha = "a" * 40
        self.snapshots: dict[str, dict[str, bytes]] = {self.sha: {}}
        self.commits = 0
        self.private = False
        self.conflicts = 0
        self.corrupt_download = False
        self.interleave = None

    def repo_info(self, repo: str, **kwargs: object) -> SimpleNamespace:
        assert repo == SCRIPT["PUBLIC"] and kwargs["token"] is False
        return SimpleNamespace(sha=self.sha, private=self.private)

    def get_paths_info(self, repo: str, names: list[str], **kwargs: object) -> list:
        assert repo == SCRIPT["PUBLIC"] and kwargs["token"] is False
        files = self.snapshots[kwargs["revision"]]
        if names == [SCRIPT["PREFIX"]] and any(n.startswith(names[0] + "/") for n in files):
            return [SimpleNamespace(path=names[0])]
        return [SimpleNamespace(path=n, size=len(files[n])) for n in names if n in files]

    def download(self, repo: str, name: str, **kwargs: object) -> str:
        assert repo == SCRIPT["PUBLIC"] and kwargs["token"] is False
        assert kwargs["force_download"] is True
        body = self.snapshots[kwargs["revision"]][name]
        target = Path(kwargs["local_dir"]) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"x" * len(body) if self.corrupt_download else body)
        return str(target)

    def create_commit(self, **kwargs: object) -> SimpleNamespace:
        assert kwargs["repo_id"] == SCRIPT["PUBLIC"]
        assert kwargs["parent_commit"] == self.sha
        if self.conflicts:
            self.conflicts -= 1
            if self.interleave:
                self.interleave(self)
            raise HfHubHTTPError(
                "conflict SECRET",
                response=httpx.Response(
                    409,
                    request=httpx.Request(
                        "POST", "https://huggingface.co/api/datasets/test/commit/main"
                    ),
                ),
            )
        files = dict(self.snapshots[self.sha])
        for operation in kwargs["operations"]:
            assert isinstance(operation.path_or_fileobj, bytes)
            if operation.path_in_repo != SCRIPT["HEAD"]:
                assert operation.path_in_repo not in files
            files[operation.path_in_repo] = operation.path_or_fileobj
        self.commits += 1
        self.sha = f"{self.commits:040x}"
        self.snapshots[self.sha] = files
        return SimpleNamespace(oid=self.sha)


@pytest.fixture
def context(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Hub, Path]:
    documents = SCRIPT["templates"]()
    work = tmp_path / "work"
    (work / "public").mkdir(parents=True)
    for name, value in documents.items():
        (work / "public" / SCRIPT["FILES"][name]).write_bytes(SCRIPT["encode"](value))
    p = documents["provenance"]["publication"]
    for key, value in {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_REPOSITORY": "edithatogo/riopa-infrastructure",
        "GITHUB_RUN_ID": p["run_id"],
        "GITHUB_RUN_ATTEMPT": p["attempt"],
        "GITHUB_SHA": p["code_sha"],
        "HF_TOKEN": "SECRET",
    }.items():
        monkeypatch.setenv(key, value)
    return Hub(), work


def invoke(context: tuple[Hub, Path]) -> dict:
    hub, work = context
    with patch.dict(SCRIPT["preserve"].__globals__, {"hf_hub_download": hub.download}):
        return SCRIPT["preserve"](hub, work)


def test_atomic_public_metadata_and_idempotent_replay(context: tuple) -> None:
    hub, _ = context
    first = invoke(context)
    assert first["status"] == "verified" and hub.commits == 1
    assert not first["three_cycle_gate_qualified"]
    assert not first["historical_baseline_imported"]
    assert len(hub.snapshots[hub.sha]) == 6
    assert invoke(context) == first
    assert hub.commits == 1


def test_commit_success_readback_failure_then_retry(context: tuple) -> None:
    hub, _ = context
    hub.corrupt_download = True
    with pytest.raises(ValueError):
        invoke(context)
    assert hub.commits == 1
    hub.corrupt_download = False
    assert invoke(context)["status"] == "verified"
    assert hub.commits == 1


def test_conflict_reloads_and_preserves_intervening_attempt(context: tuple) -> None:
    hub, work = context
    documents = SCRIPT["templates"]()
    documents["provenance"]["publication"]["run_id"] = "12345"
    bodies = {k: SCRIPT["encode"](v) for k, v in documents.items()}
    hashes = {k: sha256_bytes(v) for k, v in bodies.items()}
    ledger = SCRIPT["CORE"]["append_observation"](None, bodies, hashes)
    body = SCRIPT["encode"](ledger)
    digest = sha256_bytes(body)
    path = f"{SCRIPT['PREFIX']}/ledgers/{digest}.json"

    def competitor(hub: Hub) -> None:
        hub.sha = "b" * 40
        hub.snapshots[hub.sha] = {
            **{f"{SCRIPT['PREFIX']}/receipts/{hashes[k]}.json": v for k, v in bodies.items()},
            path: body,
            SCRIPT["HEAD"]: SCRIPT["encode"](
                {
                    "schema_version": "1.0.0",
                    "ledger_path": path,
                    "ledger_sha256": digest,
                    "ledger_bytes": len(body),
                }
            ),
        }

    hub.conflicts = 1
    hub.interleave = competitor
    result = invoke((hub, work))
    saved = json.loads(hub.snapshots[hub.sha][result["ledger_path"]])
    assert len(saved["events"]) == 2
    assert saved["unique_source_run_count"] == 1
    assert saved["events"][0]["publication"]["run_id"] == "12345"


@pytest.mark.parametrize("fault", ["visibility", "raw", "symlink", "environment", "digest"])
def test_no_public_write_on_invalid_contract(context: tuple, monkeypatch, fault: str) -> None:
    hub, work = context
    path = work / "public/tasman-publication.json"
    if fault == "visibility":
        hub.private = True
    elif fault == "environment":
        monkeypatch.setenv("GITHUB_SHA", "0" * 40)
    elif fault == "symlink":
        other = work / "source"
        path.rename(other)
        path.symlink_to(other)
    else:
        value = json.loads(path.read_bytes())
        value["rows" if fault == "raw" else "packet_manifest_sha256"] = (
            [{"secret": "payload"}] if fault == "raw" else "0" * 64
        )
        path.write_bytes(SCRIPT["encode"](value))
    with pytest.raises(ValueError):
        invoke(context)
    assert hub.commits == 0


def test_conflict_budget_and_corrupt_history_fail_closed(context: tuple) -> None:
    hub, _ = context
    hub.conflicts = 4
    with pytest.raises(HfHubHTTPError):
        invoke(context)
    assert hub.conflicts == 0 and hub.commits == 0
    invoke(context)
    original = hub.commits
    receipt = next(n for n in hub.snapshots[hub.sha] if "/receipts/" in n)
    hub.snapshots[hub.sha][receipt] = b"corrupt"
    with pytest.raises(ValueError):
        invoke(context)
    assert hub.commits == original


def test_failure_artifact_redacts_exception(context: tuple, capsys) -> None:
    _, work = context
    with (
        patch.dict(
            SCRIPT["main"].__globals__,
            {
                "preserve": lambda *_: (_ for _ in ()).throw(ValueError("SECRET private/path")),
            },
        ),
        patch("sys.argv", ["preserve", "--work", str(work)]),
    ):
        assert SCRIPT["main"]() == 1
    assert "SECRET" not in capsys.readouterr().out
    assert json.loads((work / "public/tasman-cycle-preservation-failure.json").read_bytes()) == {
        "status": "failed",
        "error_class": "ValueError",
    }


def test_change_hashes_metadata_profile() -> None:
    value = {
        "1": {
            "before": None,
            "after": {
                "attributes_sha256": "a" * 64,
                "geometry_sha256": "b" * 64,
            },
        }
    }
    SCRIPT["metadata_shape"](value, {}, "change_hashes")
    changed = copy.deepcopy(value)
    changed["1"]["after"]["rows"] = []
    with pytest.raises(ValueError):
        SCRIPT["metadata_shape"](changed, {}, "change_hashes")


def test_missing_head_cannot_reinitialise_history(context: tuple) -> None:
    hub, _ = context
    invoke(context)
    del hub.snapshots[hub.sha][SCRIPT["HEAD"]]
    with pytest.raises(ValueError):
        invoke(context)
    assert hub.commits == 1


def test_rejected_root_does_not_write_failure(tmp_path: Path) -> None:
    with (
        patch.dict(SCRIPT["main"].__globals__, {"ROOT": tmp_path}),
        patch("sys.argv", ["preserve", "--work", str(tmp_path)]),
    ):
        assert SCRIPT["main"]() == 1
    assert not (tmp_path / "public").exists()


def test_failed_retry_retains_but_relabels_prior_success(context: tuple) -> None:
    _, work = context
    invoke(context)
    with (
        patch.dict(
            SCRIPT["main"].__globals__,
            {
                "preserve": lambda *_: (_ for _ in ()).throw(ValueError("failure")),
            },
        ),
        patch("sys.argv", ["preserve", "--work", str(work)]),
    ):
        assert SCRIPT["main"]() == 1
    assert not (work / "public/tasman-cycle-preservation.json").exists()
    assert len(list((work / "public").glob("tasman-cycle-prior-*.json"))) == 1


def test_oversized_remote_metadata_rejected_before_download(context: tuple) -> None:
    hub, work = context
    hub.snapshots[hub.sha][SCRIPT["HEAD"]] = b"x" * (SCRIPT["LIMIT"] + 1)
    with pytest.raises(ValueError):
        invoke((hub, work))
    assert hub.commits == 0
