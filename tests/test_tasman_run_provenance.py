from __future__ import annotations

import copy
import json
import runpy
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from riopa_provenance.hashing import sha256_bytes, sha256_json

SCRIPT = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "scripts/record_tasman_run_provenance.py")
)


@pytest.fixture
def fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    public = tmp_path / "public"
    public.mkdir()
    source = {
        "status": "public-packet-verified-and-rebuilt",
        "state": "verified",
        "source_run": "123",
        "anonymous_full_packet_verified": True,
        "private_prefix": "campaigns/123/tasman/1",
        "packet_manifest_sha256": "a" * 64,
        "public_revision": "b" * 40,
    }
    derived = {
        "status": "derivatives-published-and-verified",
        "state": "verified",
        "identity": {"source_manifest_sha256": "a" * 64, "source_revision": "b" * 40},
        "public_revision": "c" * 40,
        "logical_sha256": "d" * 64,
    }
    source["reproduction"] = {"feature_count": 1, "geoparquet_sha256": "a" * 64}
    derived["identity"].update(source["reproduction"])
    derived["logical_sha256"] = sha256_json(derived["identity"])
    source["public_dataset_repository"] = "edithatogo/riopa-public-data-archive"
    derived["public_repository"] = "edithatogo/riopa-public-data-archive"
    for receipt in (source, derived):
        receipt.update(licence="CC-BY-4.0", attribution="Tasman District Council (TDC)")
    (tmp_path / "store").mkdir()
    (tmp_path / "store/hosted-run.json").write_text(
        json.dumps(
            {
                "source": "tasman",
                "run_id": "123",
                "attempt": "1",
                "code_revision": "e" * 40,
                "acquisition_complete": True,
            }
        )
    )
    base = {
        "id": 123,
        "run_attempt": 1,
        "repository": {"full_name": SCRIPT["REPOSITORY"]},
        "head_repository": {"full_name": SCRIPT["REPOSITORY"]},
        "head_branch": "main",
        "path": ".github/workflows/council-archive.yml",
        "head_sha": "e" * 40,
        "event": "schedule",
        "status": "completed",
        "conclusion": "success",
        "created_at": "2026-08-31T01:00:01Z",
        "run_started_at": "2026-08-31T01:00:00Z",
        "updated_at": "2026-08-31T01:05:00Z",
    }
    trigger = {**base, "run_attempt": 2}
    publication = {
        **base,
        "id": 456,
        "path": ".github/workflows/tasman-publication.yml",
        "event": "workflow_run",
        "status": "in_progress",
        "conclusion": None,
        "head_sha": "f" * 40,
    }
    event = {
        "repository": {"full_name": SCRIPT["REPOSITORY"]},
        "action": "completed",
        "workflow_run": copy.deepcopy(trigger),
    }
    event_path = tmp_path / "event.json"
    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_REPOSITORY": SCRIPT["REPOSITORY"],
        "GITHUB_RUN_ID": "456",
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_SHA": "f" * 40,
        "GITHUB_EVENT_NAME": "workflow_run",
        "GITHUB_EVENT_PATH": str(event_path),
    }
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    return {
        "source": source,
        "derived": derived,
        "capture": base,
        "trigger": trigger,
        "publication": publication,
        "event": event,
        "work": tmp_path,
        "event_path": event_path,
    }


def run(f: dict) -> dict:
    for name in ("source", "derived"):
        path = "tasman-publication.json" if name == "source" else "tasman-derivatives.json"
        (f["work"] / "public" / path).write_text(json.dumps(f[name]))
    f["event_path"].write_text(json.dumps(f["event"]))

    def api(run_id: str, attempt: str | None = None) -> dict:
        if run_id == "456":
            return f["publication"]
        return f["capture"] if attempt == "1" else f["trigger"]

    with patch.dict(SCRIPT["record"].__globals__, {"api": api}):
        return SCRIPT["record"](f["work"], "123")


def test_automatic_schedule_and_replay_dedup(fixture: dict) -> None:
    result = run(fixture)
    assert result["cycle_key"] == "123" and result["capture_checkpoint_reused"]
    assert result["source_capture"]["attempt"] == "1" and result["source_trigger"]["attempt"] == "2"
    assert result["automatic_followup"] and result["scheduled_source_trigger_observed"]
    assert (
        not result["release_cycle_qualified"] and not result["publication_job_completion_claimed"]
    )
    assert result["source_receipt_sha256"] == sha256_bytes(
        (fixture["work"] / "public/tasman-publication.json").read_bytes()
    )


