#!/usr/bin/env python3
"""Offline, hash-bound observation ledger; never a release-cycle attestation."""

from __future__ import annotations

import argparse
import json
import re
import runpy
from datetime import datetime
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_bytes, sha256_json

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("provenance", "comparison", "source", "derived")
LIMIT = 2_000_000
MAX_EVENTS = 100
GAPS = [
    "Verified signed hosted completion evidence is not consumed by this offline ledger.",
    "Fixed-baseline comparisons are not adjacent-cycle change evidence.",
    "Hosted change and recovery qualification remains unassessed.",
]


def check(condition: bool) -> None:
    if not condition:
        raise ValueError("ledger evidence binding failed")


def digest(value: Any) -> str:
    check(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None)
    return str(value)


def timestamp(value: Any) -> datetime:
    check(isinstance(value, str) and len(value) <= 40)
    result = datetime.fromisoformat(value)
    check(result.tzinfo is not None)
    return result


def parse(body: bytes) -> dict[str, Any]:
    check(0 < len(body) <= LIMIT)

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            check(key not in result)
            result[key] = value
        return result

    result = json.loads(body, object_pairs_hook=pairs)
    check(isinstance(result, dict))
    # RFC8785 also rejects NaN/infinities and unsupported numbers.
    sha256_json(result)
    return dict(result)


def observation(documents: dict[str, bytes], expected: dict[str, str]) -> dict[str, Any]:
    check(set(documents) == set(expected) == set(NAMES))
    for name in NAMES:
        check(sha256_bytes(documents[name]) == digest(expected[name]))
    p, c, s, d = (parse(documents[name]) for name in NAMES)
    validator = runpy.run_path(str(ROOT / "scripts/record_tasman_snapshot_comparison.py"))
    validator["derived_receipt"](d)
    check(p.get("record_type") == "tasman_run_provenance")
    check(p.get("repository") == "edithatogo/riopa-infrastructure")
    check(c.get("record_type") == "tasman_fixed_baseline_snapshot_comparison")
    check(c.get("status") == "compared")
    check(c.get("baseline_role") == "fixed-initial-accepted-packet-not-previous-cycle")
    check(s.get("source_id") == "urn:riopa:source:tasman:geohub")
    check(s.get("status") == "public-packet-verified-and-rebuilt")
    check(s.get("state") == "verified" and s.get("anonymous_full_packet_verified") is True)
    check(s.get("public_dataset_repository") == d["public_repository"])
    check(s.get("licence") == d["licence"] and s.get("attribution") == d["attribution"])
    for evidence in (p, c):
        check(evidence.get("source_receipt_sha256") == expected["source"])
        check(evidence.get("derived_receipt_sha256") == expected["derived"])
        check(evidence.get("source_public_revision") == s.get("public_revision"))
        check(evidence.get("source_packet_manifest_sha256") == s.get("packet_manifest_sha256"))
        check(evidence.get("derived_public_revision") == d["public_revision"])
        check(evidence.get("release_cycle_qualified") is False)
    identity = d["identity"]
    check(identity["source_revision"] == s["public_revision"])
    check(identity["source_manifest_sha256"] == s["packet_manifest_sha256"])
    check(identity["feature_count"] == s["reproduction"]["feature_count"])
    check(identity["geoparquet_sha256"] == s["reproduction"]["geoparquet_sha256"])
    check(p.get("derived_logical_sha256") == d["logical_sha256"])
    diff = c["comparison"]
    check(
        diff.get("comparison_sha256")
        == sha256_json({key: value for key, value in diff.items() if key != "comparison_sha256"})
    )
    check(diff["after"]["source_manifest_sha256"] == s["packet_manifest_sha256"])
    check(diff["after"]["feature_count"] == identity["feature_count"])
    check(diff["after"]["canonical_sha256"] == d["files"]["canonical.json"]["sha256"])
    check(c["current_canonical_sha256"] == diff["after"]["canonical_sha256"])
    check(c["baseline_canonical_sha256"] == diff["before"]["canonical_sha256"])
    check(diff.get("release_cycle_qualified") is False)
    run_validator = runpy.run_path(str(ROOT / "scripts/record_tasman_run_provenance.py"))
    number = run_validator["number"]
    run = number(p["cycle_key"])
    check(s.get("source_run") == run)
    # Current comparison schema binds source bytes rather than carrying source_run.
    # If a future producer supplies it, reject contradictory redundant identity.
    check("source_run" not in c or c["source_run"] == run)
    for key in ("source_capture", "source_trigger", "publication"):
        record = p[key]
        is_source = key != "publication"
        raw = {
            **record,
            "id": record["run_id"],
            "run_attempt": record["attempt"],
            "head_sha": record["code_sha"],
            "path": record["workflow_path"],
            "repository": {"full_name": p["repository"]},
            "head_repository": {"full_name": p["repository"]},
            "head_branch": "main",
        }
        run_validator["run_record"](
            raw,
            number(record["run_id"]),
            number(record["attempt"]),
            "council-archive.yml" if is_source else "tasman-publication.yml",
            source=is_source,
            require_success=key != "source_capture",
        )
        if is_source:
            check(record["run_id"] == run)
    captured, trigger, publication = (
        p[key] for key in ("source_capture", "source_trigger", "publication")
    )
    check(int(captured["attempt"]) <= int(trigger["attempt"]))
    check(captured["code_sha"] == trigger["code_sha"])
    check(captured["event"] == trigger["event"])
    check(
        p.get("source_capture_status_basis")
        == "verified-publication-receipt-and-archived-hosted-run"
    )
    digest(p.get("archived_hosted_run_sha256"))
    check(s.get("private_prefix") == f"campaigns/{run}/tasman/{captured['attempt']}")
    check(timestamp(captured["run_started_at"]) <= timestamp(trigger["run_started_at"]))
    check(timestamp(trigger["updated_at"]) <= timestamp(publication["run_started_at"]))
    automatic = publication["event"] == "workflow_run"
    scheduled = trigger["event"] == "schedule"
    check(p.get("automatic_followup") is automatic)
    check(p.get("scheduled_source_trigger_observed") is scheduled)
    check(p.get("capture_checkpoint_reused") is (captured["attempt"] != trigger["attempt"]))
    return {
        "kind": "observation",
        "source_run": run,
        "source_identity": {
            "capture": captured,
            "manifest": s["packet_manifest_sha256"],
            "revision": s["public_revision"],
        },
        "publication": publication,
        "source_trigger": trigger,
        "evidence_sha256": dict(expected),
        "scheduled_automatic_observation": scheduled and automatic,
        "manual_replay_ineligible": not automatic,
        "comparison_basis": "fixed-baseline-not-adjacent",
        "outcome": "receipt-verified-not-completion-attested",
    }


