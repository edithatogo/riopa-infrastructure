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

from riopa_provenance.hashing import sha256_file
from riopa_provenance.roadmap import roadmap_status, validate_roadmap

ROOT = Path(__file__).resolve().parents[1]


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
    for reference in references:
        relative = reference["path"]
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
        if not path.is_file() or sha256_file(path) != reference["sha256"]:
            raise ValueError("archive evidence digest mismatch")
    for disposition in archive["dispositions"].values():
        if disposition["evidence"] not in paths:
            raise ValueError("unbound archive disposition")


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
