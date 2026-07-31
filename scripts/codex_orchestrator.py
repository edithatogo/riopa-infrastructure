#!/usr/bin/env python3
"""Local, non-authoritative work-package orchestrator for Codex handoffs.

The Conductor records remain the programme source of truth. This helper creates a
machine-local continuation packet without changing track maturity or GitHub state.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
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


def load_queue() -> list[WorkPackage]:
    payload = _load_json(QUEUE_PATH)
    raw = payload.get("packages")
    if not isinstance(raw, list) or not raw:
        raise ValueError("Implementation queue must contain a non-empty packages list")
    packages = [WorkPackage.from_mapping(item) for item in raw if isinstance(item, dict)]
    identifiers = [item.identifier for item in packages]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Implementation queue contains duplicate package identifiers")
    return packages


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {"schema_version": "1.0.0", "packages": {}}
    state = _load_json(STATE_PATH)
    if not isinstance(state.get("packages", {}), dict):
        raise ValueError("Local Codex state packages must be an object")
    return state


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


def render_work_packet(item: WorkPackage, status: str) -> str:
    lines = [
        f"# Next Codex work package — {item.identifier}",
        "",
        f"**Title:** {item.title}",
        f"**Priority:** {item.priority}",
        f"**Local status:** {status}",
        "",
        "## Conductor tracks",
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


def status_command(queue: list[WorkPackage], state: dict[str, Any]) -> int:
    for item in queue:
        state_name = package_state(state, item.identifier)
        print(f"{item.identifier}\t{item.priority}\t{state_name}\t{item.title}")
    return 0


def next_command(queue: list[WorkPackage], state: dict[str, Any], *, write: bool) -> int:
    item = choose_next(queue, state)
    if item is None:
        print("All work packages are complete or blocked.")
        return 0
    text = render_work_packet(item, package_state(state, item.identifier))
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
    state = load_state()
    packages = state.setdefault("packages", {})
    assert isinstance(packages, dict)
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
