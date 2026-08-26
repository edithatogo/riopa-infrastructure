from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from riopa_provenance.roadmap import (
    RoadmapProblem,
    _detect_cycle,
    _markdown_dependencies,
    _maturity_rank,
    _parse_datetime,
    _plan_phases,
    _risk_label,
    _section,
    _semver_key,
    _stability_label,
    _validate_evidence_reference,
    _validate_release_evidence,
    _waiver_is_current,
    generate_issue_configuration,
    load_tracks,
    release_readiness,
    render_status_markdown,
    roadmap_status,
    validate_roadmap,
    write_issue_configuration,
)

ROOT = Path(__file__).resolve().parents[1]
FIRST_TRACK = "foundation_architecture_20260718"
HARDENING_TRACK = "v1_release_hardening_20260719"


def copy_roadmap(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for name in ("conductor", "schemas", "project", "docs"):
        shutil.copytree(ROOT / name, root / name)
    evidence_dir = root / "conductor/release-evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for path in evidence_dir.glob("*.json"):
        path.unlink()
    return root


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def track_metadata(root: Path, track_id: str = FIRST_TRACK) -> tuple[Path, dict[str, Any]]:
    path = root / "conductor/tracks" / track_id / "metadata.json"
    return path, read_json(path)


def codes(root: Path, *, issue_drift: bool = False) -> set[str]:
    return {item.code for item in validate_roadmap(root, check_generated_issues=issue_drift)}


def test_architecture_fitness_requires_boundary_contract(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    assert "architecture-artifact" not in codes(root)
    (root / "docs/v1-scope-and-boundaries.md").unlink()
    assert "architecture-artifact" in codes(root)


def test_v1_critical_track_requires_owner_and_maturity_metadata(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    path, metadata = track_metadata(root)
    metadata.pop("owner_repository")
    metadata.pop("maturity_target")
    write_json(path, metadata)
    problems = validate_roadmap(root, check_generated_issues=False)
    assert {item.code for item in problems} >= {"architecture-ownership"}
    messages = " ".join(item.message for item in problems)
    assert "missing owner_repository" in messages
    assert "missing maturity_target" in messages


def test_plan_phases_retain_completed_tasks() -> None:
    phases = _plan_phases("## 1. Done\n- [x] Completed\n## 2. Active\n- [~] In progress\n")
    assert [phase["tasks"] for phase in phases] == [["Completed"], ["In progress"]]


def test_archived_track_remains_discoverable_and_validates(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    source = root / "conductor/tracks" / FIRST_TRACK
    destination = root / "conductor/archive" / FIRST_TRACK
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(source, destination)

    metadata_path = destination / "metadata.json"
    metadata = read_json(metadata_path)
    metadata["status"] = "archived"
    metadata["current_maturity"] = metadata["maturity_target"]
    write_json(metadata_path, metadata)
    index_path = destination / "index.md"
    index = index_path.read_text(encoding="utf-8")
    index = index.replace("`validating`", "`archived`").replace("`M1`", "`M6`", 1)
    index_path.write_text(index, encoding="utf-8")

    tracks = load_tracks(root)
    assert tracks[FIRST_TRACK]["_collection"] == "archive"
    assert tracks[FIRST_TRACK]["_path"] == metadata_path.as_posix()
    issues = generate_issue_configuration(root)
    assert not any(item["key"] == FIRST_TRACK for item in issues["issues"])
    write_issue_configuration(root)
    assert validate_roadmap(root) == ()

    readiness = release_readiness(root, metadata["target_release"])
    assert not any(
        f"track {FIRST_TRACK} status archived is incompatible" in blocker
        for blocker in readiness.blockers
    )


def test_track_cannot_exist_in_active_and_archive_collections(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    archived = root / "conductor/archive" / FIRST_TRACK
    shutil.copytree(root / "conductor/tracks" / FIRST_TRACK, archived)

    with pytest.raises(ValueError, match=f"duplicate track id {FIRST_TRACK}"):
        load_tracks(root)


def iso(delta: timedelta = timedelta()) -> str:
    return (datetime.now(UTC) + delta).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evidence_ref(key: str, *, immutable: bool = True) -> dict[str, Any]:
    return {
        "evidence_id": f"urn:riopa:test:evidence:{key}",
        "kind": "test-report",
        "location": f"urn:riopa:test:evidence:{key}",
        "sha256": None,
        "immutable": immutable,
        "generated_at": iso(),
        "description": "Synthetic test evidence",
    }


def evidence_reference(name: str, *, immutable: bool = True) -> dict[str, Any]:
    digest = (name.encode("utf-8").hex() + "0" * 64)[:64]
    identifier = f"urn:sha256:{digest}"
    return {
        "evidence_id": identifier,
        "kind": "test-report",
        "location": identifier,
        "sha256": None,
        "immutable": immutable,
        "generated_at": iso(),
        "description": f"Synthetic qualification evidence for {name}.",
    }


def test_historical_evidence_uses_preserved_release_snapshot(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    live = root / "project/issues.yaml"
    live.parent.mkdir(parents=True)
    live.write_text("current issue graph\n", encoding="utf-8")
    snapshot = root / "conductor/release-evidence/artifacts/0.2.0" / "project/issues.yaml"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text("original issue graph\n", encoding="utf-8")
    reference = {
        "location": "project/issues.yaml",
        "sha256": "b0221eb9571ec0449b2ad0d295b429071ccb9534644238a1e7dba50470f40d2e",
    }
    problems: list[RoadmapProblem] = []

    _validate_evidence_reference(
        root,
        root / "conductor/release-evidence/0.2.0.json",
        reference,
        problems,
        release_version="0.2.0",
    )

    assert problems == []


def passing_gate(gate_id: str) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "status": "passed",
        "evidence": [evidence_reference(gate_id)],
        "reviewer": "Independent agent analyst",
        "reviewed_at": iso(),
        "expires_at": iso(timedelta(days=90)),
        "waiver": None,
        "notes": None,
    }


def stable_evidence(root: Path) -> dict[str, Any]:
    release_plan = read_json(root / "conductor/releases.json")
    stable = next(item for item in release_plan["releases"] if item["version"] == "1.0.0")
    gate_ids = [item["id"] for item in stable["exit_gates"] if item.get("blocking", True)]
    v1_gate = read_json(root / "conductor/v1-gate.json")
    metrics = {
        "agent_panel_analysts": 2,
        "clean_room_reproductions": 2,
        "external_reproductions": 1,
        "external_user_workflows": 2,
        "external_operator_workflows": 1,
        "operational_cycles": 3,
        "operational_evidence_days": 90,
        "release_candidate_soak_days": 30,
    }
    return {
        "schema_version": "1.0.0",
        "evidence_id": "urn:riopa:release-evidence:1.0.0:test",
        "release": "1.0.0",
        "evaluated_at": iso(),
        "evaluated_by": "RIOPA qualification workflow",
        "machine_readable": True,
        "immutable_evidence_identifiers": True,
        "source_revision": "swh:1:rev:0000000000000000000000000000000000000000",
        "tool": {
            "name": "riopa-provenance",
            "version": "1.0.0",
            "environment": "clean qualification environment",
        },
        "gates": [passing_gate(gate_id) for gate_id in gate_ids],
        "defects": {
            "open_p0": 0,
            "open_p1": 0,
            "release_blocking_p2": 0,
            "critical_security_findings": 0,
            "governance_prohibitions": 0,
            "expired_waivers": 0,
        },
        "metrics": metrics,
        "approvals": [
            {
                "role": role,
                "reviewer": f"Reviewer for {role}",
                "decision": "approve",
                "decided_at": iso(),
                "signed_decision_ref": f"urn:riopa:test:signature:{index}",
                "notes": None,
            }
            for index, role in enumerate(v1_gate["release_authority"]["required_roles"], start=1)
        ],
        "release_artifacts": [evidence_reference("stable-release-artifact")],
        "known_limitations": ["Synthetic qualification fixture for testing only."],
        "notes": "Synthetic qualification fixture for testing only.",
    }


def make_stable_ready(root: Path) -> dict[str, Any]:
    plan = read_json(root / "conductor/releases.json")
    stable = next(item for item in plan["releases"] if item["version"] == "1.0.0")
    for track_id in stable["required_tracks"]:
        path, metadata = track_metadata(root, track_id)
        metadata["status"] = "complete"
        metadata["current_maturity"] = "M6"
        metadata["evidence"] = [f"urn:riopa:test:track:{track_id}"]
        metadata["blocking_defects"] = []
        write_json(path, metadata)
    evidence = stable_evidence(root)
    evidence_path = root / "conductor/release-evidence/1.0.0.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(evidence_path, evidence)
    return evidence


def test_small_roadmap_primitives() -> None:
    assert str(RoadmapProblem("code", "where", "message")) == "code [where]: message"
    assert _semver_key("1.0.0-rc.2") < _semver_key("1.0.0")
    assert _semver_key("1.0.0-2") < _semver_key("1.0.0-alpha")
    with pytest.raises(ValueError, match="semantic version"):
        _semver_key("v1")
    assert _maturity_rank("M6") == 6
    with pytest.raises(ValueError, match="maturity"):
        _maturity_rank("stable")
    assert _parse_datetime("2026-07-19T00:00:00Z").tzinfo == UTC
    assert _parse_datetime("2026-07-19T00:00:00").tzinfo == UTC
    assert _detect_cycle({"a": {"b"}, "b": set()}) is None
    assert _detect_cycle({"a": {"b"}, "b": {"a"}}) == ["a", "b", "a"]
    markdown = "# X\n\n## Dependencies\n\n- `one`\n- `two`\n\n## Other\n"
    assert _section(markdown, "Dependencies").startswith("- `one`")
    assert _section(markdown, "Missing") == ""
    assert _markdown_dependencies(markdown) == {"one", "two"}
    phases = _plan_phases("## 1. Start\n- [ ] Task\n## 2. Finish\n- [ ] Done\n")
    assert [item["number"] for item in phases] == [1, 2]
    assert _risk_label("Critical") == "risk:critical"
    assert _stability_label("Normative") == "stability:normative"


def test_load_tracks_rejects_duplicate_identifiers(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    duplicate = root / "conductor/tracks/duplicate_track_20260719"
    duplicate.mkdir()
    source = root / "conductor/tracks" / FIRST_TRACK / "metadata.json"
    shutil.copy2(source, duplicate / "metadata.json")
    with pytest.raises(ValueError, match="duplicate track id"):
        load_tracks(root)


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ("missing-required", "missing-file"),
        ("bad-config-json", "configuration-load"),
        ("maturity-order", "maturity-order"),
        ("duplicate-dimension", "duplicate-dimension"),
        ("duplicate-release", "duplicate-release"),
        ("release-order", "release-order"),
        ("bad-semver", "semver"),
        ("release-maturity-order", "release-maturity-order"),
        ("release-reference", "release-reference"),
        ("directory-id", "directory-id"),
        ("track-contract", "status"),
        ("dependencies", "unknown-dependency"),
        ("complete-without-evidence", "complete-without-evidence"),
        ("document-contract", "v1-contract"),
        ("plan-contract", "plan-order"),
        ("dependency-cycle", "dependency-cycle"),
        ("dependency-release-order", "dependency-release-order"),
        ("release-contract", "release-track"),
        ("target-release-scope", "target-release-scope"),
        ("missing-v1", "missing-v1"),
        ("stable-contract", "v1-channel"),
        ("global-gate-contract", "v1-gate-tracks"),
        ("hardening-closure", "v1-hardening-closure"),
        ("missing-issues", "missing-file"),
        ("bad-issues", "issue-load"),
        ("issue-drift", "issue-drift"),
    ],
)
def test_validator_rejects_roadmap_drift(tmp_path: Path, case: str, expected: str) -> None:
    root = copy_roadmap(tmp_path)
    check_issues = False

    if case == "missing-required":
        (root / "conductor/v1-gate.json").unlink()
    elif case == "bad-config-json":
        (root / "conductor/releases.json").write_text("[", encoding="utf-8")
    elif case == "maturity-order":
        path = root / "conductor/maturity-model.json"
        data = read_json(path)
        data["levels"][1]["id"] = "M2"
        write_json(path, data)
    elif case == "duplicate-dimension":
        path = root / "conductor/maturity-model.json"
        data = read_json(path)
        data["dimensions"].append(dict(data["dimensions"][0]))
        write_json(path, data)
    elif case == "duplicate-release":
        path = root / "conductor/releases.json"
        data = read_json(path)
        data["releases"].append(dict(data["releases"][-1]))
        write_json(path, data)
    elif case == "release-order":
        path = root / "conductor/releases.json"
        data = read_json(path)
        data["releases"][0], data["releases"][1] = data["releases"][1], data["releases"][0]
        write_json(path, data)
    elif case == "bad-semver":
        path = root / "conductor/releases.json"
        data = read_json(path)
        data["releases"][1]["version"] = "bad"
        write_json(path, data)
    elif case == "release-maturity-order":
        path = root / "conductor/releases.json"
        data = read_json(path)
        data["releases"][2]["maturity_level"] = "M1"
        write_json(path, data)
    elif case == "release-reference":
        path = root / "conductor/releases.json"
        data = read_json(path)
        data["current_release"] = "9.9.9"
        write_json(path, data)
    elif case == "directory-id":
        source = root / "conductor/tracks" / FIRST_TRACK
        destination = root / "conductor/tracks/wrong_directory_20260719"
        source.rename(destination)
    elif case == "track-contract":
        path, data = track_metadata(root)
        data.update(
            {
                "status": "unknown",
                "phase": "Unknown",
                "target_release": "9.9.9",
                "current_maturity": "M9",
                "maturity_target": "M0",
                "maturity_dimensions": ["unknown"],
            }
        )
        write_json(path, data)
        (path.parent / "index.md").write_text("# stale\n", encoding="utf-8")
    elif case == "dependencies":
        path, data = track_metadata(root)
        data["depends_on"] = [FIRST_TRACK, "unknown_track_20260719"]
        write_json(path, data)
        tracks_index = root / "conductor/tracks.md"
        tracks_index.write_text(
            tracks_index.read_text(encoding="utf-8").replace(f"`{FIRST_TRACK}`", "removed", 1),
            encoding="utf-8",
        )
    elif case == "complete-without-evidence":
        path, data = track_metadata(root)
        data["status"] = "complete"
        data["current_maturity"] = "M1"
        data["maturity_target"] = "M6"
        data["evidence"] = []
        write_json(path, data)
    elif case == "document-contract":
        path, data = track_metadata(root)
        spec_path = path.parent / "spec.md"
        spec = spec_path.read_text(encoding="utf-8")
        spec = spec.replace("## v1 role", "## Removed role")
        spec = spec.replace("## Evidence required", "## Removed evidence")
        spec = spec.replace("## Completion rule", "## Removed completion")
        spec = spec.replace("## Risks", "## Removed risks")
        spec = spec.replace("- [ ]", "- completed", 1)
        spec = spec.replace("Phase: **Foundation**", "Phase: **Wrong**")
        spec = spec.replace("## Dependencies\n\n- None.", "## Dependencies\n\n- `not_metadata`")
        spec_path.write_text(spec, encoding="utf-8")
        (path.parent / "index.md").write_text("# stale evidence index\n", encoding="utf-8")
    elif case == "plan-contract":
        path, _ = track_metadata(root)
        (path.parent / "plan.md").write_text(
            "# Plan\n\n## 1. First\n- [ ] task\n## 3. Third\nNo task\n## 4. Fourth\n- [ ] task\n",
            encoding="utf-8",
        )
    elif case == "dependency-cycle":
        path, data = track_metadata(root)
        data["depends_on"] = [HARDENING_TRACK]
        write_json(path, data)
    elif case == "dependency-release-order":
        path, data = track_metadata(root)
        data["depends_on"] = ["documentation_developer_experience_20260719"]
        write_json(path, data)
    elif case == "release-contract":
        path = root / "conductor/releases.json"
        data = read_json(path)
        release = data["releases"][1]
        release["required_tracks"].append("unknown_track_20260719")
        release["maturity_level"] = "M9"
        release["exit_gates"].append(dict(release["exit_gates"][0]))
        write_json(path, data)
    elif case == "target-release-scope":
        path = root / "conductor/releases.json"
        data = read_json(path)
        target = next(item for item in data["releases"] if item["version"] == "0.3.0")
        target["required_tracks"].remove(FIRST_TRACK)
        write_json(path, data)
    elif case == "missing-v1":
        path = root / "conductor/releases.json"
        data = read_json(path)
        data["stable_release"] = "9.9.9"
        write_json(path, data)
    elif case == "stable-contract":
        path = root / "conductor/releases.json"
        data = read_json(path)
        stable = next(item for item in data["releases"] if item["version"] == "1.0.0")
        stable["required_tracks"] = []
        stable["maturity_level"] = "M5"
        stable["channel"] = "candidate"
        stable["exit_gates"] = [
            gate for gate in stable["exit_gates"] if gate["category"] != "performance"
        ]
        write_json(path, data)
    elif case == "global-gate-contract":
        path = root / "conductor/v1-gate.json"
        data = read_json(path)
        data["required_tracks"] = []
        data["required_dimensions"] = data["required_dimensions"][:-1]
        data["release"] = "0.9.0"
        data["required_gate_ids"] = []
        data["required_maturity"] = "M5"
        write_json(path, data)
    elif case == "hardening-closure":
        path, data = track_metadata(root, HARDENING_TRACK)
        data["depends_on"] = data["depends_on"][:-1]
        write_json(path, data)
    elif case == "missing-issues":
        check_issues = True
        (root / "project/issues.yaml").unlink()
    elif case == "bad-issues":
        check_issues = True
        (root / "project/issues.yaml").write_text("[", encoding="utf-8")
    elif case == "issue-drift":
        check_issues = True
        path = root / "project/issues.yaml"
        data = read_json(path)
        data["issues"][0]["title"] = "drifted"
        write_json(path, data)
    else:  # pragma: no cover - protects the test table itself
        raise AssertionError(case)

    found = codes(root, issue_drift=check_issues)
    assert expected in found, (case, sorted(found))


def test_release_evidence_validation_reports_structural_and_reference_failures(
    tmp_path: Path,
) -> None:
    root = copy_roadmap(tmp_path)
    evidence_dir = root / "conductor/release-evidence"
    schema = read_json(root / "schemas/release-evidence.schema.json")
    releases = read_json(root / "conductor/releases.json")
    v1_gate = read_json(root / "conductor/v1-gate.json")

    (evidence_dir / "00-broken.json").write_text("[", encoding="utf-8")
    write_json(
        evidence_dir / "01-unknown.json",
        {
            "schema_version": "1.0.0",
            "evidence_id": "urn:test:unknown-release",
            "release": "9.9.9",
            "evaluated_at": iso(),
            "evaluated_by": "tester",
            "machine_readable": True,
            "immutable_evidence_identifiers": False,
            "source_revision": "uncommitted:test",
            "gates": [],
            "defects": {
                "open_p0": 0,
                "open_p1": 0,
                "release_blocking_p2": 0,
                "critical_security_findings": 0,
                "governance_prohibitions": 0,
                "expired_waivers": 0,
            },
            "metrics": {
                "agent_panel_analysts": 0,
                "clean_room_reproductions": 0,
                "external_reproductions": 0,
                "external_user_workflows": 0,
                "external_operator_workflows": 0,
                "operational_cycles": 0,
                "operational_evidence_days": 0,
                "release_candidate_soak_days": 0,
            },
            "approvals": [],
            "release_artifacts": [],
            "known_limitations": [],
        },
    )
    existing = root / "existing.txt"
    existing.write_text("evidence", encoding="utf-8")
    missing_ref = {
        **evidence_ref("missing", immutable=False),
        "location": "missing/report.json",
    }
    escaped_ref = {
        **evidence_ref("escape"),
        "location": "../outside.json",
    }
    bad_digest_ref = {
        **evidence_ref("bad-digest"),
        "location": "existing.txt",
        "sha256": "0" * 64,
    }
    duplicate_ref = evidence_ref("duplicate")
    malformed = stable_evidence(root)
    malformed.update(
        {
            "release": "0.2.0",
            "evidence_id": "urn:test:malformed-evidence",
            "source_revision": "uncommitted:test",
            "immutable_evidence_identifiers": True,
            "gates": [
                {
                    "gate_id": "roadmap-complete",
                    "status": "passed",
                    "evidence": [],
                    "reviewer": "reviewer",
                    "reviewed_at": iso(timedelta(days=1)),
                    "expires_at": None,
                    "waiver": None,
                    "notes": None,
                },
                {
                    "gate_id": "roadmap-complete",
                    "status": "waived",
                    "evidence": [missing_ref, duplicate_ref],
                    "reviewer": "reviewer",
                    "reviewed_at": iso(),
                    "expires_at": None,
                    "waiver": {
                        "category": "temporary",
                        "scope": "test scope",
                        "reason": "A sufficiently long reason",
                        "owner": "owner",
                        "approver": "approver",
                        "created_at": iso(timedelta(days=-200)),
                        "expires_at": iso(timedelta(days=-1)),
                        "mitigation": "A sufficiently long mitigation",
                        "public_summary": "A sufficiently long summary",
                        "remediation_issue": None,
                    },
                    "notes": None,
                },
                {
                    "gate_id": "unknown-gate",
                    "status": "waived",
                    "evidence": [evidence_ref("remote"), escaped_ref, bad_digest_ref],
                    "reviewer": "reviewer",
                    "reviewed_at": "bad-date",
                    "expires_at": None,
                    "waiver": {
                        "category": "temporary",
                        "scope": "test scope",
                        "reason": "A sufficiently long reason",
                        "owner": "owner",
                        "approver": "approver",
                        "created_at": "bad-date",
                        "expires_at": "bad-date",
                        "mitigation": "A sufficiently long mitigation",
                        "public_summary": "A sufficiently long summary",
                        "remediation_issue": None,
                    },
                    "notes": None,
                },
            ],
            "approvals": [
                {
                    "role": "Role",
                    "reviewer": "One",
                    "decision": "approve",
                    "decided_at": iso(),
                    "signed_decision_ref": None,
                    "notes": None,
                },
                {
                    "role": "Role",
                    "reviewer": "Two",
                    "decision": "approve",
                    "decided_at": iso(),
                    "signed_decision_ref": None,
                    "notes": None,
                },
            ],
            "release_artifacts": [duplicate_ref],
        }
    )
    write_json(evidence_dir / "02-evidence.json", malformed)
    write_json(evidence_dir / "03-duplicate.json", malformed)

    problems: list[RoadmapProblem] = []
    _validate_release_evidence(root, releases, schema, v1_gate, problems)
    found = {item.code for item in problems}
    assert {
        "evidence-load",
        "evidence-release",
        "duplicate-evidence",
        "duplicate-gate-evidence",
        "unknown-gate-evidence",
        "empty-gate-evidence",
        "expired-waiver",
        "waiver-duration",
        "invalid-waiver",
        "invalid-review-date",
        "missing-evidence",
        "evidence-path",
        "evidence-digest",
        "duplicate-evidence-id",
        "mutable-evidence",
        "waiver-count",
        "duplicate-approval-role",
        "schema",
    } <= found


def test_release_evidence_schema_requires_stable_sections(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    payload = stable_evidence(root)
    for key in ("defects", "metrics", "approvals", "release_artifacts"):
        payload.pop(key)
    write_json(root / "conductor/release-evidence/1.0.0.json", payload)
    assert "schema" in codes(root)


def test_stable_release_can_be_proven_ready_with_full_qualification_evidence(
    tmp_path: Path,
) -> None:
    root = copy_roadmap(tmp_path)
    make_stable_ready(root)
    readiness = release_readiness(root, "1.0.0")
    assert readiness.ready
    assert readiness.qualified_tracks == readiness.required_tracks == 28
    assert readiness.passed_gates == readiness.required_gates == 14

    status = roadmap_status(root, "1.0.0")
    markdown = render_status_markdown(status)
    assert "(READY)" in markdown
    assert "Tracks qualified: 28/28" in markdown
    assert "Gates: 14/14" in markdown


def test_archiving_a_complete_stable_track_preserves_release_qualification(
    tmp_path: Path,
) -> None:
    root = copy_roadmap(tmp_path)
    make_stable_ready(root)
    source = root / "conductor/tracks" / FIRST_TRACK
    destination = root / "conductor/archive" / FIRST_TRACK
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(source, destination)
    metadata_path = destination / "metadata.json"
    metadata = read_json(metadata_path)
    metadata["status"] = "archived"
    write_json(metadata_path, metadata)

    assert release_readiness(root, "1.0.0").ready


def test_stable_release_requires_content_bound_evidence_references(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    evidence = make_stable_ready(root)
    local = evidence["gates"][0]["evidence"][0]
    local["evidence_id"] = "urn:riopa:test:mutable-local-evidence"
    local["location"] = "conductor/releases.json"
    local["sha256"] = None

    external = evidence["gates"][1]["evidence"][0]
    external["evidence_id"] = "urn:riopa:test:mutable-external-evidence"
    external["location"] = "https://example.invalid/report"
    external["sha256"] = None

    write_json(root / "conductor/release-evidence/1.0.0.json", evidence)
    readiness = release_readiness(root, "1.0.0")
    text = "\n".join(readiness.blockers)
    assert "stable local evidence lacks a verified digest" in text
    assert "stable external evidence lacks a digest or content-addressed" in text


def test_release_readiness_reports_track_and_dependency_blockers(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    make_stable_ready(root)
    plan = read_json(root / "conductor/releases.json")
    stable = next(item for item in plan["releases"] if item["version"] == "1.0.0")
    a, b, c, d, e = stable["required_tracks"][:5]

    (root / "conductor/tracks" / a / "metadata.json").unlink()
    path, data = track_metadata(root, b)
    data["blocking_defects"] = ["P1:test"]
    write_json(path, data)
    path, data = track_metadata(root, c)
    data["evidence"] = []
    write_json(path, data)
    path, data = track_metadata(root, d)
    data["status"] = "active"
    write_json(path, data)
    path, data = track_metadata(root, e)
    data["current_maturity"] = "M5"
    write_json(path, data)

    readiness = release_readiness(root, "1.0.0")
    text = "\n".join(readiness.blockers)
    assert f"track {a} is missing" in text
    assert f"track {b} has blocking defects" in text
    assert f"track {c} has no linked implementation evidence" in text
    assert "complete or archived is required for stable v1" in text
    assert "M6 is required" in text
    assert "dependencies below M6" in text


def test_release_readiness_scopes_future_defects_by_maturity(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    plan = read_json(root / "conductor/releases.json")
    release = next(item for item in plan["releases"] if item["version"] == "0.3.0")
    for track_id in release["required_tracks"]:
        path, data = track_metadata(root, track_id)
        data["current_maturity"] = "M2"
        data["status"] = "active"
        data["evidence"] = [f"urn:test:{track_id}"]
        data["blocking_defects"] = []
        data.pop("blocking_defect_maturity", None)
        write_json(path, data)

    track_id = release["required_tracks"][0]
    path, data = track_metadata(root, track_id)
    data["blocking_defects"] = ["future-m3-gate"]
    data["blocking_defect_maturity"] = {"future-m3-gate": "M3"}
    write_json(path, data)

    readiness = release_readiness(root, "0.3.0")
    assert readiness.qualified_tracks == len(release["required_tracks"])
    assert not any(f"track {track_id} has blocking defects" in item for item in readiness.blockers)

    data["blocking_defect_maturity"]["future-m3-gate"] = "M2"
    write_json(path, data)
    readiness = release_readiness(root, "0.3.0")
    assert f"track {track_id} has blocking defects" in readiness.blockers


def test_validator_rejects_orphaned_defect_maturity_threshold(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    path, data = track_metadata(root)
    data["blocking_defect_maturity"] = {"undeclared-defect": "M3"}
    write_json(path, data)

    assert "blocking-defect-maturity" in codes(root)


def test_validator_rejects_unknown_defect_maturity_level(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    path, data = track_metadata(root)
    data["blocking_defects"] = ["future-gate"]
    data["blocking_defect_maturity"] = {"future-gate": "M7"}
    write_json(path, data)

    assert "schema" in codes(root)


def test_nonstable_release_rejects_proposed_status_and_unknown_version(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    plan = read_json(root / "conductor/releases.json")
    release = next(item for item in plan["releases"] if item["version"] == "0.3.0")
    for track_id, metadata in load_tracks(root).items():
        if metadata["_collection"] == "archive":
            continue
        path, data = track_metadata(root, track_id)
        data["current_maturity"] = "M2"
        data["status"] = "active"
        data["evidence"] = [f"urn:test:{track_id}"]
        write_json(path, data)
    path, data = track_metadata(root, release["required_tracks"][0])
    data["status"] = "proposed"
    write_json(path, data)

    evidence_dir = root / "conductor/release-evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        evidence_dir / "0.3.0.json",
        {
            "schema_version": "1.0.0",
            "release": "0.3.0",
            "evaluated_at": iso(),
            "evaluated_by": "tester",
            "tool": {"name": "test", "version": "1", "environment": None},
            "gates": [passing_gate(item["id"]) for item in release["exit_gates"]],
        },
    )
    readiness = release_readiness(root, "0.3.0")
    assert not readiness.ready
    assert any("status proposed" in blocker for blocker in readiness.blockers)
    with pytest.raises(ValueError, match="unknown release"):
        release_readiness(root, "9.9.9")


def test_gate_freshness_waiver_and_decision_failures_are_blocking(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    evidence = make_stable_ready(root)
    gates = evidence["gates"]
    gates[0]["reviewer"] = None
    gates[1]["expires_at"] = iso(timedelta(days=-1))
    gates[2]["reviewed_at"] = iso(timedelta(days=-200))
    gates[3]["reviewed_at"] = "bad-date"
    gates[4].update(
        {
            "status": "waived",
            "waiver": {
                "category": "security-critical",
                "scope": "qualification gate",
                "reason": "A sufficiently long waiver reason",
                "owner": "owner",
                "approver": "approver",
                "created_at": iso(),
                "expires_at": iso(timedelta(days=30)),
                "mitigation": "A sufficiently long mitigation plan",
                "public_summary": "A sufficiently long public summary",
                "remediation_issue": None,
            },
        }
    )
    gates[5]["status"] = "failed"
    gates[5]["waiver"] = None
    write_json(root / "conductor/release-evidence/1.0.0.json", evidence)

    readiness = release_readiness(root, "1.0.0")
    text = "\n".join(readiness.blockers)
    assert "lacks stable review evidence" in text
    assert "evidence has expired" in text
    assert "days old" in text
    assert "invalid evidence dates" in text
    assert "non-waivable category security-critical" in text
    assert "is not passed with current evidence" in text


def test_current_waiver_can_satisfy_a_waivable_gate(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    evidence = make_stable_ready(root)
    evidence["gates"][0].update(
        {
            "status": "waived",
            "waiver": {
                "category": "temporary-compatibility",
                "scope": "bounded compatibility exception",
                "reason": "A sufficiently long waiver reason",
                "owner": "owner",
                "approver": "approver",
                "created_at": iso(),
                "expires_at": iso(timedelta(days=30)),
                "mitigation": "A sufficiently long mitigation plan",
                "public_summary": "A sufficiently long public summary",
                "remediation_issue": None,
            },
        }
    )
    write_json(root / "conductor/release-evidence/1.0.0.json", evidence)
    assert release_readiness(root, "1.0.0").ready
    assert _waiver_is_current(evidence["gates"][0], datetime.now(UTC))
    assert not _waiver_is_current({"waiver": {"expires_at": "bad"}}, datetime.now(UTC))


def test_stable_qualification_metrics_defects_approvals_and_decision_are_enforced(
    tmp_path: Path,
) -> None:
    root = copy_roadmap(tmp_path)
    evidence = make_stable_ready(root)
    evidence["defects"].pop("open_p0")
    evidence["defects"]["open_p1"] = 1
    evidence["metrics"].pop("agent_panel_analysts")
    evidence["metrics"]["clean_room_reproductions"] = 1
    evidence["machine_readable"] = False
    evidence["immutable_evidence_identifiers"] = False
    evidence["source_revision"] = "uncommitted:test"
    evidence["approvals"] = evidence["approvals"][:-1]
    evidence["approvals"][0]["signed_decision_ref"] = None
    evidence["release_artifacts"] = []
    write_json(root / "conductor/release-evidence/1.0.0.json", evidence)

    readiness = release_readiness(root, "1.0.0")
    text = "\n".join(readiness.blockers)
    assert "stable defect metric open_p0 is missing" in text
    assert "open_p1=1 exceeds 0" in text
    assert "agent_panel_analysts is missing" in text
    assert "clean_room_reproductions=1 is below 2" in text
    assert "not declared machine-readable" in text
    assert "does not require immutable identifiers" in text
    assert "source revision is absent or not immutable" in text
    assert "approvals missing roles" in text
    assert "approvals are unsigned" in text
    assert "no immutable release artifacts" in text


def test_issue_generation_fallbacks_and_output_paths(tmp_path: Path) -> None:
    root = copy_roadmap(tmp_path)
    path, data = track_metadata(root)
    data["v1_critical"] = False
    data["maturity_dimensions"] = []
    data["depends_on"] = []
    data["owner_role"] = "Maintainer"
    write_json(path, data)
    spec_path = path.parent / "spec.md"
    spec = spec_path.read_text(encoding="utf-8")
    spec_path.write_text(spec.replace("# Track:", "# Not a title:"), encoding="utf-8")

    generated = generate_issue_configuration(root)
    issue = next(item for item in generated["issues"] if item["key"] == FIRST_TRACK)
    assert issue["title"] == f"[Track] {FIRST_TRACK}"
    assert "v1-critical" not in issue["labels"]
    assert "provenance" not in issue["labels"]
    assert "geospatial" not in issue["labels"]
    assert "rights-governance" not in issue["labels"]
    assert "- None." in issue["body"]

    default = write_issue_configuration(root)
    assert default == root / "project/issues.yaml"
    custom = write_issue_configuration(root, tmp_path / "nested/issues.json")
    assert custom.is_file()
    assert read_json(custom) == generated
