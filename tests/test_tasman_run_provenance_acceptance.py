import json
from pathlib import Path

from riopa_provenance.hashing import sha256_bytes


def test_hosted_attempts_share_source_key_without_cycle_qualification() -> None:
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads(
        (root / "docs/tasman-run-provenance-acceptance-20260831.json").read_text()
    )
    source = json.loads((root / "docs/tasman-publication-acceptance-20260830.json").read_text())
    derived = json.loads((root / "docs/tasman-derived-acceptance-20260831.json").read_text())
    assert evidence["status"] == "hosted-run-provenance-and-retry-verified"
    assert evidence["track"] == source["track"]
    assert evidence["successful_attempts"] == [1, 2]
    records = evidence["attempts"]
    assert len(records) == 2
    for number, record in enumerate(records, 1):
        receipt = record["receipt"]
        assert record["receipt_sha256"] == sha256_bytes(
            (json.dumps(receipt, indent=2) + "\n").encode()
        )
        assert receipt["publication"]["attempt"] == str(number)
        assert receipt["publication"]["run_id"] == evidence["run_id"]
        assert receipt["publication"]["code_sha"] == evidence["producer_revision"]
        assert receipt["publication"]["event"] == "workflow_dispatch"
        assert receipt["publication_job_completion_claimed"] is False
        assert receipt["cycle_key"] == source["publication_receipt"]["source_run"]
        assert receipt["source_capture"]["run_id"] == receipt["cycle_key"]
        assert receipt["source_trigger"]["run_id"] == receipt["cycle_key"]
        assert receipt["source_trigger"]["event"] == "workflow_dispatch"
        assert (
            receipt["source_receipt_sha256"]
            == source["hosted_execution"]["identical_receipts_sha256"]
        )
        assert (
            receipt["derived_receipt_sha256"]
            == derived["hosted_execution"]["identical_receipts_sha256"]
        )
        assert (
            receipt["derived_public_revision"] == derived["publication_receipt"]["public_revision"]
        )
        assert receipt["scheduled_source_trigger_observed"] is False
        assert receipt["automatic_followup"] is False
        assert receipt["release_cycle_qualified"] is False
        assert receipt["change_recovery"] == "not-evaluated"
    assert records[0]["receipt"]["source_capture"] == records[1]["receipt"]["source_capture"]
    assert records[0]["receipt_sha256"] != records[1]["receipt_sha256"]
    assert evidence["ci"]["branch_aware_coverage_percent"] >= 90
