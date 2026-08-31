#!/usr/bin/env python3
"""Read-only progress projection; no network, local routing state or gate promotion."""

from __future__ import annotations

import argparse
import json
import re
import runpy
from collections import Counter
from pathlib import Path
from typing import Any

from riopa_provenance.hashing import sha256_bytes, sha256_file, sha256_json
from riopa_provenance.roadmap import roadmap_status, validate_roadmap

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RECEIPTS = (
    "docs/tasman-publication-acceptance-20260830.json",
    "docs/tasman-derived-acceptance-20260831.json",
    "docs/tasman-run-provenance-acceptance-20260831.json",
    "docs/tasman-feature-comparison-acceptance-20260831.json",
    "docs/tasman-first-scheduled-cycle-20260831.json",
)


def plan_tasks(text: str) -> list[dict[str, str]]:
    """Count top-level task rows only, excluding examples in fenced code blocks."""
    tasks = []
    phase = "Unsectioned"
    fence: str | None = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        if line.startswith("## "):
            phase = line[3:].strip()
        match = re.match(r"^- \[([x~ ])\] (.+)$", line)
        if match:
            tasks.append({"state": match[1], "phase": phase, "task": match[2]})
    return tasks


def track_progress(root: Path) -> list[dict[str, Any]]:
    result = []
    identities: set[str] = set()
    for location in ("tracks", "archive"):
        for path in sorted((root / "conductor" / location).glob("*/metadata.json")):
            for file in (path, path.with_name("plan.md")):
                if any(p.is_symlink() for p in (file, *file.parents)):
                    raise ValueError("symlinked track input")
                if not file.is_file() or not 0 < file.stat().st_size <= 2_000_000:
                    raise ValueError("missing or oversized track input")
            metadata = json.loads(path.read_bytes())
            identity = metadata["track_id"]
            if identity != path.parent.name or identity in identities:
                raise ValueError("duplicate or mismatched track identity")
            identities.add(identity)
            tasks = plan_tasks(path.with_name("plan.md").read_text())
            counts = Counter(item["state"] for item in tasks)
            current = next((item for item in tasks if item["state"] == "~"), None)
            pending = next((item for item in tasks if item["state"] == " "), None)
            result.append(
                {
                    "track_id": identity,
                    "status": metadata["status"],
                    "maturity": metadata["current_maturity"],
                    "location": str(path.parent.relative_to(root)),
                    "tasks": {
                        "completed": counts["x"],
                        "in_progress": counts["~"],
                        "pending": counts[" "],
                        "total": len(tasks),
                    },
                    "current_task": current,
                    "next_pending_task": pending,
                    "blocking_defects": metadata.get("blocking_defects", []),
                    "plan_sha256": sha256_file(path.with_name("plan.md")),
                    "metadata_sha256": sha256_file(path),
                }
            )
    if not result:
        raise ValueError("no Conductor tracks")
    return sorted(result, key=lambda item: item["track_id"])


def report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    problems = validate_roadmap(root)
    if problems:
        raise ValueError("Conductor validation failed: " + "; ".join(p.code for p in problems))
    tracks = track_progress(root)
    # Load the shipped implementation, never arbitrary executable code from --root.
    orchestrator = runpy.run_path(str(ROOT / "scripts/codex_orchestrator.py"))
    queue = orchestrator["load_queue"](root=root)
    state = orchestrator["reconcile_state"](queue, {"packages": {}}, root=root)
    totals = {
        key: sum(t["tasks"][key] for t in tracks)
        for key in ("completed", "in_progress", "pending", "total")
    }
    next_package = orchestrator["choose_next"](queue, state)
    archive_path = root / "docs/archive-current-status-20260831.json"
    archive = json.loads(archive_path.read_bytes())
    validate_archive_evidence(root, archive)
    ledger_path = root / "docs/tasman-cycle-ledger-baseline-20260831.json"
    ledger = json.loads(ledger_path.read_bytes())
    ledger_tools = runpy.run_path(str(ROOT / "scripts/tasman_cycle_ledger.py"))
    ledger_tools["validate"](ledger)
    return {
        "schema_version": "1.0.0",
        "record_type": "repository_progress_projection",
        "integrity": "passed",
        "task_counting": "top-level plan checkbox rows; fenced examples and subtasks excluded",
        "task_totals": totals,
        "tracks": tracks,
        "release_readiness": roadmap_status(root),
        "work_packages": state["packages"],
        "next_work_package": next_package.identifier if next_package else None,
        "archive_evidence": archive,
        "archive_evidence_sha256": sha256_file(archive_path),
        "recorded_cycle_ledger": {
            key: ledger[key]
            for key in (
                "unique_source_run_count",
                "scheduled_automatic_source_runs",
                "three_cycle_gate_qualified",
                "qualification_gaps",
            )
        },
        "recorded_cycle_ledger_sha256": sha256_file(ledger_path),
        "non_claims": [
            "Local evidence projection; hosted systems and credentials are not queried.",
            "Task completion is not release readiness, publication or accountable approval.",
            "Local routing overrides are excluded; waivers are assessed at invocation time.",
        ],
    }


