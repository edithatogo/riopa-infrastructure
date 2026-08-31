#!/usr/bin/env python3
"""Local, non-authoritative work-package orchestrator for Codex handoffs.

The Conductor records remain the programme source of truth. This helper creates a
machine-local continuation packet without changing track maturity or GitHub state.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "codex" / "implementation-queue.json"
LOCAL_DIR = ROOT / ".riopa-local" / "codex"
STATE_PATH = LOCAL_DIR / "state.json"
NEXT_PATH = LOCAL_DIR / "NEXT_WORK_PACKAGE.md"


@dataclass(frozen=True)
class WorkPackage:
    identifier: str
    title: str
    priority: str
    tracks: tuple[str, ...]
    acceptance: tuple[str, ...]
    commands: tuple[str, ...]
    requires: tuple[str, ...]
    reconciliation: str | None = None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> WorkPackage:
        return cls(
            identifier=str(value["id"]),
            title=str(value["title"]),
            priority=str(value["priority"]),
            tracks=tuple(str(item) for item in value.get("tracks", [])),
            acceptance=tuple(str(item) for item in value.get("acceptance", [])),
            commands=tuple(str(item) for item in value.get("commands", [])),
            requires=tuple(str(item) for item in value.get("requires", [])),
        )


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected an object in {path}")
    return loaded


def load_queue(*, root: Path | None = None) -> list[WorkPackage]:
    payload = _load_json(QUEUE_PATH if root is None else root / "codex/implementation-queue.json")
    raw = payload.get("packages")
    if not isinstance(raw, list) or not raw:
        raise ValueError("Implementation queue must contain a non-empty packages list")
    if any(not isinstance(item, dict) for item in raw):
        raise ValueError("Implementation queue entries must be objects")
    reference = payload.get("repository_reconciliation")
    if reference is not None and (not isinstance(reference, str) or not reference):
        raise ValueError("Invalid repository reconciliation reference")
    packages = [replace(WorkPackage.from_mapping(item), reconciliation=reference) for item in raw]
    identifiers = [item.identifier for item in packages]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Implementation queue contains duplicate package identifiers")
    return packages


def load_local_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"schema_version": "1.0.0", "packages": {}}
    state = _load_json(STATE_PATH)
    if not isinstance(state.get("packages", {}), dict):
        raise ValueError("Local Codex state packages must be an object")
    return state


def _evidence_path(root: Path, reference: str) -> Path:
    path = Path(reference)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("Evidence must be a repository-relative path")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
        raise ValueError("Evidence is missing or outside the repository")
    return resolved


def reconcile_state(
    queue: list[WorkPackage], local_state: dict[str, Any], *, root: Path | None = None
) -> dict[str, Any]:
    """Combine verified portable evidence and optional legacy local routing overrides.

    Completion here is bounded implementation, never track or release qualification.
    Pass raw local state, not an earlier reconciled view; the input is not mutated.
    """
    root = ROOT if root is None else root
    local = local_state.get("packages", {})
    if not isinstance(local, dict):
        raise ValueError("Local Codex state packages must be an object")
    references = {item.reconciliation for item in queue}
    if len(references) > 1:
        raise ValueError("Queue has inconsistent reconciliation references")
    reference = next(iter(references), None)
    baseline: dict[str, Any] = {}
    if reference is not None:
        document = _load_json(_evidence_path(root, reference))
        baseline = document.get("packages", {})
        if document.get("schema_version") != "1.0.0" or not isinstance(baseline, dict):
            raise ValueError("Invalid reconciliation schema")
        if set(baseline) != {item.identifier for item in queue}:
            raise ValueError("Reconciliation must cover exactly the configured packages")
    result = copy.deepcopy(local_state)
    result["packages"] = {}
    for item in queue:
        entry = copy.deepcopy(baseline.get(item.identifier, {}))
        if not isinstance(entry, dict):
            raise ValueError("Reconciliation package must be an object")
        implementation = entry.get("repository_implementation_status", "pending")
        if not isinstance(implementation, str) or implementation not in {
            "pending",
            "partial",
            "complete",
        }:
            raise ValueError("Invalid repository implementation status")
        if reference is not None:
            if entry.get("qualification_status") != "pending":
                raise ValueError("This reconciliation cannot qualify tracks or releases")
            for field in ("scope", "remaining_work"):
                if not isinstance(entry.get(field), str) or not entry[field].strip():
                    raise ValueError(f"Reconciliation requires {field}")
            evidence = entry.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                raise ValueError("Reconciliation requires evidence")
            for binding in evidence:
                if not isinstance(binding, dict) or not isinstance(binding.get("path"), str):
                    raise ValueError("Malformed evidence binding")
                path = _evidence_path(root, binding["path"])
                if hashlib.sha256(path.read_bytes()).hexdigest() != binding.get("sha256"):
                    raise ValueError("Evidence digest mismatch")
                _load_json(path)
        override = local.get(item.identifier, {})
        if not isinstance(override, dict):
            raise ValueError("Local package must be an object")
        status = override.get("status", implementation)
        if not isinstance(status, str) or status not in {
            "pending",
            "partial",
            "active",
            "complete",
            "blocked",
        }:
            raise ValueError("Invalid local routing status")
        entry.update({key: override[key] for key in ("note", "updated_at") if key in override})
        entry.update(
            status=status,
            status_origin="local-override" if "status" in override else "repository-evidence",
            repository_implementation_status=implementation,
            qualification_status="pending",
        )
        result["packages"][item.identifier] = entry
    return result


def load_state() -> dict[str, Any]:
    return reconcile_state(load_queue(), load_local_state())


def save_state(state: dict[str, Any]) -> None:
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.now(UTC).isoformat()
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def package_state(state: dict[str, Any], identifier: str) -> str:
    packages = state.get("packages", {})
    value = packages.get(identifier, {}) if isinstance(packages, dict) else {}
    return str(value.get("status", "pending")) if isinstance(value, dict) else "pending"


def choose_next(queue: list[WorkPackage], state: dict[str, Any]) -> WorkPackage | None:
    active = [item for item in queue if package_state(state, item.identifier) == "active"]
    if active:
        return active[0]
    return next(
        (
            item
            for item in queue
            if package_state(state, item.identifier) not in {"complete", "blocked"}
        ),
        None,
    )


def render_work_packet(
    item: WorkPackage, status: str, progress: dict[str, Any] | None = None
) -> str:
    lines = [
        f"# Next Codex work package — {item.identifier}",
        "",
        f"**Title:** {item.title}",
        f"**Priority:** {item.priority}",
        f"**Routing status:** {status}",
        "",
        "## Conductor tracks",
        "",
    ]
    if progress:
        lines[7:7] = [
            f"Repository implementation: {progress['repository_implementation_status']}",
            f"Qualification: {progress['qualification_status']} (no track/release promotion)",
            f"Scope: {progress.get('scope', 'No portable evidence recorded')}",
            f"Remaining: {progress.get('remaining_work', 'Reconcile mapped track evidence')}",
            "",
        ]
    lines.extend(f"- `{track}`" for track in item.tracks)
    if item.requires:
        lines.extend(["", "## External prerequisites", ""])
        lines.extend(f"- {requirement}" for requirement in item.requires)
    lines.extend(["", "## Acceptance criteria", ""])
    lines.extend(f"- [ ] {criterion}" for criterion in item.acceptance)
    if item.commands:
        lines.extend(["", "## Baseline commands", "", "```bash"])
        lines.extend(item.commands)
        lines.append("```")
    lines.extend(
        [
            "",
            "## Execution rule",
            "",
            "Read the mapped track specifications and live issue state, choose a bounded "
            "vertical slice, implement and test it, record evidence, commit and push "
            "normally, update the local package state, then continue to the next "
            "unblocked package.",
            "",
        ]
    )
    return "\n".join(lines)


def render_terminal_packet(queue: list[WorkPackage], state: dict[str, Any]) -> str:
    """Render a fail-closed packet when no configured package can be selected."""

    complete = [item for item in queue if package_state(state, item.identifier) == "complete"]
    blocked = [item for item in queue if package_state(state, item.identifier) == "blocked"]
    unavailable = len(queue) - len(complete) - len(blocked)
    lines = [
        "# No unblocked Codex work package",
        "",
        "All configured work packages are complete or blocked. This terminal packet",
        "replaces any earlier next-work packet so stale instructions cannot be mistaken",
        "for an executable assignment.",
        "Routing completion does not qualify mapped tracks or a release.",
        "",
        "## Status summary",
        "",
        f"- Complete: {len(complete)}",
        f"- Blocked: {len(blocked)}",
        f"- Other selectable states: {unavailable}",
    ]
    if blocked:
        lines.extend(["", "## Blocked packages", ""])
        lines.extend(f"- `{item.identifier}` — {item.title}" for item in blocked)
    lines.extend(
        [
            "",
            "## Continuation rule",
            "",
            "Do not execute an earlier packet. Reconcile the blocking evidence against",
            "the current Conductor tracks, or add an explicitly authorised work package",
            "before continuing.",
            "",
        ]
    )
    return "\n".join(lines)


def status_command(queue: list[WorkPackage], state: dict[str, Any]) -> int:
    for item in queue:
        state_name = package_state(state, item.identifier)
        entry = state.get("packages", {}).get(item.identifier, {})
        implementation = entry.get("repository_implementation_status", "unreconciled")
        print(
            f"{item.identifier}\t{item.priority}\t{state_name}\t"
            f"repository={implementation}\tqualification=pending\t{item.title}"
        )
    return 0


def next_command(queue: list[WorkPackage], state: dict[str, Any], *, write: bool) -> int:
    item = choose_next(queue, state)
    if item is None:
        print("All work packages are complete or blocked.")
        if write:
            LOCAL_DIR.mkdir(parents=True, exist_ok=True)
            NEXT_PATH.write_text(render_terminal_packet(queue, state), encoding="utf-8")
            print(NEXT_PATH.relative_to(ROOT))
        return 0
    entry = state.get("packages", {}).get(item.identifier, {})
    progress = entry if "repository_implementation_status" in entry else None
    text = render_work_packet(item, package_state(state, item.identifier), progress)
    if write:
        LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        NEXT_PATH.write_text(text, encoding="utf-8")
        print(NEXT_PATH.relative_to(ROOT))
    else:
        print(text)
    return 0


def mutate_command(identifier: str, new_status: str, note: str | None) -> int:
    queue = load_queue()
    known = {item.identifier for item in queue}
    if identifier not in known:
        raise ValueError(f"Unknown work package: {identifier}")
    state = load_local_state()
    packages = state.setdefault("packages", {})
    if not isinstance(packages, dict):
        raise ValueError("Local Codex state packages must be an object")
    entry = packages.setdefault(identifier, {})
    if not isinstance(entry, dict):
        entry = {}
        packages[identifier] = entry
    entry["status"] = new_status
    entry["updated_at"] = datetime.now(UTC).isoformat()
    if note:
        entry["note"] = note
    save_state(state)
    print(f"{identifier}: {new_status}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    next_parser = sub.add_parser("next")
    next_parser.add_argument("--write", action="store_true")
    for name in ("start", "complete", "block", "reset"):
        item = sub.add_parser(name)
        item.add_argument("identifier")
        item.add_argument("--note")
    return result


def main() -> int:
    args = parser().parse_args()
    queue = load_queue()
    state = load_state()
    if args.command == "status":
        return status_command(queue, state)
    if args.command == "next":
        return next_command(queue, state, write=bool(args.write))
    statuses = {"start": "active", "complete": "complete", "block": "blocked", "reset": "pending"}
    return mutate_command(args.identifier, statuses[args.command], args.note)


if __name__ == "__main__":
    raise SystemExit(main())