def assemble(events: list[dict[str, Any]]) -> dict[str, Any]:
    runs: dict[str, dict[str, Any]] = {}
    attempts: set[tuple[str, str]] = set()
    latest_attempt: dict[str, int] = {}
    previous: str | None = None
    previous_time: datetime | None = None
    for event in events:
        check(event["previous_event_sha256"] == previous)
        check(
            event["event_sha256"]
            == sha256_json({key: value for key, value in event.items() if key != "event_sha256"})
        )
        previous = event["event_sha256"]
        if event["kind"] == "local-rejected-attempt":
            check(event["hosted_recovery_qualified"] is False)
            continue
        check(event["kind"] == "observation")
        automatic = event["publication"]["event"] == "workflow_run"
        scheduled = event["source_trigger"]["event"] == "schedule"
        check(event["scheduled_automatic_observation"] is (automatic and scheduled))
        check(event["manual_replay_ineligible"] is (not automatic))
        check(event["source_trigger"]["run_id"] == event["source_run"])
        check(event["source_identity"]["capture"]["run_id"] == event["source_run"])
        check(event["source_identity"]["capture"]["event"] == event["source_trigger"]["event"])
        check(event["comparison_basis"] == "fixed-baseline-not-adjacent")
        check(event["outcome"] == "receipt-verified-not-completion-attested")
        attempt = (event["publication"]["run_id"], event["publication"]["attempt"])
        check(attempt not in attempts)
        check(int(attempt[1]) > latest_attempt.get(attempt[0], 0))
        latest_attempt[attempt[0]] = int(attempt[1])
        attempts.add(attempt)
        run = event["source_run"]
        if run in runs:
            check(runs[run]["source_identity"] == event["source_identity"])
            check(event["predecessor_source_run"] == runs[run]["predecessor_source_run"])
        else:
            now = timestamp(event["source_identity"]["capture"]["run_started_at"])
            check(previous_time is None or now > previous_time)
            check(event["predecessor_source_run"] == next(reversed(runs), None))
            runs[run] = event
            previous_time = now
    result = {
        "record_type": "tasman_offline_cycle_ledger",
        "schema_version": "1.0.0",
        "events": events,
        "source_runs": list(runs),
        "unique_source_run_count": len(runs),
        "scheduled_automatic_source_runs": sorted(
            {
                e["source_run"]
                for e in events
                if e["kind"] == "observation" and e["scheduled_automatic_observation"]
            },
            key=int,
        ),
        "three_cycle_gate_qualified": False,
        "qualification_gaps": GAPS,
    }
    return {**result, "ledger_sha256": sha256_json(result)}