def validate_archive_evidence(root: Path, archive: dict[str, Any]) -> None:
    if archive.get("record_type") != "bounded_archive_current_disposition":
        raise ValueError("unexpected archive disposition")
    references = archive.get("evidence_refs")
    if not isinstance(references, list) or not references:
        raise ValueError("missing archive evidence references")
    paths: set[str] = set()
    documents: dict[str, Any] = {}
    for reference in references:
        relative = reference["path"]
        if not isinstance(relative, str):
            raise ValueError("unsafe archive evidence path")
        path = root / relative
        if (
            not isinstance(relative, str)
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or not path.resolve().is_relative_to((root / "docs").resolve())
            or any(p.is_symlink() for p in (path, *path.parents))
            or relative in paths
        ):
            raise ValueError("unsafe or duplicate archive evidence path")
        paths.add(relative)
        if (
            not path.is_file()
            or not 0 < path.stat().st_size <= 2_000_000
            or sha256_file(path) != reference["sha256"]
        ):
            raise ValueError("archive evidence digest mismatch")
        documents[relative] = json.loads(path.read_bytes())
    if paths != set(ARCHIVE_RECEIPTS):
        raise ValueError("unexpected archive evidence set")
    expected = archive_projection(documents)
    expected["evidence_refs"] = [
        {"path": path, "sha256": sha256_file(root / path)} for path in ARCHIVE_RECEIPTS
    ]
    # Canonical comparison distinguishes booleans from integers as well as extra keys.
    if sha256_json(archive) != sha256_json(expected):
        raise ValueError("archive disposition differs from receipt-derived claims")


