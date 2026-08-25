#!/usr/bin/env python3
"""Build a deterministic, non-authorizing stable-v1 gate snapshot."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_json
from riopa_provenance.roadmap import release_readiness


class V1GateSnapshotError(ValueError):
    """Raised when release-gate inputs cannot be evaluated safely."""


SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
UTC_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise V1GateSnapshotError(f"cannot load gate input: {path}") from exc
    if not isinstance(value, dict):
        raise V1GateSnapshotError(f"gate input must be an object: {path}")
    return value


def _validate_generated_at(value: str) -> str:
    if not UTC_TIMESTAMP_RE.fullmatch(value):
        raise V1GateSnapshotError("generated_at must be a second-precision UTC timestamp")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as exc:
        raise V1GateSnapshotError("generated_at is not a valid UTC timestamp") from exc
    return value


def evaluate_candidate_continuity(campaign: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate exact-candidate continuity without interpreting elapsed duration."""

    gate = campaign.get("rc_gate")
    observations = campaign.get("observations")
    if not isinstance(gate, Mapping) or not isinstance(observations, list):
        raise V1GateSnapshotError("campaign requires rc_gate and observations")
    campaign_id = gate.get("campaign_id")
    declared_candidate = gate.get("candidate_revision")
    if not isinstance(campaign_id, str) or not campaign_id.strip():
        raise V1GateSnapshotError("rc_gate requires campaign_id")
    if not isinstance(declared_candidate, str) or not SHA40_RE.fullmatch(declared_candidate):
        raise V1GateSnapshotError("rc_gate requires a lowercase 40-character SHA")
    relevant: list[dict[str, str]] = []
    for observation in observations:
        if not isinstance(observation, Mapping):
            raise V1GateSnapshotError("campaign observations must be objects")
        if observation.get("lane") != "rc-soak-observation":
            continue
        if observation.get("campaign_id") != campaign_id:
            continue
        revision = observation.get("revision")
        candidate = observation.get("candidate_revision")
        if (
            not isinstance(revision, str)
            or not SHA40_RE.fullmatch(revision)
            or not isinstance(candidate, str)
            or not SHA40_RE.fullmatch(candidate)
        ):
            raise V1GateSnapshotError("RC observations require lowercase 40-character SHAs")
        relevant.append(
            {
                "run_id": str(observation.get("run_id", "")),
                "revision": revision,
                "candidate_revision": candidate,
            }
        )
    candidate_revisions = sorted({item["candidate_revision"] for item in relevant})
    exact_candidate = bool(relevant) and candidate_revisions == [declared_candidate]
    observation_bindings_valid = all(
        item["revision"] == item["candidate_revision"] for item in relevant
    )
    continuity_met = (
        exact_candidate and observation_bindings_valid and gate.get("status") == "passed"
    )
    return {
        "campaign_id": campaign_id,
        "qualification_epoch": gate.get("qualification_epoch"),
        "declared_candidate_revision": declared_candidate,
        "declared_status": gate.get("status"),
        "required_days": gate.get("required_days"),
        "observation_count": len(relevant),
        "candidate_revisions": candidate_revisions,
        "observation_bindings_valid": observation_bindings_valid,
        "exact_candidate_continuity_met": continuity_met,
        "reset_required": bool(relevant) and not exact_candidate,
        "observations": relevant,
    }


