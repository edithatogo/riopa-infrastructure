from __future__ import annotations

import json
from pathlib import Path

import scripts.codex_orchestrator as orchestrator


def test_queue_is_ordered_and_unique() -> None:
    queue = orchestrator.load_queue()
    assert queue[0].identifier == "WP-001"
    assert len({item.identifier for item in queue}) == len(queue)
    assert all(item.tracks for item in queue)
    assert all(item.acceptance for item in queue)


def test_active_package_takes_precedence() -> None:
    queue = orchestrator.load_queue()
    state = {
        "packages": {
            "WP-001": {"status": "complete"},
            "WP-003": {"status": "active"},
        }
    }
    selected = orchestrator.choose_next(queue, state)
    assert selected is not None
    assert selected.identifier == "WP-003"


def test_next_skips_complete_and_blocked_packages() -> None:
    queue = orchestrator.load_queue()
    state = {
        "packages": {
            "WP-001": {"status": "complete"},
            "WP-002": {"status": "blocked"},
        }
    }
    selected = orchestrator.choose_next(queue, state)
    assert selected is not None
    assert selected.identifier == "WP-003"


def test_local_state_mutation_does_not_change_conductor(tmp_path: Path, monkeypatch) -> None:
    local_dir = tmp_path / ".riopa-local" / "codex"
    monkeypatch.setattr(orchestrator, "LOCAL_DIR", local_dir)
    monkeypatch.setattr(orchestrator, "STATE_PATH", local_dir / "state.json")
    monkeypatch.setattr(orchestrator, "NEXT_PATH", local_dir / "NEXT_WORK_PACKAGE.md")

    assert orchestrator.mutate_command("WP-001", "active", "focused slice") == 0
    state = json.loads((local_dir / "state.json").read_text(encoding="utf-8"))
    assert state["packages"]["WP-001"]["status"] == "active"
    assert state["packages"]["WP-001"]["note"] == "focused slice"


def test_rendered_packet_contains_evidence_contract() -> None:
    item = orchestrator.load_queue()[0]
    rendered = orchestrator.render_work_packet(item, "pending")
    assert item.identifier in rendered
    assert "Acceptance criteria" in rendered
    assert "record evidence" in rendered
    assert all(track in rendered for track in item.tracks)


def test_terminal_next_replaces_stale_packet(tmp_path: Path, monkeypatch) -> None:
    queue = orchestrator.load_queue()
    state = {
        "packages": {
            item.identifier: {"status": "blocked" if item.identifier == "WP-006" else "complete"}
            for item in queue
        }
    }
    local_dir = tmp_path / ".riopa-local" / "codex"
    next_path = local_dir / "NEXT_WORK_PACKAGE.md"
    local_dir.mkdir(parents=True)
    next_path.write_text("stale executable packet\n", encoding="utf-8")
    monkeypatch.setattr(orchestrator, "ROOT", tmp_path)
    monkeypatch.setattr(orchestrator, "LOCAL_DIR", local_dir)
    monkeypatch.setattr(orchestrator, "NEXT_PATH", next_path)

    assert orchestrator.next_command(queue, state, write=True) == 0
    rendered = next_path.read_text(encoding="utf-8")
    assert rendered.startswith("# No unblocked Codex work package")
    assert "stale executable packet" not in rendered
    assert "Complete: 9" in rendered
    assert "Blocked: 1" in rendered
    assert "`WP-006`" in rendered
    assert "Do not execute an earlier packet" in rendered