def archive_projection(documents: dict[str, Any]) -> dict[str, Any]:
    """Project only this accepted Tasman packet; not a generic receipt trust engine."""
    source, derived, provenance, comparison = (documents[path] for path in ARCHIVE_RECEIPTS[:4])

    def check(condition: bool) -> None:
        if not condition:
            raise ValueError("archive acceptance receipt semantic mismatch")

    for document, status in zip(
        (source, derived, provenance, comparison),
        (
            "hosted-publication-and-rebuild-verified",
            "hosted-derived-publication-and-replay-verified",
            "hosted-run-provenance-and-retry-verified",
            "hosted-fixed-baseline-comparison-verified",
        ),
        strict=True,
    ):
        check(document["schema_version"] == "1.0.0")
        check(document["track"] == "nz_spatial_archive_mvp_20260718")
        check(document["status"] == status)
    s, d, c = (
        source["publication_receipt"],
        derived["publication_receipt"],
        comparison["comparison_receipt"],
    )

    def body(value: dict[str, Any]) -> bytes:
        # Exact serialization used by these four historical producers.
        return (json.dumps(value, indent=2) + "\n").encode()

    check(s["reproduction"]["builds"] == 2)
    check(type(s["reproduction"]["feature_count"]) is int)
    check(s["reproduction"]["feature_count"] > 0)
    for document, receipt in ((source, s), (derived, d)):
        check(
            sha256_bytes(body(receipt)) == document["hosted_execution"]["identical_receipts_sha256"]
        )
        check(document["hosted_execution"]["successful_attempts"] == [1, 2])
        check(document["hosted_execution"]["original_public_revision_reused"] is True)
    check(sha256_bytes(body(c)) == comparison["hosted_execution"]["receipt_sha256"])
    check(comparison["hosted_execution"]["conclusion"] == "success")
    check(comparison["hosted_execution"]["event"] == "workflow_dispatch")
    check(comparison["hosted_execution"]["source_run"] == s["source_run"])
    check(c["baseline_public_revision"] == d["public_revision"])
    check(c["baseline_acceptance_sha256"] == sha256_bytes(body(derived)))
    diff = c["comparison"]
    check(
        all(
            diff[name] == []
            for name in ("added", "removed", "attribute_changed", "geometry_changed")
        )
    )
    check(diff["change_hashes"] == {})
    check(diff["before"] == diff["after"])
    check(c["baseline_canonical_sha256"] == c["current_canonical_sha256"])
    # Reuse the shipped receipt binding validator, not executable code from --root.
    ledger = runpy.run_path(str(ROOT / "scripts/tasman_cycle_ledger.py"))
    attempts = provenance["attempts"]
    check(isinstance(attempts, list) and len(attempts) == 2)
    check([a["receipt"]["publication"]["attempt"] for a in attempts] == ["1", "2"])
    for attempt in attempts:
        p = attempt["receipt"]
        check(sha256_bytes(body(p)) == attempt["receipt_sha256"])
        check(
            all(
                p[name]["event"] == "workflow_dispatch"
                for name in ("source_capture", "source_trigger", "publication")
            )
        )
        check(p["automatic_followup"] is False)
        check(p["scheduled_source_trigger_observed"] is False)
        check(p["publication_job_completion_claimed"] is False)
        check(p["change_recovery"] == "not-evaluated")
        documents_bytes = {
            "source": body(s),
            "derived": body(d),
            "comparison": body(c),
            "provenance": body(p),
        }
        ledger["observation"](
            documents_bytes, {k: sha256_bytes(v) for k, v in documents_bytes.items()}
        )
    scheduled = scheduled_archive_projection(documents[ARCHIVE_RECEIPTS[4]], s, d)
    return {
        "schema_version": "1.0.0",
        "record_type": "bounded_archive_current_disposition",
        "as_of": "2026-08-31",
        "track": "nz_spatial_archive_mvp_20260718",
        "basis": "checked-in-immutable-acceptance-receipts-not-a-fresh-network-observation",
        "source_scope": "Tasman selected TRMP zones layer and standalone item rights only",
        "public_repository": s["public_dataset_repository"],
        "feature_count": s["reproduction"]["feature_count"],
        "licence": s["licence"],
        "attribution": s["attribution"],
        "dispositions": {
            "source_publication": {
                "status": "accepted",
                "role": "historical-baseline",
                "evidence": ARCHIVE_RECEIPTS[0],
                "public_revision": s["public_revision"],
            },
            "derived_publication": {
                "status": "accepted",
                "role": "historical-baseline",
                "evidence": ARCHIVE_RECEIPTS[1],
                "public_revision": d["public_revision"],
            },
            "run_attempt_binding": {
                "status": "accepted-manual-replay",
                "role": "historical-baseline",
                "evidence": ARCHIVE_RECEIPTS[2],
            },
            "fixed_baseline_comparison": {
                "status": "accepted-no-feature-differences",
                "role": "historical-baseline",
                "evidence": ARCHIVE_RECEIPTS[3],
            },
            "scheduled_capture_and_publication": scheduled,
        },
        "supersession": {
            "scope": "Earlier pending-publication wording for this exact source and derived "
            "packet is historical, not a current blocker.",
            "historical_receipts_modified": False,
            "source_only_receipt_reinterpreted_as_derived_publication": False,
        },
        "remaining_qualification": [
            "wider-council-and-national-source-capture-to-release",
            "broader-release-packet-preservation-and-publication",
            "three-scheduled-cycles-including-change-and-failure-recovery",
            "external-software-research-object-validation",
            "isolated-clean-room-subagent-reproduction",
            "release-specific-authority-and-stable-elapsed-periods",
        ],
        "non_claims": [
            "No mixed catalogue or website payload publication is asserted.",
            "No current source health, legal valid time or operative planning status is asserted.",
            "No whole-track, alpha-cycle or stable-release qualification is asserted.",
            "This Tasman disposition does not alter other source packets or historical "
            "technical-preview preservation receipts.",
            "The four historical-baseline dispositions retain the original manual/no-difference "
            "acceptance; the latest observed scheduled packet is separately identified.",
            "One scheduled source run is observed; the two ledger source runs include the earlier "
            "manual source and do not satisfy the three-cycle gate.",
            "All 3655 projected attribute digests differ from the fixed baseline; their cause is "
            "unattributed and no adjacent-cycle source-change qualification is asserted.",
        ],
    }