def build_snapshot(root: Path, *, evaluated_revision: str, generated_at: str) -> dict[str, Any]:
    """Reconcile track, stable-gate, campaign, artifact, and authority state."""

    base = root.resolve()
    if not SHA40_RE.fullmatch(evaluated_revision):
        raise V1GateSnapshotError("evaluated_revision must be a lowercase 40-character SHA")
    evaluated_at = _validate_generated_at(generated_at.strip())
    gate = _load_object(base / "conductor/v1-gate.json")
    campaign = _load_object(base / "docs/evidence-campaign-status-20260821.json")
    required_tracks = gate.get("required_tracks")
    required_gate_ids = gate.get("required_gate_ids")
    if not isinstance(required_tracks, list) or not isinstance(required_gate_ids, list):
        raise V1GateSnapshotError("v1 gate requires track and gate arrays")

    track_metadata: dict[str, dict[str, Any]] = {}
    for track_id in required_tracks:
        if not isinstance(track_id, str) or not track_id:
            raise V1GateSnapshotError("required track identifiers must be non-empty strings")
        track_metadata[track_id] = _load_object(
            base / "conductor/tracks" / track_id / "metadata.json"
        )

    track_rows: list[dict[str, Any]] = []
    for track_id, metadata in track_metadata.items():
        blockers = metadata.get("blocking_defects")
        if not isinstance(blockers, list):
            raise V1GateSnapshotError(f"track {track_id} blocking_defects must be an array")
        evidence = metadata.get("evidence")
        dependencies = metadata.get("depends_on")
        if not isinstance(evidence, list) or not isinstance(dependencies, list):
            raise V1GateSnapshotError(f"track {track_id} evidence and dependencies must be arrays")
        dependencies_at_required_maturity = all(
            dependency in track_metadata
            and track_metadata[dependency].get("current_maturity") == gate.get("required_maturity")
            for dependency in dependencies
        )
        qualified = (
            metadata.get("status") in {"complete", "archived"}
            and metadata.get("current_maturity") == gate.get("required_maturity")
            and not blockers
            and bool(evidence)
            and dependencies_at_required_maturity
        )
        track_rows.append(
            {
                "track_id": track_id,
                "status": metadata.get("status"),
                "current_maturity": metadata.get("current_maturity"),
                "blocking_defects": blockers,
                "linked_evidence_present": bool(evidence),
                "dependencies_at_required_maturity": dependencies_at_required_maturity,
                "qualified": qualified,
            }
        )

    readiness = release_readiness(base, "1.0.0")
    stable_evidence_path = base / "conductor/release-evidence/1.0.0.json"
    continuity = evaluate_candidate_continuity(campaign)
    operational_gate = campaign.get("elapsed_gate")
    if not isinstance(operational_gate, Mapping):
        raise V1GateSnapshotError("campaign requires elapsed_gate")
    qualified_tracks = sum(bool(row["qualified"]) for row in track_rows)
    stable_evidence_present = stable_evidence_path.is_file()
    operational_campaign_passed = (
        operational_gate.get("status") == "passed" and continuity["exact_candidate_continuity_met"]
    )
    evidence_ready = readiness.ready and operational_campaign_passed
    blockers = {
        "tracks": [row["track_id"] for row in track_rows if not row["qualified"]],
        "stable_gates": (
            []
            if readiness.passed_gates == len(required_gate_ids)
            else [
                f"{len(required_gate_ids) - readiness.passed_gates}-of-"
                f"{len(required_gate_ids)}-not-qualified"
            ]
        ),
        "operational_campaign": [
            f"beta:{operational_gate.get('status')}",
            f"rc:{continuity['declared_status']}",
            "rc:exact-candidate-reset-required" if continuity["reset_required"] else None,
        ],
        "release_evidence": [] if stable_evidence_present else ["stable-release-record-absent"],
        "release_authority": (
            [] if readiness.ready else ["signed-unanimous-decision-not-qualified"]
        ),
        "roadmap": list(readiness.blockers),
    }
    blockers["operational_campaign"] = [
        item for item in blockers["operational_campaign"] if item is not None
    ]
    body: dict[str, Any] = {
        "schema_version": "1.0.0",
        "record_type": "v1_stable_release_gate_snapshot",
        "generated_at": evaluated_at,
        "evaluated_revision": evaluated_revision,
        "release": "1.0.0",
        "status": "evidence-ready" if evidence_ready else "blocked",
        "release_ready": evidence_ready,
        "promotion_allowed": False,
        "track_summary": {
            "required": len(track_rows),
            "qualified": qualified_tracks,
            "tracks": track_rows,
        },
        "stable_gate_summary": {
            "required": len(required_gate_ids),
            "passed": readiness.passed_gates,
            "required_gate_ids": required_gate_ids,
        },
        "campaign": {
            "beta": {
                "campaign_id": operational_gate.get("campaign_id"),
                "status": operational_gate.get("status"),
                "required_days": operational_gate.get("required_days"),
                "required_operational_cycles": operational_gate.get("required_operational_cycles"),
            },
            "rc": continuity,
        },
        "stable_release_evidence_present": stable_evidence_present,
        "blockers": blockers,
        "nonclaims": [
            (
                "This snapshot evaluates declared repository evidence and does not grant "
                "release authority."
            ),
            (
                "Hosted observations do not substitute for elapsed duration, external "
                "reproduction or preservation acceptance."
            ),
            (
                "A candidate revision change resets exact-candidate soak; observations "
                "are not combined across revisions."
            ),
        ],
    }
    body["snapshot_sha256"] = sha256_json(body)
    return body


def write_snapshot(snapshot: Mapping[str, Any], destination: Path) -> None:
    destination.write_text(
        json.dumps(dict(snapshot), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--evaluated-revision", required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    snapshot = build_snapshot(
        args.root,
        evaluated_revision=args.evaluated_revision,
        generated_at=args.generated_at,
    )
    write_snapshot(snapshot, args.output)
    print(
        f"release_ready={snapshot['release_ready']} "
        f"qualified_tracks={snapshot['track_summary']['qualified']}/"
        f"{snapshot['track_summary']['required']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
