#!/usr/bin/env python3
"""Build a fail-closed elapsed-evidence ledger from hosted receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path}: receipt must be an object")
    return value


def build_ledger(
    paths: list[Path], *, maximum_gap_hours: int = 36, now: datetime | None = None
) -> dict[str, Any]:
    if not paths:
        raise ValueError("at least one receipt is required")
    loaded = [(path, _load(path)) for path in paths]
    campaign_ids = {receipt.get("campaign_id") for _, receipt in loaded}
    if None in campaign_ids or len(campaign_ids) != 1:
        raise ValueError("receipts must share one explicit campaign_id")
    lanes = {receipt.get("lane") for _, receipt in loaded}
    if lanes not in ({"operational-observation"}, {"rc-soak-observation"}):
        raise ValueError("a ledger must contain exactly one elapsed-evidence lane")
    expected_classification = (
        "qualifying-rc-observation"
        if lanes == {"rc-soak-observation"}
        else "qualifying-beta-observation"
    )
    observations = []
    seen_receipts: set[str] = set()
    duplicate_receipt_count = 0
    for path, receipt in loaded:
        receipt_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        if receipt_sha256 in seen_receipts:
            duplicate_receipt_count += 1
            continue
        seen_receipts.add(receipt_sha256)
        lane = receipt.get("lane")
        if receipt.get("classification") != expected_classification:
            raise ValueError(f"{path}: receipt classification is not qualifying for {lane}")
        activation = receipt.get("campaign_activation")
        if not isinstance(activation, dict) or activation.get("status") != "activated":
            raise ValueError(f"{path}: qualifying receipt requires campaign activation")
        if activation.get("campaign_id") != receipt.get("campaign_id"):
            raise ValueError(f"{path}: campaign activation is not bound to campaign_id")
        if not activation.get("authority") or not activation.get("activated_at"):
            raise ValueError(f"{path}: campaign activation requires authority and activated_at")
        run_id = receipt.get("hosted_run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            raise ValueError(f"{path}: qualifying receipt requires a hosted_run_id")
        revision = receipt.get("source_revision")
        candidate = receipt.get("candidate_revision")
        if lane == "rc-soak-observation" and candidate != revision:
            raise ValueError(f"{path}: RC observation is not bound to its source revision")
        observations.append(
            {
                "lane": lane,
                "status": receipt.get("status"),
                "source_revision": revision,
                "candidate_revision": candidate,
                "qualification_epoch": receipt.get("qualification_epoch"),
                "operational_cycle_id": receipt.get("operational_cycle_id"),
                "classification": receipt.get("classification"),
                "hosted_run_id": run_id,
                "started_at": receipt.get("started_at"),
                "ended_at": receipt.get("ended_at"),
                "receipt_sha256": receipt_sha256,
            }
        )
    observations.sort(key=lambda item: str(item["started_at"]))
    current_time = now or datetime.now(UTC)
    if current_time.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    observed_dates: set[str] = set()
    previous_chain = ""
    for observation in observations:
        start = datetime.fromisoformat(str(observation["started_at"]).replace("Z", "+00:00"))
        end = datetime.fromisoformat(str(observation["ended_at"]).replace("Z", "+00:00"))
        if end < start:
            raise ValueError("receipt ended_at precedes started_at")
        if start > current_time or end > current_time:
            raise ValueError("receipt timestamps cannot be in the future")
        observed_date = start.date().isoformat()
        if observed_date in observed_dates:
            raise ValueError("qualifying receipts require distinct UTC observation dates")
        observed_dates.add(observed_date)
        previous_chain = hashlib.sha256(
            f"{previous_chain}:{observation['receipt_sha256']}".encode()
        ).hexdigest()
        observation["chain_sha256"] = previous_chain
    segments: list[dict[str, Any]] = []
    for observation in observations:
        if not observation["qualification_epoch"]:
            raise ValueError("receipts require an explicit qualification_epoch")
        if not observation["operational_cycle_id"]:
            raise ValueError("receipts require an explicit operational_cycle_id")
        is_rc = observation["lane"] == "rc-soak-observation"
        reset = not segments or segments[-1]["failed"]
        if segments and not reset:
            reset = segments[-1]["qualification_epoch"] != observation["qualification_epoch"]
        if segments and not reset and is_rc:
            reset = segments[-1]["source_revision"] != observation["source_revision"]
        if reset:
            segments.append(
                {
                    "source_revision": observation["source_revision"],
                    "source_revisions": [],
                    "qualification_epoch": observation["qualification_epoch"],
                    "started_at": observation["started_at"],
                    "ended_at": observation["ended_at"],
                    "observation_count": 0,
                    "operational_cycle_ids": [],
                    "maximum_gap_seconds": 0,
                    "failed": False,
                }
            )
        segment = segments[-1]
        previous_end = datetime.fromisoformat(str(segment["ended_at"]).replace("Z", "+00:00"))
        current_start = datetime.fromisoformat(
            str(observation["started_at"]).replace("Z", "+00:00")
        )
        if segment["observation_count"]:
            segment["maximum_gap_seconds"] = max(
                segment["maximum_gap_seconds"],
                max(0, int((current_start - previous_end).total_seconds())),
            )
        segment["observation_count"] += 1
        if observation["source_revision"] not in segment["source_revisions"]:
            segment["source_revisions"].append(observation["source_revision"])
        if observation["operational_cycle_id"] not in segment["operational_cycle_ids"]:
            segment["operational_cycle_ids"].append(observation["operational_cycle_id"])
        segment["ended_at"] = observation["ended_at"]
        segment["failed"] = observation["status"] != "passed"
    active = segments[-1]
    start = datetime.fromisoformat(str(active["started_at"]).replace("Z", "+00:00"))
    end = datetime.fromisoformat(str(active["ended_at"]).replace("Z", "+00:00"))
    active["elapsed_seconds"] = max(0, int((end - start).total_seconds()))
    required_days = 30 if lanes == {"rc-soak-observation"} else 90
    required_cycles = 1 if lanes == {"rc-soak-observation"} else 3
    cadence_passed = active["maximum_gap_seconds"] <= maximum_gap_hours * 3600
    cycles_passed = len(active["operational_cycle_ids"]) >= required_cycles
    duration_passed = active["elapsed_seconds"] >= required_days * 86400
    daily_observations_passed = len(observed_dates) >= required_days
    return {
        "schema": "riopa.evidence-campaign-ledger.v1",
        "campaign_id": campaign_ids.pop(),
        "observations": observations,
        "duplicate_receipt_count": duplicate_receipt_count,
        "chain_head_sha256": previous_chain,
        "segments": segments,
        "active_segment": active,
        "required_elapsed_days": required_days,
        "required_operational_cycles": required_cycles,
        "required_daily_observations": required_days,
        "distinct_observation_dates": len(observed_dates),
        "maximum_allowed_gap_hours": maximum_gap_hours,
        "duration_status": "passed" if duration_passed else "pending-duration",
        "cadence_status": "passed" if cadence_passed else "failed-gap",
        "operational_cycles_status": "passed" if cycles_passed else "pending-cycles",
        "daily_observations_status": (
            "passed" if daily_observations_passed else "pending-observations"
        ),
        "elapsed_gate_status": "passed"
        if duration_passed
        and cadence_passed
        and cycles_passed
        and daily_observations_passed
        and not active["failed"]
        else "pending",
        "non_claims": [
            "Observation count does not substitute for elapsed time.",
            "A qualification-epoch change or failed observation starts a new beta segment.",
            "An RC source-revision change starts a new RC segment.",
            "Passing requires bounded observation gaps and the required operational cycles.",
            "Operational observations do not start the RC clock.",
            "Identical receipt bytes restored under multiple artifact paths count once.",
            "Preview drills and receipts without an activated campaign never qualify.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipts", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    ledger = build_ledger(args.receipts)
    args.output.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
