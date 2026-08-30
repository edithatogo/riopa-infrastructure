import json
from copy import deepcopy
from pathlib import Path

import pytest

from riopa_provenance.hashing import sha256_json
from scripts.build_v1_release_gate_snapshot import (
    V1GateSnapshotError,
    build_snapshot,
    evaluate_candidate_continuity,
    write_snapshot,
)

ROOT = Path(__file__).resolve().parents[1]
REVISION = "a" * 40


def test_current_v1_gate_snapshot_is_explicitly_blocked() -> None:
    snapshot = build_snapshot(
        ROOT, evaluated_revision=REVISION, generated_at="2026-08-25T11:30:00Z"
    )
    assert snapshot["status"] == "blocked"
    assert snapshot["release_ready"] is False
    assert snapshot["promotion_allowed"] is False
    assert snapshot["track_summary"]["required"] == 28
    assert snapshot["track_summary"]["qualified"] == 0
    assert snapshot["stable_gate_summary"] == {
        "required": 14,
        "passed": 0,
        "required_gate_ids": snapshot["stable_gate_summary"]["required_gate_ids"],
    }
    assert snapshot["stable_release_evidence_present"] is False
    assert "stable-release-record-absent" in snapshot["blockers"]["release_evidence"]
    digest = snapshot.pop("snapshot_sha256")
    assert digest == sha256_json(snapshot)


def test_current_rc_observations_start_one_fresh_candidate_segment() -> None:
    snapshot = build_snapshot(
        ROOT, evaluated_revision=REVISION, generated_at="2026-08-25T11:30:00Z"
    )
    rc = snapshot["campaign"]["rc"]
    assert rc["observation_count"] == 1
    assert rc["campaign_id"] == "operational-rc-20260830-26bc0b4"
    assert rc["qualification_epoch"] == "rc-epoch-20260830-26bc0b4"
    assert rc["candidate_revisions"] == ["26bc0b49bcd84f409bf24b527e1049fd396c94a6"]
    assert rc["observation_bindings_valid"] is True
    assert rc["exact_candidate_continuity_met"] is False
    assert rc["reset_required"] is False
    assert "rc:exact-candidate-reset-required" not in snapshot["blockers"]["operational_campaign"]
    assert "rc:exact-candidate-continuity-not-met" in snapshot["blockers"]["operational_campaign"]


def test_candidate_continuity_can_only_pass_for_one_declared_candidate() -> None:
    campaign = {
        "rc_gate": {
            "campaign_id": "rc",
            "qualification_epoch": "epoch",
            "candidate_revision": "b" * 40,
            "required_days": 30,
            "status": "passed",
        },
        "observations": [
            {
                "lane": "rc-soak-observation",
                "campaign_id": "rc",
                "run_id": "1",
                "revision": "b" * 40,
                "candidate_revision": "b" * 40,
            }
        ],
    }
    result = evaluate_candidate_continuity(campaign)
    assert result["exact_candidate_continuity_met"] is True
    assert result["reset_required"] is False
    changed = deepcopy(campaign)
    changed["observations"][0]["candidate_revision"] = "c" * 40
    result = evaluate_candidate_continuity(changed)
    assert result["exact_candidate_continuity_met"] is False
    assert result["observation_bindings_valid"] is False


@pytest.mark.parametrize(
    "campaign",
    [
        {},
        {"rc_gate": {}, "observations": []},
        {
            "rc_gate": {"campaign_id": "rc", "candidate_revision": "short"},
            "observations": [],
        },
        {
            "rc_gate": {"campaign_id": "rc", "candidate_revision": "b" * 40},
            "observations": ["bad"],
        },
        {
            "rc_gate": {"campaign_id": "rc", "candidate_revision": "Z" * 40},
            "observations": [],
        },
    ],
)
def test_candidate_continuity_rejects_malformed_campaign(campaign: dict[str, object]) -> None:
    with pytest.raises(V1GateSnapshotError):
        evaluate_candidate_continuity(campaign)


def test_snapshot_rejects_invalid_revision_and_writes_deterministically(tmp_path: Path) -> None:
    with pytest.raises(V1GateSnapshotError, match="evaluated_revision"):
        build_snapshot(ROOT, evaluated_revision="BAD", generated_at="now")
    with pytest.raises(V1GateSnapshotError, match="generated_at"):
        build_snapshot(ROOT, evaluated_revision=REVISION, generated_at="now")
    snapshot = build_snapshot(
        ROOT, evaluated_revision=REVISION, generated_at="2026-08-25T11:30:00Z"
    )
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    write_snapshot(snapshot, first)
    write_snapshot(snapshot, second)
    assert first.read_bytes() == second.read_bytes()


def test_historical_snapshot_digest_is_self_consistent() -> None:
    artifact = json.loads(
        (ROOT / "docs/v1-stable-release-gate-snapshot-20260825.json").read_text(encoding="utf-8")
    )
    digest = artifact.pop("snapshot_sha256")
    assert digest == sha256_json(artifact)
    assert artifact["status"] == "blocked"


def test_successor_snapshot_digest_is_self_consistent() -> None:
    artifact = json.loads(
        (ROOT / "docs/v1-stable-release-gate-snapshot-20260829.json").read_text(encoding="utf-8")
    )
    digest = artifact.pop("snapshot_sha256")
    assert digest == sha256_json(artifact)
    assert artifact["status"] == "blocked"


@pytest.mark.parametrize(
    "filename,revision",
    [
        (
            "docs/v1-stable-release-gate-snapshot-20260829-07686ac.json",
            "07686ac3378a4ac5656d31310f44dfb345dadca7",
        ),
        (
            "docs/v1-stable-release-gate-snapshot-20260829-1fa16a6.json",
            "1fa16a61ff11ef7efbc0f64c5f2dcd98f0da1d1f",
        ),
        (
            "docs/v1-stable-release-gate-snapshot-20260829-012a0e7.json",
            "012a0e7294d39410fac789f873e99666ccb365a3",
        ),
        (
            "docs/v1-stable-release-gate-snapshot-20260830-b0f5d28.json",
            "b0f5d28ef761c7c10948f23ec026ffdaac54dcf9",
        ),
    ],
)
def test_historical_snapshot_digest_and_revision_are_immutable(
    filename: str, revision: str
) -> None:
    artifact = json.loads((ROOT / filename).read_text(encoding="utf-8"))
    digest = artifact.pop("snapshot_sha256")
    assert digest == sha256_json(artifact)
    assert artifact["evaluated_revision"] == revision
    assert artifact["status"] == "blocked"
    assert artifact["promotion_allowed"] is False


def test_current_snapshot_reconstruction_remains_exact() -> None:
    snapshot = build_snapshot(
        ROOT, evaluated_revision=REVISION, generated_at="2026-08-25T11:30:00Z"
    )
    digest = snapshot.pop("snapshot_sha256")
    assert digest == sha256_json(snapshot)
    assert snapshot["evaluated_revision"] == REVISION
    assert snapshot["status"] == "blocked"