def test_manual_followup_is_not_automatic(fixture: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    fixture["publication"]["event"] = "workflow_dispatch"
    fixture["event"] = {
        "repository": {"full_name": SCRIPT["REPOSITORY"]},
        "inputs": {"source_run": "123"},
        "ref": "refs/heads/main",
    }
    result = run(fixture)
    assert not result["automatic_followup"] and result["scheduled_source_trigger_observed"]


@pytest.mark.parametrize(
    "target,key,value",
    [
        ("capture", "status", "in_progress"),
        ("trigger", "conclusion", "failure"),
        ("trigger", "head_sha", "a" * 40),
        ("trigger", "run_attempt", 3),
        ("capture", "event", "pull_request"),
        ("publication", "head_sha", "a" * 40),
        ("publication", "head_branch", "other"),
        ("publication", "path", ".github/workflows/other.yml"),
        ("publication", "repository", {"full_name": "wrong/repo"}),
        ("publication", "id", 99),
        ("publication", "updated_at", "invalid"),
        ("source", "state", "pending"),
        ("source", "source_run", "789"),
        ("source", "private_prefix", "campaigns/789/tasman/1"),
        ("derived", "logical_sha256", "bad"),
        ("derived", "public_revision", "bad"),
        ("derived", "identity", {"source_manifest_sha256": "wrong"}),
        ("event", "action", "requested"),
        ("event", "repository", {"full_name": "wrong/repo"}),
    ],
)
def test_tampering_rejected(fixture: dict, target: str, key: str, value: object) -> None:
    fixture[target][key] = value
    with pytest.raises(ValueError):
        run(fixture)
    assert not (fixture["work"] / "public/tasman-run-provenance.json").exists()


@pytest.mark.parametrize("value", [True, None, "../x", "0", "1" * 30])
def test_numeric_identity_bounds(value: object) -> None:
    with pytest.raises(ValueError):
        SCRIPT["number"](value)


def test_api_is_bounded_array_subprocess() -> None:
    def execute(command: list, **kwargs: object) -> None:
        assert command == [
            "/usr/bin/gh",
            "api",
            "--hostname",
            "github.com",
            "repos/edithatogo/riopa-infrastructure/actions/runs/123/attempts/2",
        ]
        assert kwargs["timeout"] == 30 and kwargs["stderr"] == subprocess.DEVNULL
        kwargs["stdout"].write(b'{"id":123}')

    with (
        patch("shutil.which", return_value="/usr/bin/gh"),
        patch("subprocess.run", side_effect=execute),
    ):
        assert SCRIPT["api"]("123", "2")["id"] == 123


@pytest.mark.parametrize("executable", [None, "relative/gh"])
def test_api_requires_absolute_executable(executable: str | None) -> None:
    with patch("shutil.which", return_value=executable), patch("subprocess.run") as execute:
        with pytest.raises(ValueError):
            SCRIPT["api"]("123", "2")
        execute.assert_not_called()


def test_cli_failure_no_secret_messages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.argv", ["provenance", "--work", str(tmp_path), "--source-run", "123"])

    def fail(*args: object) -> None:
        raise ValueError("SECRET token file/path")

    with patch.dict(SCRIPT["main"].__globals__, {"record": fail}):
        assert SCRIPT["main"]() == 1
    text = (
        capsys.readouterr().out
        + (tmp_path / "public/tasman-run-provenance-failure.json").read_text()
    )
    assert "SECRET" not in text and "file/path" not in text


def test_failed_original_matrix_with_verified_tasman_checkpoint(fixture: dict) -> None:
    fixture["capture"]["conclusion"] = "failure"
    fixture["event"]["workflow_run"].pop("repository")
    result = run(fixture)
    assert result["source_capture"]["conclusion"] == "failure"
    assert result["source_trigger"]["conclusion"] == "success"
    assert result["capture_checkpoint_reused"]


@pytest.mark.parametrize(
    "target,key,value",
    [
        ("source", "public_dataset_repository", "wrong/repo"),
        ("derived", "public_repository", "wrong/repo"),
        ("derived", "licence", "wrong"),
        ("publication", "updated_at", "2026-99-31T00:00:00Z"),
        ("publication", "updated_at", "2026-08-30T00:00:00Z"),
        ("publication", "status", "completed"),
    ],
)
def test_additional_identity_and_time_guards(
    fixture: dict, target: str, key: str, value: object
) -> None:
    fixture[target][key] = value
    with pytest.raises(ValueError):
        run(fixture)


def test_archived_run_code_binding(fixture: dict) -> None:
    path = fixture["work"] / "store/hosted-run.json"
    value = json.loads(path.read_bytes())
    value["code_revision"] = "0" * 40
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="archived Tasman"):
        run(fixture)
