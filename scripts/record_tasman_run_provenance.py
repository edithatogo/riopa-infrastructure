#!/usr/bin/env python3
"""Bind Tasman publication receipts to observed, attempt-specific GitHub runs."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess  # nosec B404
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_bytes, sha256_json

REPOSITORY = "edithatogo/riopa-infrastructure"
LIMIT = 2_000_000


def number(value: object) -> str:
    if isinstance(value, bool) or not re.fullmatch(r"[1-9][0-9]{0,19}", str(value)):
        raise ValueError("invalid numeric run identity")
    return str(value)


def digest(value: object, size: int) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{" + str(size) + r"}", value):
        raise ValueError("invalid digest identity")
    return value


def api(run: str, attempt: str | None = None) -> dict[str, Any]:
    endpoint = f"repos/{REPOSITORY}/actions/runs/{number(run)}"
    if attempt is not None:
        endpoint += f"/attempts/{number(attempt)}"
    executable = shutil.which("gh")
    if executable is None or not Path(executable).is_absolute():
        raise ValueError("absolute GitHub CLI executable required")
    with tempfile.TemporaryFile() as output:
        # Fixed gh API argv, absolute executable, no shell; only numeric identities vary.
        subprocess.run(  # nosec B603
            [executable, "api", "--hostname", "github.com", endpoint],
            stdout=output,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=True,
        )
        if output.tell() > LIMIT:
            raise ValueError("GitHub response exceeds parse budget")
        output.seek(0)
        payload = json.load(output)
    if not isinstance(payload, dict):
        raise ValueError("GitHub response must be an object")
    return payload


def read(path: Path, root: Path) -> tuple[dict[str, Any], str]:
    if not path.resolve().is_relative_to(root.resolve()) or any(
        p.is_symlink() for p in (path, *path.parents)
    ):
        raise ValueError("unsafe evidence path")
    if not path.is_file() or not 0 < path.stat().st_size <= LIMIT:
        raise ValueError("missing or oversized evidence")
    body = path.read_bytes()
    value = json.loads(body)
    if not isinstance(value, dict):
        raise ValueError("evidence must be an object")
    return value, sha256_bytes(body)


def run_record(
    value: dict[str, Any],
    run: str,
    attempt: str,
    workflow: str,
    *,
    source: bool,
    require_success: bool = True,
) -> dict[str, Any]:
    if (number(value.get("id")), number(value.get("run_attempt"))) != (run, attempt):
        raise ValueError("run/attempt API binding mismatch")
    if (
        value.get("repository", {}).get("full_name") != REPOSITORY
        or value.get("head_repository", {}).get("full_name") != REPOSITORY
    ):
        raise ValueError("repository identity mismatch")
    if value.get("path") != f".github/workflows/{workflow}" or value.get("head_branch") != "main":
        raise ValueError("workflow/main identity mismatch")
    if source and (
        value.get("status") != "completed"
        or (require_success and value.get("conclusion") != "success")
        or value.get("conclusion") not in ("success", "failure", "cancelled", "timed_out")
        or value.get("event") not in ("schedule", "workflow_dispatch")
    ):
        raise ValueError("source attempt is not successfully completed")
    if not source and (
        value.get("status") not in ("in_progress", "completed")
        or (value.get("status") == "in_progress" and value.get("conclusion") is not None)
        or (value.get("status") == "completed" and value.get("conclusion") != "success")
        or value.get("event") not in ("workflow_dispatch", "workflow_run")
    ):
        raise ValueError("publication run state/event mismatch")
    result = {
        "run_id": run,
        "attempt": attempt,
        "code_sha": digest(value.get("head_sha"), 40),
        "event": value["event"],
        "status": value["status"],
        "conclusion": value.get("conclusion"),
        "workflow_path": value["path"],
    }
    for key in ("created_at", "run_started_at", "updated_at"):
        timestamp = value.get(key)
        if not isinstance(timestamp, str) or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", timestamp
        ):
            raise ValueError("invalid run timestamp")
        result[key] = timestamp
        datetime.fromisoformat(timestamp)
    if datetime.fromisoformat(result["run_started_at"]) > datetime.fromisoformat(
        result["updated_at"]
    ):
        raise ValueError("run update predates start")
    return result


def record(work: Path, source_run: str) -> dict[str, Any]:
    source_run = number(source_run)
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
        or os.environ.get("GITHUB_REPOSITORY") != REPOSITORY
    ):
        raise ValueError("main Actions repository context required")
    publication_run = number(os.environ.get("GITHUB_RUN_ID"))
    publication_attempt = number(os.environ.get("GITHUB_RUN_ATTEMPT"))
    source, source_hash = read(work / "public/tasman-publication.json", work)
    derived, derived_hash = read(work / "public/tasman-derivatives.json", work)
    if (
        source.get("status") != "public-packet-verified-and-rebuilt"
        or source.get("state") != "verified"
        or source.get("source_run") != source_run
        or source.get("anonymous_full_packet_verified") is not True
    ):
        raise ValueError("source publication receipt is not verified")
    identity = derived.get("identity", {})
    public_repo = "edithatogo/riopa-public-data-archive"
    if (
        source.get("public_dataset_repository") != public_repo
        or derived.get("public_repository") != public_repo
    ):
        raise ValueError("public repository binding mismatch")
    if any(
        receipt.get("licence") != "CC-BY-4.0"
        or receipt.get("attribution") != "Tasman District Council (TDC)"
        for receipt in (source, derived)
    ):
        raise ValueError("rights receipt binding mismatch")
    if (
        derived.get("logical_sha256") != sha256_json(identity)
        or identity.get("feature_count") != source.get("reproduction", {}).get("feature_count")
        or identity.get("geoparquet_sha256")
        != source.get("reproduction", {}).get("geoparquet_sha256")
    ):
        raise ValueError("derivative semantic receipt mismatch")
    if (
        derived.get("status") != "derivatives-published-and-verified"
        or derived.get("state") != "verified"
        or identity.get("source_manifest_sha256") != source.get("packet_manifest_sha256")
        or identity.get("source_revision") != source.get("public_revision")
    ):
        raise ValueError("derivative/source receipt bindings differ")
    private = re.fullmatch(
        r"campaigns/([1-9][0-9]*)/tasman/([1-9][0-9]*)", source.get("private_prefix", "")
    )
    if private is None or private.group(1) != source_run:
        raise ValueError("private capture attempt binding mismatch")
    capture_attempt = number(private.group(2))
    event_path = Path(os.environ["GITHUB_EVENT_PATH"])
    event, _ = read(event_path, event_path.parent)
    if event.get("repository", {}).get("full_name") != REPOSITORY:
        raise ValueError("event repository mismatch")
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    if event_name == "workflow_run":
        upstream = event.get("workflow_run", {})
        if event.get("action") != "completed" or number(upstream.get("id")) != source_run:
            raise ValueError("upstream event identity mismatch")
        trigger_attempt = number(upstream.get("run_attempt"))
    elif event_name == "workflow_dispatch":
        if event.get("inputs", {}).get("source_run") != source_run or event.get("ref") not in (
            "main",
            "refs/heads/main",
        ):
            raise ValueError("dispatch inputs/ref mismatch")
        trigger_attempt = number(api(source_run).get("run_attempt"))
    else:
        raise ValueError("unsupported publication event")
    trigger_raw = api(source_run, trigger_attempt)
    trigger = run_record(
        trigger_raw, source_run, trigger_attempt, "council-archive.yml", source=True
    )
    if event_name == "workflow_run":
        event_upstream = run_record(
            {**upstream, "repository": event["repository"]},
            source_run,
            trigger_attempt,
            "council-archive.yml",
            source=True,
        )
        if any(
            event_upstream[key] != trigger[key] for key in ("code_sha", "event", "workflow_path")
        ):
            raise ValueError("upstream event differs from pinned API attempt")
    captured = run_record(
        api(source_run, capture_attempt),
        source_run,
        capture_attempt,
        "council-archive.yml",
        source=True,
        require_success=False,
    )
    hosted, hosted_hash = read(work / "store/hosted-run.json", work)
    if (
        hosted.get("source") != "tasman"
        or hosted.get("run_id") != source_run
        or hosted.get("attempt") != capture_attempt
        or hosted.get("acquisition_complete") is not True
        or hosted.get("code_revision") != captured["code_sha"]
    ):
        raise ValueError("archived Tasman capture does not match source attempt")
    publication = run_record(
        api(publication_run, publication_attempt),
        publication_run,
        publication_attempt,
        "tasman-publication.yml",
        source=False,
    )
    if (
        publication["code_sha"] != digest(os.environ.get("GITHUB_SHA"), 40)
        or publication["event"] != event_name
    ):
        raise ValueError("publication environment differs from pinned API attempt")
    if int(capture_attempt) > int(trigger_attempt):
        raise ValueError("capture attempt postdates trigger attempt")
    result = {
        "schema_version": "1.0.0",
        "record_type": "tasman_run_provenance",
        "repository": REPOSITORY,
        "source_receipt_sha256": source_hash,
        "derived_receipt_sha256": derived_hash,
        "source_public_revision": digest(source.get("public_revision"), 40),
        "source_packet_manifest_sha256": digest(source.get("packet_manifest_sha256"), 64),
        "derived_public_revision": digest(derived.get("public_revision"), 40),
        "derived_logical_sha256": digest(derived.get("logical_sha256"), 64),
        "source_capture": captured,
        "source_capture_status_basis": "verified-publication-receipt-and-archived-hosted-run",
        "archived_hosted_run_sha256": hosted_hash,
        "source_trigger": trigger,
        "publication": publication,
        "cycle_key": source_run,
        "capture_checkpoint_reused": capture_attempt != trigger_attempt,
        "scheduled_source_trigger_observed": trigger["event"] == "schedule",
        "automatic_followup": event_name == "workflow_run",
        "release_cycle_qualified": False,
        "change_recovery": "not-evaluated",
        "publication_job_completion_claimed": False,
    }
    output = work / "public/tasman-run-provenance.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--source-run", required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    root = Path(__file__).resolve().parents[1]
    if work.is_relative_to(root) and not work.is_relative_to(root / ".riopa-local"):
        parser.error("ignored or external work directory required")
    try:
        result = record(work, args.source_run)
    except Exception as error:
        failure = {"status": "failed", "error_class": type(error).__name__[:128]}
        try:
            directory = work / "public"
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "tasman-run-provenance-failure.json").write_text(
                json.dumps(failure) + "\n"
            )
        except Exception as secondary:
            failure["record_error_class"] = type(secondary).__name__[:128]
        print(json.dumps(failure))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
