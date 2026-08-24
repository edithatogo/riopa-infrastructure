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
