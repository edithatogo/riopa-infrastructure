from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_conductor_dependency_graph_is_complete_and_acyclic() -> None:
    metadata_files = sorted((ROOT / "conductor/tracks").glob("*/metadata.json"))
    metadata = [json.loads(path.read_text(encoding="utf-8")) for path in metadata_files]
    ids = {item["track_id"] for item in metadata}
    assert len(ids) == 27

    dependencies = {
        item["track_id"]: set(item.get("depends_on", item.get("depends", []))) for item in metadata
    }
    for track_id, required in dependencies.items():
        assert required <= ids, f"{track_id} has unknown dependencies: {required - ids}"

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(track_id: str) -> None:
        assert track_id not in visiting, f"dependency cycle at {track_id}"
        if track_id in visited:
            return
        visiting.add(track_id)
        for dependency in dependencies[track_id]:
            visit(dependency)
        visiting.remove(track_id)
        visited.add(track_id)

    for track_id in ids:
        visit(track_id)


def test_issue_graph_references_valid_keys_and_all_tracks() -> None:
    issue_config = load("project/issues.yaml")
    assert isinstance(issue_config, dict)
    issues = issue_config["issues"]
    keys = [item["key"] for item in issues]
    assert len(keys) == len(set(keys))
    key_set = set(keys)

    for item in issues:
        parent = item.get("parent")
        if parent:
            assert parent in key_set
        for dependency in item.get("blocked_by", []):
            assert dependency in key_set

    track_ids = {
        json.loads(path.read_text(encoding="utf-8"))["track_id"]
        for path in (ROOT / "conductor/tracks").glob("*/metadata.json")
    }
    issue_track_ids = {
        item["key"]
        for item in issues
        if item["key"] in track_ids and item.get("parent") == "program-epic"
    }
    assert issue_track_ids == track_ids


def test_cross_repository_issue_keys_and_targets_are_unique() -> None:
    config = load("project/cross-repo-adoption.yaml")
    assert isinstance(config, dict)
    issues = config["issues"]
    keys = [item["key"] for item in issues]
    targets = [(item["repository"], item["title"]) for item in issues]
    assert len(keys) == len(set(keys))
    assert len(targets) == len(set(targets))
    assert len(issues) >= 8


def test_every_configured_label_has_a_definition() -> None:
    labels = load("project/labels.yaml")
    issues = load("project/issues.yaml")
    cross = load("project/cross-repo-adoption.yaml")
    assert isinstance(labels, list)
    known = {item["name"] for item in labels}
    used = {
        label
        for config in (issues, cross)
        for item in config["issues"]
        for label in item.get("labels", [])
    }
    assert used <= known
