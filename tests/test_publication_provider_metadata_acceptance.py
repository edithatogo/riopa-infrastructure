"""Offline checks of the bounded hosted metadata observation acceptance."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from riopa_provenance.hashing import sha256_bytes, sha256_json
from scripts.reconcile_publication_provider_metadata import validate_request

ROOT = Path(__file__).resolve().parents[1]


def evidence() -> dict:
    return json.loads(
        (ROOT / "docs/publication-provider-metadata-acceptance-20260831.json").read_bytes()
    )


def test_request_and_embedded_report_are_exactly_bound() -> None:
    data = evidence()
    raw_request = (ROOT / data["request"]["path"]).read_bytes()
    request = json.loads(raw_request)
    validate_request(request)
    assert sha256_bytes(raw_request) == data["request"]["file_sha256"]
    assert sha256_json(request) == data["request"]["request_sha256"]
    report = data["observation"]["report"]
    raw_report = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    assert sha256_bytes(raw_report) == data["observation"]["file_sha256"]
    assert len(raw_report) == data["observation"]["file_bytes"]
    assert report["report_sha256"] == sha256_json(report, omit_keys={"report_sha256"})
    assert report["request_sha256"] == sha256_json(request)
    assert report["binding"] == {
        key: request[key] for key in ("repository", "revision", "path", "sha256")
    }
    assert request["revision"] == "ebecf6d38084aa459b27ef2bf753505003b08a16"
    assert request["sha256"] == "f0eee330ac23067b92f0eef64fb9c69028f79ea1161fdd846e2b446b8761445d"


def test_hosted_execution_and_metadata_only_bounds() -> None:
    data = evidence()
    run = data["hosted_execution"]
    assert run["run_id"] == "33385363775" and run["attempt"] == 1
    assert run["head_sha"] == "703b7ccdeb612056bde49306502f036ccebfb1ce"
    assert run["event"] == "workflow_dispatch"
    assert run["status"] == "completed" and run["conclusion"] == "success"
    assert run["job_id"] == "99466666100" and run["job_conclusion"] == "success"
    assert datetime.fromisoformat(run["job_started_at"]) < datetime.fromisoformat(
        run["job_completed_at"]
    )
    assert data["artifact"]["name"] == "publication-metadata-33385363775-1"
    assert data["artifact"]["files"] == ["publication-provider-metadata.json"]
    assert data["artifact"]["archive_bytes"] == 786
    assert data["artifact"]["github_archive_sha256"] == (
        "98d4aea4d374a59e2614c8b70b203f51138628746a1ba4af58c531704ca4f992"
    )
    assert data["status"] == "hosted-matching-metadata-observed"
    report = data["observation"]["report"]
    assert report["status"] == "matching-metadata-observed"
    assert report["remote_write_authorized"] is False
    assert report["publication_receipt_created"] is False
    assert report["observed_bytes"] == 1178
    assert report["attempts"] == 1
    assert report["attempt_history"] == [{"ordinal": 1, "status": "matching-metadata-observed"}]
    for key in ("full_asset_verification", "publication_acceptance", "release_qualification"):
        assert data["qualification"][key] is False
