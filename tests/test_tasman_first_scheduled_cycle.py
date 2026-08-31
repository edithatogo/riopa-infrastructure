"""Offline contract checks for observed scheduled-run metadata, not live provider tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from riopa_provenance.hashing import sha256_bytes, sha256_json

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs/tasman-first-scheduled-cycle-20260831.json"


def evidence() -> dict:
    return json.loads(DOCUMENT.read_bytes())


def test_embedded_receipt_byte_hashes_and_cross_bindings() -> None:
    data = evidence()
    preservation = data["preservation"]["receipt"]
    for binding in [*data["receipts"].values(), data["preservation"]]:
        body = (json.dumps(binding["receipt"], indent=2) + "\n").encode()
        assert sha256_bytes(body) == binding["sha256"]
    for name, binding in data["receipts"].items():
        assert preservation["receipt_sha256"][name] == binding["sha256"]
    source = data["receipts"]["source"]["receipt"]
    derived = data["receipts"]["derived"]["receipt"]
    provenance = data["receipts"]["provenance"]["receipt"]
    assert derived["identity"]["source_manifest_sha256"] == source["packet_manifest_sha256"]
    assert derived["identity"]["source_revision"] == source["public_revision"]
    assert sha256_json(derived["identity"]) == derived["logical_sha256"]
    assert provenance["derived_logical_sha256"] == derived["logical_sha256"]
    assert provenance["source_public_revision"] == source["public_revision"]
    assert provenance["derived_public_revision"] == derived["public_revision"]
    assert source["licence"] == derived["licence"] == "CC-BY-4.0"
    assert source["state"] == derived["state"] == "verified"
    assert source["anonymous_full_packet_verified"] is True
    assert source["reproduction"]["feature_count"] == derived["identity"]["feature_count"] == 3655


def test_actual_schedule_and_automatic_followup_identity() -> None:
    data = evidence()
    provenance = data["receipts"]["provenance"]["receipt"]
    source, publication = data["source_execution"], data["publication_execution"]
    assert source["run_id"] == "33379733331"
    assert publication["run_id"] == "33379877031"
    assert source["event"] == "schedule" and publication["event"] == "workflow_run"
    assert source["conclusion"] == publication["conclusion"] == "success"
    for name in ("source_capture", "source_trigger"):
        receipt = provenance[name]
        assert receipt["run_id"] == source["run_id"]
        assert receipt["event"] == source["event"]
        assert receipt["attempt"] == str(source["attempt"])
        assert receipt["code_sha"] == data["producer_revision"]
        assert receipt["status"] == "completed" and receipt["conclusion"] == "success"
    observed = provenance["publication"]
    assert observed["run_id"] == publication["run_id"]
    assert observed["attempt"] == str(publication["attempt"])
    assert observed["event"] == publication["event"]
    assert observed["code_sha"] == data["producer_revision"]
    assert provenance["scheduled_source_trigger_observed"] is True
    assert provenance["automatic_followup"] is True
    assert provenance["capture_checkpoint_reused"] is False
    assert provenance["cycle_key"] == source["run_id"]
    assert observed["status"] == "in_progress" and observed["conclusion"] is None
    assert provenance["publication_job_completion_claimed"] is False
    assert datetime.fromisoformat(observed["updated_at"]) < datetime.fromisoformat(
        publication["job_completed_at"]
    )


def test_ledger_receipt_is_pinned_and_deduplicated_not_three_cycles() -> None:
    data = evidence()
    receipt = data["preservation"]["receipt"]
    assert receipt["status"] == "verified"
    assert receipt["public_repository"] == "edithatogo/riopa-public-data-archive"
    assert receipt["public_revision"] == "46ff54604026525630d7e8e44d3ac4c26edeaddc"
    assert receipt["ledger_path"] == (
        "operational/tasman-cycle-ledger/v1/ledgers/" + receipt["ledger_sha256"] + ".json"
    )
    assert receipt["source_run"] == data["source_execution"]["run_id"]
    assert receipt["publication"] == data["receipts"]["provenance"]["receipt"]["publication"]
    assert (
        receipt["source_run_count"]
        == data["qualification"]["ledger_distinct_source_run_count"]
        == 2
    )
    assert data["qualification"]["scheduled_source_runs_observed"] == ["33379733331"]
    assert receipt["three_cycle_gate_qualified"] is False
    assert receipt["historical_baseline_imported"] is False
    for key in (
        "three_cycle_gate_qualified",
        "adjacent_cycle_change_qualified",
        "hosted_outage_recovery_qualified",
    ):
        assert data["qualification"][key] is False


def test_large_comparison_is_referenced_not_embedded_or_misclassified() -> None:
    data = evidence()
    summary = data["comparison_summary"]
    preservation = data["preservation"]["receipt"]
    derived = data["receipts"]["derived"]["receipt"]
    source = data["receipts"]["source"]["receipt"]
    assert summary["receipt_sha256"] == preservation["receipt_sha256"]["comparison"]
    assert summary["public_revision"] == preservation["public_revision"]
    assert summary["receipt_path"] == (
        "operational/tasman-cycle-ledger/v1/receipts/" + summary["receipt_sha256"] + ".json"
    )
    assert summary["receipt_bytes"] == 1788088 and not summary["full_receipt_embedded"]
    assert summary["after"]["canonical_sha256"] == derived["files"]["canonical.json"]["sha256"]
    assert summary["after"]["source_manifest_sha256"] == source["packet_manifest_sha256"]
    assert summary["before"]["feature_count"] == summary["after"]["feature_count"] == 3655
    assert summary["difference_counts"] == {
        "added": 0,
        "removed": 0,
        "attribute_changed": 3655,
        "geometry_changed": 0,
    }
    assert summary["baseline_role"] == "fixed-initial-accepted-packet-not-previous-cycle"
    assert summary["diagnostic_status"] == "projected-attribute-differences-unattributed"
    assert DOCUMENT.stat().st_size < 20_000


def test_historical_acceptance_is_preserved_and_new_scope_is_explicit() -> None:
    previous = json.loads(
        (ROOT / "docs/tasman-cycle-preservation-acceptance-20260831.json").read_bytes()
    )
    assert previous["event"] == "workflow_dispatch"
    assert previous["attempts"][1]["preservation_receipt"]["source_run_count"] == 1
    data = evidence()
    assert data["artifact"]["id"] == "9753327809"
    assert data["artifact"]["archive_bytes"] == 460041
    assert "GitHub artifacts API" in data["artifact"]["archive_digest_basis"]
    text = " ".join(data["non_claims"])
    assert "not yet attributed" in text
    assert "not two scheduled cycles" in text
    assert "not raw or derived datasets" in text
    assert "complete QLDC ePlan" in text
