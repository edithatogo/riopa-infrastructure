from __future__ import annotations

import json
import runpy
from datetime import datetime
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_bytes

ROOT = Path(__file__).resolve().parents[1]


def test_hosted_cycle_preservation_receipts_rebuild_exact_checkpoints() -> None:
    evidence = json.loads(
        (ROOT / "docs/tasman-cycle-preservation-acceptance-20260831.json").read_bytes()
    )
    core = runpy.run_path(str(ROOT / "scripts/tasman_cycle_ledger.py"))

    def body(value: Any) -> bytes:
        return (json.dumps(value, indent=2) + "\n").encode()

    assert evidence["schema_version"] == "1.0.0"
    assert evidence["track"] == "nz_spatial_archive_mvp_20260718"
    assert evidence["status"] == "hosted-public-metadata-ledger-and-retry-verified"
    assert evidence["producer_revision"] == "ac984b782a7433166a14b72d72c413357df7e09e"
    assert evidence["run_id"] == "33360096774"
    assert evidence["run_url"].endswith("/actions/runs/33360096774")
    assert evidence["event"] == "workflow_dispatch"
    assert evidence["shared_inputs"] == {
        "source": "docs/tasman-publication-acceptance-20260830.json",
        "derived": "docs/tasman-derived-acceptance-20260831.json",
        "comparison": "docs/tasman-feature-comparison-acceptance-20260831.json",
    }
    inputs = {
        name: json.loads((ROOT / path).read_bytes())
        for name, path in evidence["shared_inputs"].items()
    }
    shared = {
        name: body(doc["comparison_receipt" if name == "comparison" else "publication_receipt"])
        for name, doc in inputs.items()
    }
    expected_hashes = {
        "source": "1a62aa1eeb4ea778acb2ec3d98356780af46b0200ae84e7785b9e0cadb676ec2",
        "derived": "e25f96dcf8df5d25bbf3a19d26edcda4cc1e7fc240ea35f5f0a84636bb389e24",
        "comparison": "6d30934d24e62cf78328802afa2b792d6a775a31a604339d85428b88def85ff3",
    }
    assert {name: sha256_bytes(data) for name, data in shared.items()} == expected_hashes
    assert [a["attempt"] for a in evidence["attempts"]] == [1, 2]
    assert [a["job_id"] for a in evidence["attempts"]] == ["99389645033", "99389916004"]
    revisions = [
        "77ddbe7f3e9a7715da443c8be5eda34e2d2795be",
        "148b99fdc661badfc8ce78f771e76a80572be1f0",
    ]
    ledger = None
    previous_completion = None
    for index, attempt in enumerate(evidence["attempts"]):
        receipt = attempt["preservation_receipt"]
        provenance = attempt["provenance_receipt"]
        assert sha256_bytes(body(receipt)) == attempt["preservation_receipt_sha256"]
        assert sha256_bytes(body(provenance)) == attempt["provenance_receipt_sha256"]
        # Match the publisher's FILES insertion order for physical JSON bytes.
        documents = {
            "source": shared["source"],
            "derived": shared["derived"],
            "provenance": body(provenance),
            "comparison": shared["comparison"],
        }
        hashes = {name: sha256_bytes(data) for name, data in documents.items()}
        assert receipt["receipt_sha256"] == hashes
        ledger = core["append_observation"](ledger, documents, hashes)
        core["validate"](ledger)
        assert sha256_bytes(body(ledger)) == receipt["ledger_sha256"]
        assert ledger["ledger_sha256"] == receipt["ledger_semantic_sha256"]
        assert receipt["ledger_path"] == (
            f"operational/tasman-cycle-ledger/v1/ledgers/{receipt['ledger_sha256']}.json"
        )
        assert receipt["public_repository"] == "edithatogo/riopa-public-data-archive"
        assert receipt["public_revision"] == revisions[index]
        assert receipt["record_type"] == "tasman_cycle_ledger_preservation"
        assert receipt["status"] == "verified"
        assert receipt["source_run"] == provenance["cycle_key"] == "33301038921"
        assert receipt["source_run_count"] == ledger["unique_source_run_count"] == 1
        assert len(ledger["events"]) == index + 1
        assert ledger["source_runs"] == ["33301038921"]
        assert ledger["scheduled_automatic_source_runs"] == []
        assert receipt["three_cycle_gate_qualified"] is False
        assert ledger["three_cycle_gate_qualified"] is False
        assert receipt["historical_baseline_imported"] is False
        assert receipt["qualification_gaps"] == ledger["qualification_gaps"]
        publication = provenance["publication"]
        assert receipt["publication"] == publication
        assert publication["run_id"] == evidence["run_id"]
        assert publication["code_sha"] == evidence["producer_revision"]
        assert publication["attempt"] == str(attempt["attempt"])
        assert publication["event"] == "workflow_dispatch"
        assert publication["status"] == "in_progress" and publication["conclusion"] is None
        assert provenance["publication_job_completion_claimed"] is False
        assert provenance["scheduled_source_trigger_observed"] is False
        assert provenance["automatic_followup"] is False
        assert provenance["release_cycle_qualified"] is False
        assert attempt["conclusion"] == "success"
        completed = datetime.fromisoformat(attempt["completed_at"])
        assert completed > datetime.fromisoformat(publication["updated_at"])
        if previous_completion is not None:
            assert datetime.fromisoformat(publication["run_started_at"]) > previous_completion
        previous_completion = completed
        assert core["append_observation"](ledger, documents, hashes) == ledger
