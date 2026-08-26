from __future__ import annotations

import json
import shutil
from pathlib import Path

from riopa_provenance.roadmap import (
    generate_issue_configuration,
    release_readiness,
    roadmap_status,
    validate_roadmap,
)

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> object:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def copy_roadmap(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for name in ("conductor", "schemas", "project"):
        shutil.copytree(ROOT / name, root / name)
    return root


def test_complete_roadmap_validates_without_drift() -> None:
    assert validate_roadmap(ROOT) == ()


def test_stable_v1_model_has_full_scope_and_dimensions() -> None:
    maturity = load("conductor/maturity-model.json")
    releases = load("conductor/releases.json")
    gate = load("conductor/v1-gate.json")
    assert isinstance(maturity, dict)
    assert isinstance(releases, dict)
    assert isinstance(gate, dict)

    assert [item["id"] for item in maturity["levels"]] == [f"M{i}" for i in range(7)]
    dimensions = {item["id"] for item in maturity["dimensions"]}
    assert len(dimensions) == 12

    tracks = {
        json.loads(path.read_text(encoding="utf-8"))["track_id"]
        for path in (ROOT / "conductor/tracks").glob("*/metadata.json")
    }
    assert len(tracks) == 28
    assert {
        json.loads(path.read_text(encoding="utf-8"))["maturity_target"]
        for path in (ROOT / "conductor/tracks").glob("*/metadata.json")
    } == {"M6"}

    stable = next(item for item in releases["releases"] if item["version"] == "1.0.0")
    assert stable["maturity_level"] == "M6"
    assert set(stable["required_tracks"]) == tracks
    assert dimensions <= {item["category"] for item in stable["exit_gates"]}
    assert set(gate["required_tracks"]) == tracks
    assert set(gate["required_dimensions"]) == dimensions
    assert set(gate["required_gate_ids"]) == {item["id"] for item in stable["exit_gates"]}


def test_generated_issue_graph_covers_all_tracks_and_phases() -> None:
    config = generate_issue_configuration(ROOT)
    issues = config["issues"]
    assert config["version"] == 3
    assert len([item for item in issues if item.get("parent") == "program-epic"]) == 28
    assert not any(
        item.get("track_id") == "bounded_roadmap_technical_preview_release_20260826"
        for item in issues
    )
    assert len([item for item in issues if ":phase-" in item["key"]]) >= 112
    assert len({item["key"] for item in issues}) == len(issues)


def test_current_development_release_is_blocked_but_stable_is_not() -> None:
    status = roadmap_status(ROOT)
    assert status["tracks"]["total"] == 29
    assert status["tracks"]["by_current_maturity"] == {"M1": 25, "M2": 4}
    assert status["releases"][0]["ready"] is False
    assert status["releases"][0]["blockers"]
    assert all(not release["ready"] for release in status["releases"][1:])

    stable = release_readiness(ROOT, "1.0.0")
    assert not stable.ready
    assert stable.required_tracks == 28
    assert stable.qualified_tracks == 0
    assert any("M6 is required" in blocker for blocker in stable.blockers)
    assert any("stable release evidence record is absent" in blocker for blocker in stable.blockers)


def test_validator_detects_missing_stable_dimension_gate(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    releases_path = root / "conductor/releases.json"
    releases = json.loads(releases_path.read_text(encoding="utf-8"))
    stable = next(item for item in releases["releases"] if item["version"] == "1.0.0")
    stable["exit_gates"] = [
        item for item in stable["exit_gates"] if item["category"] != "performance"
    ]
    releases_path.write_text(json.dumps(releases, indent=2) + "\n", encoding="utf-8")

    problems = validate_roadmap(root, check_generated_issues=False)
    assert any(problem.code == "v1-dimension-gates" for problem in problems)
    assert any(problem.code == "v1-gate-ids" for problem in problems)


def test_validator_detects_issue_drift(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    issue_path = root / "project/issues.yaml"
    issues = json.loads(issue_path.read_text(encoding="utf-8"))
    issues["issues"][0]["title"] = "drifted"
    issue_path.write_text(json.dumps(issues, indent=2) + "\n", encoding="utf-8")
    problems = validate_roadmap(root)
    assert any(problem.code == "issue-drift" for problem in problems)