def scheduled_archive_projection(
    document: dict[str, Any], baseline_source: dict[str, Any], baseline_derived: dict[str, Any]
) -> dict[str, Any]:
    """Bind the additional observation without reinterpreting the historical baseline."""

    def check(condition: bool) -> None:
        if not condition:
            raise ValueError("scheduled archive acceptance semantic mismatch")

    check(document["schema_version"] == "1.0.0")
    check(document["track"] == "nz_spatial_archive_mvp_20260718")
    check(document["status"] == "first-scheduled-capture-and-automatic-publication-observed")
    receipts = document["receipts"]
    for item in (*receipts.values(), document["preservation"]):
        check(
            sha256_bytes((json.dumps(item["receipt"], indent=2) + "\n").encode()) == item["sha256"]
        )
    s, d, p = (receipts[key]["receipt"] for key in ("source", "derived", "provenance"))
    preservation = document["preservation"]["receipt"]
    comparison = document["comparison_summary"]
    qualification = document["qualification"]
    check(s["status"] == "public-packet-verified-and-rebuilt")
    check(d["status"] == "derivatives-published-and-verified")
    check(s["state"] == d["state"] == "verified")
    check(s["source_id"] == baseline_source["source_id"])
    check(d["logical_sha256"] == sha256_json(d["identity"]))
    check(s["anonymous_full_packet_verified"] is True)
    check(s["reproduction"]["builds"] == 2)
    check(s["reproduction"]["feature_count"] == d["identity"]["feature_count"] == 3655)
    check(d["identity"]["source_revision"] == s["public_revision"])
    check(d["identity"]["source_manifest_sha256"] == s["packet_manifest_sha256"])
    check(d["identity"]["geoparquet_sha256"] == s["reproduction"]["geoparquet_sha256"])
    for key in ("licence", "attribution"):
        check(s[key] == d[key] == baseline_source[key])
    repository = baseline_source["public_dataset_repository"]
    check(s["public_dataset_repository"] == d["public_repository"] == repository)
    check(p["source_public_revision"] == s["public_revision"])
    check(p["derived_public_revision"] == d["public_revision"])
    check(p["source_packet_manifest_sha256"] == s["packet_manifest_sha256"])
    check(p["derived_logical_sha256"] == d["logical_sha256"])
    for name in ("source", "derived"):
        check(p[f"{name}_receipt_sha256"] == receipts[name]["sha256"])
    for name, execution_name, event in (
        ("source_capture", "source_execution", "schedule"),
        ("source_trigger", "source_execution", "schedule"),
        ("publication", "publication_execution", "workflow_run"),
    ):
        execution = document[execution_name]
        check(p[name]["run_id"] == execution["run_id"])
        check(p[name]["attempt"] == str(execution["attempt"]))
        check(p[name]["code_sha"] == document["producer_revision"])
        check(p[name]["event"] == execution["event"] == event)
        check(execution["conclusion"] == "success")
    check(p["cycle_key"] == p["source_capture"]["run_id"] == s["source_run"])
    check(p["automatic_followup"] is True and p["scheduled_source_trigger_observed"] is True)
    check(p["release_cycle_qualified"] is False)
    check(p["publication_job_completion_claimed"] is False)
    check(p["change_recovery"] == "not-evaluated")
    check(preservation["status"] == "verified")
    check(preservation["source_run"] == s["source_run"])
    check(preservation["publication"] == p["publication"])
    check(preservation["public_repository"] == comparison["public_repository"] == repository)
    check(preservation["public_revision"] == comparison["public_revision"])
    for name in ("source", "derived", "provenance"):
        check(preservation["receipt_sha256"][name] == receipts[name]["sha256"])
    check(preservation["receipt_sha256"]["comparison"] == comparison["receipt_sha256"])
    check(
        comparison["receipt_path"]
        == "operational/tasman-cycle-ledger/v1/receipts/" + comparison["receipt_sha256"] + ".json"
    )
    check(
        comparison["before"]["canonical_sha256"]
        == baseline_derived["files"]["canonical.json"]["sha256"]
    )
    check(comparison["after"]["canonical_sha256"] == d["files"]["canonical.json"]["sha256"])
    check(comparison["baseline_role"] == "fixed-initial-accepted-packet-not-previous-cycle")
    check(comparison["diagnostic_status"] == "projected-attribute-differences-unattributed")
    check(
        comparison["difference_counts"]
        == {
            "added": 0,
            "removed": 0,
            "attribute_changed": 3655,
            "geometry_changed": 0,
        }
    )
    check(qualification["scheduled_source_runs_observed"] == [s["source_run"]])
    check(
        qualification["ledger_distinct_source_run_count"] == preservation["source_run_count"] == 2
    )
    check(preservation["three_cycle_gate_qualified"] is False)
    for key in (
        "three_cycle_gate_qualified",
        "adjacent_cycle_change_qualified",
        "hosted_outage_recovery_qualified",
    ):
        check(qualification[key] is False)
    return {
        "status": "accepted-first-scheduled-observation",
        "role": "latest-observed-scheduled-packet",
        "evidence": ARCHIVE_RECEIPTS[4],
        "source_run": s["source_run"],
        "publication_run": p["publication"]["run_id"],
        "source_public_revision": s["public_revision"],
        "derived_public_revision": d["public_revision"],
        "ledger_public_revision": preservation["public_revision"],
        "scheduled_source_runs_observed": qualification["scheduled_source_runs_observed"],
        "ledger_distinct_source_run_count": preservation["source_run_count"],
        "comparison_basis": comparison["baseline_role"],
        "difference_counts": comparison["difference_counts"],
        "difference_cause": "unattributed",
        "three_cycle_gate_qualified": False,
    }


