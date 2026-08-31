from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

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


def portable_fixture(tmp_path: Path):
    queue = [replace(orchestrator.load_queue()[0], reconciliation="reconciliation.json")]
    evidence = tmp_path / "evidence.json"
    evidence.write_text('{"status":"bounded-evidence"}\n')
    entry = {
        "repository_implementation_status": "partial",
        "qualification_status": "pending",
        "scope": "bounded implementation",
        "remaining_work": "broader acceptance",
        "evidence": [
            {"path": evidence.name, "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest()}
        ],
    }
    document = {"schema_version": "1.0.0", "packages": {"WP-001": entry}}
    (tmp_path / "reconciliation.json").write_text(json.dumps(document))
    return queue, document


def test_fresh_worktree_has_evidenced_status_and_sensible_next() -> None:
    queue = orchestrator.load_queue()
    state = orchestrator.reconcile_state(queue, {"packages": {}})
    assert state["packages"]["WP-001"]["status"] == "complete"
    assert state["packages"]["WP-002"]["status"] == "complete"
    assert state["packages"]["WP-006"]["status"] == "partial"
    assert state["packages"]["WP-010"]["status"] == "complete"
    assert all(v["qualification_status"] == "pending" for v in state["packages"].values())
    selected = orchestrator.choose_next(queue, state)
    assert selected is not None and selected.identifier == "WP-003"


@pytest.mark.parametrize("status", ["active", "blocked", "complete", "pending"])
def test_legacy_override_only_changes_routing(tmp_path: Path, status: str) -> None:
    queue, _ = portable_fixture(tmp_path)
    local = {"packages": {"WP-001": {"status": status, "note": "legacy"}}}
    state = orchestrator.reconcile_state(queue, local, root=tmp_path)
    entry = state["packages"]["WP-001"]
    assert entry["status"] == status
    assert entry["status_origin"] == "local-override"
    assert entry["repository_implementation_status"] == "partial"
    assert entry["qualification_status"] == "pending"
    assert local == {"packages": {"WP-001": {"status": status, "note": "legacy"}}}


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "malformed",
        "schema",
        "coverage",
        "entry",
        "implementation",
        "qualification",
        "scope",
        "remaining_work",
        "empty_evidence",
        "binding",
        "digest",
        "traversal",
        "absolute",
        "symlink",
        "invalid_json",
        "missing_evidence",
    ],
)
def test_invalid_portable_evidence_fails_closed(tmp_path: Path, fault: str) -> None:
    queue, document = portable_fixture(tmp_path)
    entry = document["packages"]["WP-001"]
    binding = entry["evidence"][0]
    path = tmp_path / "reconciliation.json"
    if fault == "missing":
        queue = [replace(queue[0], reconciliation="missing.json")]
    elif fault == "malformed":
        document = []
    elif fault == "schema":
        document["schema_version"] = "2"
    elif fault == "coverage":
        document["packages"] = {}
    elif fault == "entry":
        document["packages"]["WP-001"] = []
    elif fault == "implementation":
        entry["repository_implementation_status"] = []
    elif fault == "qualification":
        entry["qualification_status"] = "complete"
    elif fault in {"scope", "remaining_work"}:
        entry[fault] = ""
    elif fault == "empty_evidence":
        entry["evidence"] = []
    elif fault == "binding":
        entry["evidence"] = ["not an object"]
    elif fault == "digest":
        binding["sha256"] = "0" * 64
    elif fault == "traversal":
        binding["path"] = "../evidence.json"
    elif fault == "absolute":
        binding["path"] = str(tmp_path / "evidence.json")
    elif fault == "symlink":
        (tmp_path / "outside").symlink_to(tmp_path.parent, target_is_directory=True)
        binding["path"] = "outside/evidence.json"
    elif fault == "invalid_json":
        (tmp_path / "evidence.json").write_text("[]")
        binding["sha256"] = hashlib.sha256(b"[]").hexdigest()
    elif fault == "missing_evidence":
        binding["path"] = "absent.json"
    path.write_text(json.dumps(document))
    with pytest.raises(ValueError):
        orchestrator.reconcile_state(queue, {"packages": {}}, root=tmp_path)


def test_old_queue_without_reconciliation_still_works(tmp_path: Path) -> None:
    queue, _ = portable_fixture(tmp_path)
    queue = [replace(queue[0], reconciliation=None)]
    state = orchestrator.reconcile_state(queue, {}, root=tmp_path)
    assert state["packages"]["WP-001"]["status"] == "pending"


@pytest.mark.parametrize(
    "local",
    [{"packages": []}, {"packages": {"WP-001": []}}, {"packages": {"WP-001": {"status": []}}}],
)
def test_malformed_local_state_rejected(tmp_path: Path, local) -> None:
    queue, _ = portable_fixture(tmp_path)
    with pytest.raises(ValueError):
        orchestrator.reconcile_state(queue, local, root=tmp_path)


def test_local_mutation_never_persists_inherited_status(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(orchestrator, "LOCAL_DIR", tmp_path)
    monkeypatch.setattr(orchestrator, "STATE_PATH", tmp_path / "state.json")
    orchestrator.mutate_command("WP-003", "active", None)
    persisted = json.loads((tmp_path / "state.json").read_text())
    assert set(persisted["packages"]) == {"WP-003"}
    reconciled = orchestrator.load_state()
    assert reconciled["packages"]["WP-001"]["status"] == "complete"
    assert reconciled["packages"]["WP-003"]["status"] == "active"


def test_next_packet_explains_remaining_scope(tmp_path: Path, capsys) -> None:
    queue, _ = portable_fixture(tmp_path)
    state = orchestrator.reconcile_state(queue, {}, root=tmp_path)
    orchestrator.next_command(queue, state, write=False)
    text = capsys.readouterr().out
    assert "Repository implementation: partial" in text
    assert "broader acceptance" in text
    assert "no track/release promotion" in text


def test_root_aware_queue_and_malformed_entries(tmp_path: Path) -> None:
    queue_path = tmp_path / "codex/implementation-queue.json"
    queue_path.parent.mkdir()
    queue_path.write_text('{"packages":[null]}')
    with pytest.raises(ValueError, match="entries"):
        orchestrator.load_queue(root=tmp_path)
    raw = json.loads(orchestrator.QUEUE_PATH.read_text())
    raw["repository_reconciliation"] = []
    queue_path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="reference"):
        orchestrator.load_queue(root=tmp_path)