def validate(ledger: dict[str, Any] | None) -> list[dict[str, Any]]:
    if ledger is None:
        return []
    events = ledger["events"]
    check(isinstance(events, list) and len(events) <= MAX_EVENTS)
    check(assemble(events) == ledger)
    return list(events)


def append_event(ledger: dict[str, Any] | None, event: dict[str, Any]) -> dict[str, Any]:
    events = validate(ledger)
    if event["kind"] == "observation":
        prior = [e for e in events if e["kind"] == "observation"]
        same = [e for e in prior if e["source_run"] == event["source_run"]]
        event["predecessor_source_run"] = (
            same[0]["predecessor_source_run"]
            if same
            else (list(dict.fromkeys(e["source_run"] for e in prior))[-1] if prior else None)
        )
        for old in prior:
            if (
                old["publication"]["run_id"] == event["publication"]["run_id"]
                and old["publication"]["attempt"] == event["publication"]["attempt"]
            ):
                check(
                    {
                        k: v
                        for k, v in old.items()
                        if k not in ("event_sha256", "previous_event_sha256")
                    }
                    == event
                )
                return assemble(events)
    check(len(events) < MAX_EVENTS)
    event["previous_event_sha256"] = events[-1]["event_sha256"] if events else None
    event["event_sha256"] = sha256_json(event)
    return assemble([*events, event])


def append_observation(
    ledger: dict[str, Any] | None, documents: dict[str, bytes], expected_sha256: dict[str, str]
) -> dict[str, Any]:
    return append_event(ledger, observation(documents, expected_sha256))


def record_rejected_attempt(
    ledger: dict[str, Any] | None, attempt_id: str, error_class: str
) -> dict[str, Any]:
    """Record local validation failure, not a hosted source or recovery outcome."""
    check(re.fullmatch(r"[A-Za-z0-9_-]{1,64}", attempt_id) is not None)
    check(error_class in ("ValueError", "KeyError", "TypeError", "OSError"))
    return append_event(
        ledger,
        {
            "kind": "local-rejected-attempt",
            "attempt_id": attempt_id,
            "error_class": error_class,
            "hosted_recovery_qualified": False,
        },
    )


def read(path: Path, limit: int = LIMIT) -> bytes:
    check(".." not in path.parts and not any(p.is_symlink() for p in (path, *path.parents)))
    check(path.is_file() and 0 < path.stat().st_size <= limit)
    return path.read_bytes()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in NAMES:
        parser.add_argument(f"--{name}", type=Path, required=True)
        parser.add_argument(f"--{name}-sha256", required=True)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--ledger-sha256")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        check((args.ledger is None) == (args.ledger_sha256 is None))
        ledger = None
        if args.ledger is not None:
            body = read(args.ledger)
            check(sha256_bytes(body) == digest(args.ledger_sha256))
            ledger = parse(body)
        result = append_observation(
            ledger,
            {n: read(getattr(args, n)) for n in NAMES},
            {n: getattr(args, n + "_sha256") for n in NAMES},
        )
        output = args.output
        check(
            ".." not in output.parts and not any(p.is_symlink() for p in (output, *output.parents))
        )
        with output.open("x") as target:
            target.write(json.dumps(result, indent=2) + "\n")
    except Exception as error:
        print(json.dumps({"status": "failed", "error_class": type(error).__name__[:128]}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
