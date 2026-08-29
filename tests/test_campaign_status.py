import json
from pathlib import Path

from scripts.validate_campaign_status import validate_status

ROOT = Path(__file__).resolve().parents[1]


def test_checked_in_campaign_status_is_fail_closed_and_revision_bound() -> None:
    document = json.loads(
        (ROOT / "docs/evidence-campaign-status-20260821.json").read_text(encoding="utf-8")
    )
    assert validate_status(document) == ()


def test_campaign_status_rejects_rc_candidate_drift() -> None:
    document = {
        "source_revision": "a" * 40,
        "observations": [
            {
                "run_id": "1",
                "lane": "rc-soak-observation",
                "status": "passed",
                "revision": "a" * 40,
                "candidate_revision": "b" * 40,
                "campaign_id": "rc",
                "qualification_epoch": "epoch",
                "operational_cycle_id": "cycle",
            }
        ],
        "elapsed_gate": {},
        "rc_gate": {"candidate_revision": "a" * 40},
    }
    assert any("candidate must equal" in error for error in validate_status(document))


def test_campaign_status_rejects_duplicate_runs_and_stale_source() -> None:
    observation = {
        "run_id": "1",
        "lane": "operational-observation",
        "status": "passed",
        "revision": "a" * 40,
    }
    document = {
        "source_revision": "b" * 40,
        "observations": [observation, dict(observation)],
        "elapsed_gate": {},
        "rc_gate": {},
    }
    errors = validate_status(document)
    assert any("duplicated" in error for error in errors)
    assert any("latest receipt-bearing" in error for error in errors)


def test_campaign_status_rejects_non_hex_or_uppercase_revisions() -> None:
    document = {
        "source_revision": "A" * 40,
        "observations": [
            {
                "run_id": "1",
                "lane": "operational-observation",
                "status": "passed",
                "revision": "g" * 40,
            }
        ],
        "elapsed_gate": {},
        "rc_gate": {},
    }
    errors = validate_status(document)
    assert any(
        "source_revision must be a 40-character lowercase hexadecimal" in error for error in errors
    )
    assert any(
        "observations[0].revision must be a 40-character lowercase hexadecimal" in error
        for error in errors
    )


def test_campaign_status_rejects_malformed_rc_revision() -> None:
    revision = "f" * 39
    document = {
        "source_revision": revision,
        "observations": [
            {
                "run_id": "1",
                "lane": "rc-soak-observation",
                "status": "passed",
                "revision": revision,
                "candidate_revision": revision,
                "campaign_id": "rc",
                "qualification_epoch": "epoch",
                "operational_cycle_id": "cycle",
            }
        ],
        "elapsed_gate": {},
        "rc_gate": {"candidate_revision": revision},
    }
    errors = validate_status(document)
    assert any(
        "observations[0].revision must be a 40-character lowercase hexadecimal" in error
        for error in errors
    )


def test_campaign_status_rejects_malformed_supplemental_revisions() -> None:
    document = {
        "source_revision": "a" * 40,
        "observations": [
            {
                "run_id": "1",
                "lane": "operational-observation",
                "status": "passed",
                "revision": "a" * 40,
            }
        ],
        "supplemental_observations": [{"revision": "A" * 40, "candidate_revision": "not-a-sha"}],
        "elapsed_gate": {},
        "rc_gate": {},
    }
    errors = validate_status(document)
    assert any(
        "supplemental_observations[0].revision must be a 40-character lowercase hexadecimal"
        in error
        for error in errors
    )
    assert any(
        "supplemental_observations[0].candidate_revision must be a 40-character "
        "lowercase hexadecimal" in error
        for error in errors
    )