def markdown(value: dict[str, Any]) -> str:
    counts = value["task_totals"]
    lines = [
        "# Repository progress",
        "",
        "Conductor integrity: passed.",
        "",
        f"Tasks: {counts['completed']}/{counts['total']} complete; "
        f"{counts['in_progress']} underway; {counts['pending']} pending.",
        "",
        "| Track | Status | Maturity | Completed / total |",
        "|---|---|---|---:|",
    ]
    for track in value["tracks"]:
        tasks = track["tasks"]
        lines.append(
            f"| {track['track_id']} | {track['status']} | {track['maturity']} | "
            f"{tasks['completed']} / {tasks['total']} |"
        )
    lines += ["", "## Release qualification", ""]
    for release in value["release_readiness"]["releases"]:
        lines.append(
            f"- {release['version']}: {release['qualified_tracks']}/"
            f"{release['required_tracks']} tracks; {release['passed_gates']}/"
            f"{release['required_gates']} gates; ready={release['ready']}."
        )
    lines += [
        "",
        f"Next package: {value['next_work_package'] or 'none'}.",
        "",
        "See JSON output for current tasks, evidence bindings and individual blockers.",
        "",
    ]
    lines += [f"- {claim}" for claim in value["non_claims"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    try:
        value = report(args.root)
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(json.dumps({"status": "invalid", "error_class": type(error).__name__}))
        return 1
    print(
        json.dumps(value, indent=2, sort_keys=True) if args.format == "json" else markdown(value),
        end="\n" if args.format == "json" else "",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
