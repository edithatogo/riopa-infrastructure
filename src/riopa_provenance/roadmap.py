"""Executable Conductor roadmap, maturity, and release-readiness tooling.

The roadmap is treated as versioned configuration rather than prose. Track metadata,
dependency order, maturity levels, release gates, global v1 policy, evidence records,
and generated GitHub issues must remain mutually consistent.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .hashing import sha256_file

TRACK_STATUSES = (
    "proposed",
    "specified",
    "ready",
    "active",
    "validating",
    "complete",
    "archived",
)
PHASE_SLUGS = {
    "Foundation": "foundation",
    "Core": "core",
    "NZ Spatial": "nz-spatial",
    "Analytics": "analytics",
    "Applications": "applications",
    "Publication": "publication",
    "Release": "release",
}
SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<pre>[0-9A-Za-z.-]+))?$"
)
PHASE_RE = re.compile(r"^##\s+(?P<number>\d+)\.\s+(?P<title>.+?)\s*$", re.MULTILINE)
TASK_RE = re.compile(r"^- \[[ x~]\]\s+(?P<task>.+?)\s*$", re.MULTILINE)
CHECKBOX_RE = re.compile(r"^- \[ \]\s+(.+?)\s*$", re.MULTILINE)
HEADER_RE = {
    "track_id": re.compile(r"^Track ID:\s*`(?P<value>[^`]+)`", re.MULTILINE),
    "phase": re.compile(r"^Phase:\s*\*\*(?P<value>[^*]+)\*\*", re.MULTILINE),
    "target_release": re.compile(r"^Target release:\s*\*\*(?P<value>[^*]+)\*\*", re.MULTILINE),
    "maturity_target": re.compile(r"^Maturity target:\s*\*\*(?P<value>[^*]+)\*\*", re.MULTILINE),
    "stability_class": re.compile(r"^Stability class:\s*\*\*(?P<value>[^*]+)\*\*", re.MULTILINE),
}


@dataclass(frozen=True)
class RoadmapProblem:
    """One deterministic roadmap validation failure."""

    code: str
    location: str
    message: str

    def __str__(self) -> str:
        return f"{self.code} [{self.location}]: {self.message}"


@dataclass(frozen=True)
class ReleaseReadiness:
    """Calculated readiness for one planned release."""

    version: str
    name: str
    maturity_level: str
    ready: bool
    qualified_tracks: int
    required_tracks: int
    passed_gates: int
    required_gates: int
    blockers: tuple[str, ...]


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_errors(instance: Any, schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.path))
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def _semver_key(version: str) -> tuple[int, int, int, int, tuple[tuple[int, Any], ...]]:
    """Return a SemVer ordering key, including numeric prerelease identifiers."""

    match = SEMVER_RE.fullmatch(version)
    if not match:
        raise ValueError(f"invalid semantic version: {version}")
    prerelease = match.group("pre")
    pre_key: tuple[tuple[int, Any], ...] = ()
    if prerelease:
        pre_key = tuple(
            (0, int(part)) if part.isdigit() else (1, part) for part in prerelease.split(".")
        )
    return (
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("patch")),
        0 if prerelease else 1,
        pre_key,
    )


def _maturity_rank(identifier: str) -> int:
    if not re.fullmatch(r"M\d+", identifier):
        raise ValueError(f"invalid maturity identifier: {identifier}")
    return int(identifier[1:])


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def load_tracks(root: str | Path) -> dict[str, dict[str, Any]]:
    """Load active and archived Conductor metadata keyed by track ID."""

    base = Path(root)
    tracks: dict[str, dict[str, Any]] = {}
    for collection in ("tracks", "archive"):
        for path in sorted((base / "conductor" / collection).glob("*/metadata.json")):
            item = _load(path)
            track_id = item.get("track_id", path.parent.name)
            if track_id in tracks:
                previous = tracks[track_id]["_path"]
                raise ValueError(f"duplicate track id {track_id}: {previous} and {path.as_posix()}")
            item["_collection"] = collection
            item["_directory"] = path.parent.name
            item["_path"] = path.as_posix()
            tracks[track_id] = item
    return tracks


def _track_directory(item: dict[str, Any]) -> Path:
    """Return the discovered directory containing one track's artifacts."""

    return Path(str(item["_path"])).parent


def _detect_cycle(dependencies: dict[str, set[str]]) -> list[str] | None:
    visiting: list[str] = []
    visited: set[str] = set()

    def visit(track_id: str) -> list[str] | None:
        if track_id in visited:
            return None
        if track_id in visiting:
            start = visiting.index(track_id)
            return [*visiting[start:], track_id]
        visiting.append(track_id)
        for dependency in sorted(dependencies.get(track_id, set())):
            cycle = visit(dependency)
            if cycle:
                return cycle
        visiting.pop()
        visited.add(track_id)
        return None

    for track_id in sorted(dependencies):
        cycle = visit(track_id)
        if cycle:
            return cycle
    return None


def _section(text: str, heading: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group("body").strip() if match else ""


def _plan_phases(text: str) -> list[dict[str, Any]]:
    matches = list(PHASE_RE.finditer(text))
    phases: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end() : end]
        phases.append(
            {
                "number": int(match.group("number")),
                "title": match.group("title").strip(),
                "tasks": TASK_RE.findall(body),
            }
        )
    return phases


def _markdown_dependencies(spec: str) -> set[str]:
    body = _section(spec, "Dependencies")
    return set(re.findall(r"^- `([^`]+)`\s*$", body, flags=re.MULTILINE))


def _risk_label(value: str) -> str:
    return f"risk:{value.lower()}"


def _stability_label(value: str) -> str:
    return f"stability:{value.lower()}"


def _validate_track_documents(
    item: dict[str, Any],
    problems: list[RoadmapProblem],
) -> None:
    track_dir = _track_directory(item)
    spec_path = track_dir / "spec.md"
    plan_path = track_dir / "plan.md"
    index_path = track_dir / "index.md"
    if spec_path.is_file():
        spec = spec_path.read_text(encoding="utf-8")
        if "## Acceptance criteria" not in spec or not CHECKBOX_RE.search(
            _section(spec, "Acceptance criteria")
        ):
            problems.append(
                RoadmapProblem(
                    "acceptance", spec_path.as_posix(), "acceptance criteria are not checkable"
                )
            )
        required_sections = ("v1 role", "Evidence required", "Completion rule", "Risks")
        missing = [name for name in required_sections if f"## {name}" not in spec]
        if missing:
            problems.append(
                RoadmapProblem(
                    "v1-contract",
                    spec_path.as_posix(),
                    f"missing required sections: {missing}",
                )
            )
        for field, pattern in HEADER_RE.items():
            match = pattern.search(spec)
            if not match or match.group("value") != str(item.get(field)):
                problems.append(
                    RoadmapProblem(
                        "spec-metadata-drift",
                        spec_path.as_posix(),
                        f"{field} header does not match metadata",
                    )
                )
        documented_dependencies = _markdown_dependencies(spec)
        metadata_dependencies = set(item.get("depends_on", []))
        if documented_dependencies != metadata_dependencies:
            problems.append(
                RoadmapProblem(
                    "dependency-doc-drift",
                    spec_path.as_posix(),
                    "documented dependencies do not match metadata",
                )
            )

    if plan_path.is_file():
        plan = plan_path.read_text(encoding="utf-8")
        phases = _plan_phases(plan)
        if not phases or any(not phase["tasks"] for phase in phases):
            problems.append(
                RoadmapProblem(
                    "plan",
                    plan_path.as_posix(),
                    "numbered phases with checkable tasks are required",
                )
            )
        numbers = [phase["number"] for phase in phases]
        if numbers != list(range(1, len(numbers) + 1)):
            problems.append(
                RoadmapProblem(
                    "plan-order", plan_path.as_posix(), "phase numbers must be consecutive from 1"
                )
            )
        if len(phases) < 4:
            problems.append(
                RoadmapProblem(
                    "plan-depth",
                    plan_path.as_posix(),
                    "a v1-critical track needs at least four phases",
                )
            )

    if index_path.is_file():
        index = index_path.read_text(encoding="utf-8")
        expected_fragments = (
            f"`{item.get('status')}`",
            f"`{item.get('target_release')}`",
            f"`{item.get('current_maturity')}`",
            f"`{item.get('maturity_target')}`",
        )
        missing = [value for value in expected_fragments if value not in index]
        if missing:
            problems.append(
                RoadmapProblem(
                    "evidence-index-drift",
                    index_path.as_posix(),
                    f"metadata values missing from evidence index: {missing}",
                )
            )


def _validate_architecture_fitness(
    base: Path, tracks: dict[str, dict[str, Any]], problems: list[RoadmapProblem]
) -> None:
    """Check the foundation boundary contract and component ownership index."""

    required = {
        "docs/architecture.md": ("## Component model", "## Data-flow guarantees"),
        "docs/v1-scope-and-boundaries.md": (
            "## Platform guarantees",
            "## Separate release axes",
            "## Responsibility boundaries",
            "## Non-claims",
        ),
        "docs/governance-and-sustainability.md": (
            "## Decision rights",
            "## Sources of truth",
            "## Contribution and succession",
        ),
        "docs/adr/README.md": ("# Architecture decision register", "## Reconciliation rules"),
    }
    for relative, headings in required.items():
        path = base / relative
        if not path.is_file():
            problems.append(
                RoadmapProblem("architecture-artifact", relative, "required artifact is absent")
            )
            continue
        text = path.read_text(encoding="utf-8")
        for heading in headings:
            if heading not in text:
                problems.append(
                    RoadmapProblem(
                        "architecture-artifact",
                        relative,
                        f"missing required contract section: {heading}",
                    )
                )

    for track_id, item in sorted(tracks.items()):
        for field in ("owner_repository", "owner_role", "target_release", "maturity_target"):
            if not item.get(field):
                problems.append(
                    RoadmapProblem(
                        "architecture-ownership",
                        f"conductor/tracks/{track_id}/metadata.json",
                        f"missing {field}",
                    )
                )


def _evidence_location(reference: Any) -> str:
    """Return an evidence location without assuming a schema-valid payload."""

    return str(reference.get("location", "")) if isinstance(reference, dict) else ""


def _evidence_identifier(reference: Any) -> str:
    return str(reference.get("evidence_id", "")) if isinstance(reference, dict) else ""


def _validate_evidence_reference(
    base: Path,
    evidence_path: Path,
    reference: Any,
    problems: list[RoadmapProblem],
    *,
    release_version: str | None = None,
) -> None:
    """Verify a local evidence reference and any declared digest."""

    if not isinstance(reference, dict):
        return
    location = _evidence_location(reference)
    if not location or location.startswith(("http://", "https://", "urn:", "doi:", "swh:")):
        return
    candidate = (base / location).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        problems.append(
            RoadmapProblem(
                "evidence-path",
                evidence_path.as_posix(),
                f"evidence path escapes repository root: {location}",
            )
        )
        return
    snapshot: Path | None = None
    snapshot_root: Path | None = None
    if release_version is not None:
        snapshot_root = (base / "conductor/release-evidence/artifacts" / release_version).resolve()
        snapshot = snapshot_root / location
    if snapshot is not None and snapshot.is_file():
        candidate = snapshot.resolve()
        assert snapshot_root is not None
        try:
            candidate.relative_to(snapshot_root)
        except ValueError:
            problems.append(
                RoadmapProblem(
                    "evidence-path",
                    evidence_path.as_posix(),
                    f"snapshot evidence path escapes release root: {location}",
                )
            )
            return
    elif not candidate.is_file():
        problems.append(
            RoadmapProblem(
                "missing-evidence",
                evidence_path.as_posix(),
                f"evidence path does not exist: {location}",
            )
        )
        return
    expected_digest = reference.get("sha256")
    if expected_digest and sha256_file(candidate) != expected_digest:
        problems.append(
            RoadmapProblem(
                "evidence-digest",
                evidence_path.as_posix(),
                f"evidence digest does not match: {location}",
            )
        )


def _validate_release_evidence(
    base: Path,
    release_plan: dict[str, Any],
    evidence_schema: dict[str, Any],
    v1_gate: dict[str, Any],
    problems: list[RoadmapProblem],
) -> None:
    """Validate release evidence records, references, waivers, and review metadata."""

    release_by_version = {item["version"]: item for item in release_plan.get("releases", [])}
    evidence_dir = base / "conductor/release-evidence"
    if not evidence_dir.is_dir():
        return

    now = datetime.now(UTC)
    maximum_waiver_days = v1_gate.get("waiver_policy", {}).get("maximum_duration_days", 90)
    seen_releases: set[str] = set()
    for path in sorted(evidence_dir.glob("*.json")):
        try:
            payload = _load(path)
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(RoadmapProblem("evidence-load", path.as_posix(), str(exc)))
            continue
        for error in _schema_errors(payload, evidence_schema):
            problems.append(RoadmapProblem("schema", path.as_posix(), error))
        if not isinstance(payload, dict):
            continue

        version = payload.get("release")
        if isinstance(version, str) and version in seen_releases:
            problems.append(
                RoadmapProblem(
                    "duplicate-evidence", path.as_posix(), f"duplicate release evidence: {version}"
                )
            )
        if isinstance(version, str):
            seen_releases.add(version)
        release = release_by_version.get(version)
        if not release:
            problems.append(
                RoadmapProblem(
                    "evidence-release", path.as_posix(), "evidence references an unknown release"
                )
            )
            continue

        allowed_gates = {gate["id"] for gate in release.get("exit_gates", [])}
        gates = [gate for gate in payload.get("gates", []) if isinstance(gate, dict)]
        gate_ids: list[str] = [
            gate_id for gate in gates if isinstance((gate_id := gate.get("gate_id")), str)
        ]
        if len(gate_ids) != len(set(gate_ids)):
            problems.append(
                RoadmapProblem(
                    "duplicate-gate-evidence", path.as_posix(), "gate evidence IDs must be unique"
                )
            )
        unknown = set(gate_ids) - allowed_gates
        if unknown:
            problems.append(
                RoadmapProblem(
                    "unknown-gate-evidence", path.as_posix(), f"unknown gate IDs: {sorted(unknown)}"
                )
            )

        all_references: list[Any] = []
        expired_waivers = 0
        for gate in gates:
            status = gate.get("status")
            references = gate.get("evidence", []) if isinstance(gate.get("evidence"), list) else []
            all_references.extend(references)
            if status in {"passed", "waived"} and not references:
                problems.append(
                    RoadmapProblem(
                        "empty-gate-evidence",
                        path.as_posix(),
                        f"gate {gate.get('gate_id')} has no evidence",
                    )
                )
            if status in {"passed", "waived"}:
                reviewed_at = gate.get("reviewed_at")
                try:
                    if not reviewed_at or _parse_datetime(reviewed_at) > now:
                        problems.append(
                            RoadmapProblem(
                                "invalid-review-date",
                                path.as_posix(),
                                f"gate {gate.get('gate_id')} review date is missing or in "
                                "the future",
                            )
                        )
                except TypeError, ValueError:
                    problems.append(
                        RoadmapProblem(
                            "invalid-review-date",
                            path.as_posix(),
                            f"gate {gate.get('gate_id')} review date is invalid",
                        )
                    )
            if status == "waived":
                waiver = gate.get("waiver") or {}
                created = waiver.get("created_at") if isinstance(waiver, dict) else None
                expires = waiver.get("expires_at") if isinstance(waiver, dict) else None
                if not expires:
                    problems.append(
                        RoadmapProblem(
                            "invalid-waiver",
                            path.as_posix(),
                            f"gate {gate.get('gate_id')} waiver has no expiry",
                        )
                    )
                else:
                    try:
                        expiry = _parse_datetime(expires)
                        if expiry <= now:
                            expired_waivers += 1
                            problems.append(
                                RoadmapProblem(
                                    "expired-waiver",
                                    path.as_posix(),
                                    f"gate {gate.get('gate_id')} waiver has expired",
                                )
                            )
                        if created:
                            duration = (expiry - _parse_datetime(created)).days
                            if duration < 0 or duration > maximum_waiver_days:
                                problems.append(
                                    RoadmapProblem(
                                        "waiver-duration",
                                        path.as_posix(),
                                        f"gate {gate.get('gate_id')} waiver duration is "
                                        f"{duration} days",
                                    )
                                )
                    except TypeError, ValueError:
                        problems.append(
                            RoadmapProblem(
                                "invalid-waiver",
                                path.as_posix(),
                                f"gate {gate.get('gate_id')} waiver dates are invalid",
                            )
                        )
            for reference in references:
                _validate_evidence_reference(
                    base, path, reference, problems, release_version=version
                )

        release_artifacts = payload.get("release_artifacts", [])
        if isinstance(release_artifacts, list):
            all_references.extend(release_artifacts)
            for reference in release_artifacts:
                _validate_evidence_reference(
                    base, path, reference, problems, release_version=version
                )

        identifiers = [
            _evidence_identifier(reference)
            for reference in all_references
            if _evidence_identifier(reference)
        ]
        duplicates = sorted(key for key, count in Counter(identifiers).items() if count > 1)
        if duplicates:
            problems.append(
                RoadmapProblem(
                    "duplicate-evidence-id",
                    path.as_posix(),
                    f"evidence identifiers must be unique: {duplicates}",
                )
            )
        if payload.get("immutable_evidence_identifiers"):
            mutable = [
                _evidence_identifier(reference) or _evidence_location(reference)
                for reference in all_references
                if isinstance(reference, dict) and not reference.get("immutable")
            ]
            if mutable:
                problems.append(
                    RoadmapProblem(
                        "mutable-evidence",
                        path.as_posix(),
                        f"evidence declared immutable contains mutable references: {mutable}",
                    )
                )

        declared_expired = (payload.get("defects") or {}).get("expired_waivers")
        if isinstance(declared_expired, int) and declared_expired != expired_waivers:
            problems.append(
                RoadmapProblem(
                    "waiver-count",
                    path.as_posix(),
                    f"declared expired_waivers={declared_expired}, observed={expired_waivers}",
                )
            )
        approval_roles = [
            item.get("role")
            for item in payload.get("approvals", [])
            if isinstance(item, dict) and isinstance(item.get("role"), str)
        ]
        if len(approval_roles) != len(set(approval_roles)):
            problems.append(
                RoadmapProblem(
                    "duplicate-approval-role",
                    path.as_posix(),
                    "each release-authority role may appear at most once",
                )
            )


def validate_roadmap(
    root: str | Path, *, check_generated_issues: bool = True
) -> tuple[RoadmapProblem, ...]:
    """Validate the complete Conductor roadmap and stable-v1 release model."""

    base = Path(root).resolve()
    problems: list[RoadmapProblem] = []
    required_files = [
        base / "conductor/maturity-model.json",
        base / "conductor/releases.json",
        base / "conductor/v1-gate.json",
        base / "conductor/tracks.md",
        base / "schemas/track-metadata.schema.json",
        base / "schemas/maturity-model.schema.json",
        base / "schemas/release-roadmap.schema.json",
        base / "schemas/v1-gate.schema.json",
        base / "schemas/release-evidence.schema.json",
    ]
    for path in required_files:
        if not path.is_file():
            problems.append(
                RoadmapProblem("missing-file", path.as_posix(), "required file is absent")
            )
    if problems:
        return tuple(problems)

    try:
        track_schema = _load(base / "schemas/track-metadata.schema.json")
        maturity = _load(base / "conductor/maturity-model.json")
        release_plan = _load(base / "conductor/releases.json")
        v1_gate = _load(base / "conductor/v1-gate.json")
        maturity_schema = _load(base / "schemas/maturity-model.schema.json")
        release_schema = _load(base / "schemas/release-roadmap.schema.json")
        v1_gate_schema = _load(base / "schemas/v1-gate.schema.json")
        evidence_schema = _load(base / "schemas/release-evidence.schema.json")
    except (OSError, json.JSONDecodeError) as exc:
        return (RoadmapProblem("configuration-load", base.as_posix(), str(exc)),)

    for payload, schema, location in (
        (maturity, maturity_schema, "conductor/maturity-model.json"),
        (release_plan, release_schema, "conductor/releases.json"),
        (v1_gate, v1_gate_schema, "conductor/v1-gate.json"),
    ):
        for error in _schema_errors(payload, schema):
            problems.append(RoadmapProblem("schema", location, error))

    try:
        tracks = load_tracks(base)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return (RoadmapProblem("track-load", "conductor/tracks", str(exc)),)

    _validate_architecture_fitness(base, tracks, problems)

    maturity_ids = [item.get("id") for item in maturity.get("levels", [])]
    expected_maturity_ids = [f"M{index}" for index in range(len(maturity_ids))]
    if maturity_ids != expected_maturity_ids:
        problems.append(
            RoadmapProblem(
                "maturity-order",
                "conductor/maturity-model.json",
                f"levels must be contiguous and ordered: {expected_maturity_ids}",
            )
        )
    dimension_ids = [item.get("id") for item in maturity.get("dimensions", [])]
    if len(dimension_ids) != len(set(dimension_ids)):
        problems.append(
            RoadmapProblem(
                "duplicate-dimension",
                "conductor/maturity-model.json",
                "maturity dimensions must be unique",
            )
        )
    maturity_set = set(maturity_ids)
    dimension_set = set(dimension_ids)

    release_versions = [item.get("version") for item in release_plan.get("releases", [])]
    release_set = set(release_versions)
    release_by_version = {
        item["version"]: item for item in release_plan.get("releases", []) if "version" in item
    }
    if len(release_versions) != len(release_set):
        problems.append(
            RoadmapProblem(
                "duplicate-release", "conductor/releases.json", "release versions must be unique"
            )
        )
    try:
        if release_versions != sorted(release_versions, key=_semver_key):
            problems.append(
                RoadmapProblem(
                    "release-order",
                    "conductor/releases.json",
                    "releases are not in semantic-version order",
                )
            )
    except ValueError as exc:
        problems.append(RoadmapProblem("semver", "conductor/releases.json", str(exc)))
    release_maturities = [item.get("maturity_level") for item in release_plan.get("releases", [])]
    known_release_maturities = [value for value in release_maturities if value in maturity_set]
    if known_release_maturities and [
        _maturity_rank(value) for value in known_release_maturities
    ] != sorted(_maturity_rank(value) for value in known_release_maturities):
        problems.append(
            RoadmapProblem(
                "release-maturity-order",
                "conductor/releases.json",
                "release maturity must not regress across the release train",
            )
        )
    for key in ("current_release", "stable_release"):
        if release_plan.get(key) not in release_set:
            problems.append(
                RoadmapProblem(
                    "release-reference",
                    "conductor/releases.json",
                    f"{key} is not present in the release train",
                )
            )

    dependencies: dict[str, set[str]] = {}
    track_index_text = (base / "conductor/tracks.md").read_text(encoding="utf-8")
    for track_id, item in tracks.items():
        location = item.get("_path", track_id)
        track_dir = _track_directory(item)
        candidate = {key: value for key, value in item.items() if not key.startswith("_")}
        for error in _schema_errors(candidate, track_schema):
            problems.append(RoadmapProblem("schema", location, error))
        if item.get("_directory") != track_id:
            problems.append(
                RoadmapProblem("directory-id", location, "track_id must match its directory")
            )
        collection = item.get("_collection")
        status = item.get("status")
        if collection == "archive" and status != "archived":
            problems.append(
                RoadmapProblem(
                    "archive-status",
                    location,
                    "tracks under conductor/archive must have archived status",
                )
            )
        if collection == "tracks" and status == "archived":
            problems.append(
                RoadmapProblem(
                    "archive-location",
                    location,
                    "archived tracks must be moved under conductor/archive",
                )
            )
        for filename in ("spec.md", "plan.md", "metadata.json", "index.md"):
            path = track_dir / filename
            if not path.is_file():
                problems.append(
                    RoadmapProblem(
                        "missing-track-file", path.as_posix(), "track artifact is absent"
                    )
                )
        if item.get("status") not in TRACK_STATUSES:
            problems.append(
                RoadmapProblem("status", location, f"unknown track status: {item.get('status')}")
            )
        if item.get("phase") not in PHASE_SLUGS:
            problems.append(
                RoadmapProblem("phase", location, f"unknown phase: {item.get('phase')}")
            )
        target_release = item.get("target_release")
        if target_release not in release_set:
            problems.append(
                RoadmapProblem(
                    "target-release", location, f"unknown target release: {target_release}"
                )
            )
        current_maturity = item.get("current_maturity")
        target_maturity = item.get("maturity_target")
        if current_maturity not in maturity_set:
            problems.append(
                RoadmapProblem(
                    "maturity", location, f"unknown current maturity: {current_maturity}"
                )
            )
        if target_maturity not in maturity_set:
            problems.append(
                RoadmapProblem("maturity", location, f"unknown maturity target: {target_maturity}")
            )
        if (
            isinstance(current_maturity, str)
            and isinstance(target_maturity, str)
            and current_maturity in maturity_set
            and target_maturity in maturity_set
            and _maturity_rank(current_maturity) > _maturity_rank(target_maturity)
        ):
            problems.append(
                RoadmapProblem(
                    "maturity-regression",
                    location,
                    "current maturity cannot exceed the declared target",
                )
            )
        unknown_dimensions = set(item.get("maturity_dimensions", [])) - dimension_set
        if unknown_dimensions:
            problems.append(
                RoadmapProblem(
                    "maturity-dimension",
                    location,
                    f"unknown dimensions: {sorted(unknown_dimensions)}",
                )
            )
        defect_maturity = item.get("blocking_defect_maturity", {})
        if isinstance(defect_maturity, dict):
            orphaned_defects = set(defect_maturity) - set(item.get("blocking_defects", []))
            if orphaned_defects:
                problems.append(
                    RoadmapProblem(
                        "blocking-defect-maturity",
                        location,
                        "maturity thresholds reference undeclared blocking defects: "
                        f"{sorted(orphaned_defects)}",
                    )
                )
        dependencies[track_id] = set(item.get("depends_on", []))
        if track_id in dependencies[track_id]:
            problems.append(
                RoadmapProblem("self-dependency", location, "track cannot depend on itself")
            )
        unknown_dependencies = dependencies[track_id] - tracks.keys()
        if unknown_dependencies:
            problems.append(
                RoadmapProblem(
                    "unknown-dependency",
                    location,
                    f"unknown dependencies: {sorted(unknown_dependencies)}",
                )
            )
        if f"`{track_id}`" not in track_index_text:
            problems.append(
                RoadmapProblem("track-index", "conductor/tracks.md", f"missing track {track_id}")
            )
        if item.get("v1_critical") and target_maturity != maturity_ids[-1]:
            problems.append(
                RoadmapProblem(
                    "v1-track-maturity",
                    location,
                    f"v1-critical tracks must target {maturity_ids[-1]}",
                )
            )
        if item.get("status") in {"complete", "archived"}:
            if not item.get("evidence"):
                problems.append(
                    RoadmapProblem(
                        "complete-without-evidence",
                        location,
                        "complete or archived tracks require linked evidence",
                    )
                )
            if current_maturity != target_maturity:
                problems.append(
                    RoadmapProblem(
                        "complete-before-target",
                        location,
                        "complete or archived tracks must reach their target maturity",
                    )
                )
        _validate_track_documents(item, problems)

    cycle = _detect_cycle(dependencies)
    if cycle:
        problems.append(RoadmapProblem("dependency-cycle", "conductor/tracks", " -> ".join(cycle)))

    for track_id, required in dependencies.items():
        target = tracks[track_id].get("target_release")
        if target not in release_set:
            continue
        for dependency in required:
            dependency_target = tracks.get(dependency, {}).get("target_release")
            if (
                isinstance(dependency_target, str)
                and isinstance(target, str)
                and dependency_target in release_set
                and _semver_key(dependency_target) > _semver_key(target)
            ):
                problems.append(
                    RoadmapProblem(
                        "dependency-release-order",
                        tracks[track_id].get("_path", track_id),
                        f"dependency {dependency} targets later release {dependency_target}",
                    )
                )

    for release in release_plan.get("releases", []):
        version = release.get("version")
        location = f"conductor/releases.json#{version}"
        unknown = set(release.get("required_tracks", [])) - tracks.keys()
        if unknown:
            problems.append(
                RoadmapProblem(
                    "release-track", location, f"unknown required tracks: {sorted(unknown)}"
                )
            )
        if release.get("maturity_level") not in maturity_set:
            problems.append(
                RoadmapProblem(
                    "release-maturity",
                    location,
                    f"unknown maturity level: {release.get('maturity_level')}",
                )
            )
        gate_ids = [gate.get("id") for gate in release.get("exit_gates", [])]
        if len(gate_ids) != len(set(gate_ids)):
            problems.append(
                RoadmapProblem("duplicate-gate", location, "exit gate IDs must be unique")
            )

    for track_id, item in tracks.items():
        target = item.get("target_release")
        release = release_by_version.get(target)
        if release and track_id not in release.get("required_tracks", []):
            problems.append(
                RoadmapProblem(
                    "target-release-scope",
                    item.get("_path", track_id),
                    f"track is absent from its target release {target}",
                )
            )

    stable_version = release_plan.get("stable_release")
    stable = release_by_version.get(stable_version)
    critical = {track_id for track_id, item in tracks.items() if item.get("v1_critical")}
    if not stable:
        problems.append(
            RoadmapProblem(
                "missing-v1", "conductor/releases.json", "stable release definition is required"
            )
        )
    else:
        stable_tracks = set(stable.get("required_tracks", []))
        if stable_tracks != critical:
            problems.append(
                RoadmapProblem(
                    "v1-scope",
                    f"conductor/releases.json#{stable_version}",
                    f"stable required tracks differ from v1-critical tracks: "
                    f"missing={sorted(critical - stable_tracks)}, "
                    f"extra={sorted(stable_tracks - critical)}",
                )
            )
        if stable.get("maturity_level") != maturity_ids[-1]:
            problems.append(
                RoadmapProblem(
                    "v1-maturity",
                    f"conductor/releases.json#{stable_version}",
                    f"stable release must require {maturity_ids[-1]}",
                )
            )
        if stable.get("channel") != "stable":
            problems.append(
                RoadmapProblem(
                    "v1-channel",
                    f"conductor/releases.json#{stable_version}",
                    "stable release must use the stable channel",
                )
            )
        stable_categories = {gate.get("category") for gate in stable.get("exit_gates", [])}
        missing_categories = dimension_set - stable_categories
        if missing_categories:
            problems.append(
                RoadmapProblem(
                    "v1-dimension-gates",
                    f"conductor/releases.json#{stable_version}",
                    f"stable release omits maturity dimensions: {sorted(missing_categories)}",
                )
            )

    gate_tracks = set(v1_gate.get("required_tracks", []))
    if gate_tracks != critical:
        problems.append(
            RoadmapProblem(
                "v1-gate-tracks",
                "conductor/v1-gate.json",
                f"required tracks differ from v1-critical tracks: "
                f"missing={sorted(critical - gate_tracks)}, extra={sorted(gate_tracks - critical)}",
            )
        )
    if set(v1_gate.get("required_dimensions", [])) != dimension_set:
        problems.append(
            RoadmapProblem(
                "v1-gate-dimensions",
                "conductor/v1-gate.json",
                "required dimensions must exactly match the maturity model",
            )
        )
    if v1_gate.get("release") != stable_version:
        problems.append(
            RoadmapProblem(
                "v1-gate-release",
                "conductor/v1-gate.json",
                "global gate release must match the stable release",
            )
        )
    if stable:
        stable_gate_ids = {gate["id"] for gate in stable.get("exit_gates", [])}
        if set(v1_gate.get("required_gate_ids", [])) != stable_gate_ids:
            problems.append(
                RoadmapProblem(
                    "v1-gate-ids",
                    "conductor/v1-gate.json",
                    "required gate IDs must exactly match stable release exit gates",
                )
            )
        if v1_gate.get("required_maturity") != stable.get("maturity_level"):
            problems.append(
                RoadmapProblem(
                    "v1-gate-maturity",
                    "conductor/v1-gate.json",
                    "required maturity must match stable release maturity",
                )
            )
    if v1_gate.get("required_maturity") != maturity_ids[-1]:
        problems.append(
            RoadmapProblem(
                "v1-gate-highest-maturity",
                "conductor/v1-gate.json",
                f"stable v1 must require the highest maturity {maturity_ids[-1]}",
            )
        )

    hardening_id = "v1_release_hardening_20260719"
    if hardening_id in tracks:
        expected = critical - {hardening_id}
        actual = set(tracks[hardening_id].get("depends_on", []))
        if actual != expected:
            problems.append(
                RoadmapProblem(
                    "v1-hardening-closure",
                    tracks[hardening_id].get("_path", hardening_id),
                    f"release hardening must depend on every other v1-critical track: "
                    f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}",
                )
            )

    _validate_release_evidence(base, release_plan, evidence_schema, v1_gate, problems)

    if check_generated_issues:
        issue_path = base / "project/issues.yaml"
        if not issue_path.is_file():
            problems.append(
                RoadmapProblem(
                    "missing-file", issue_path.as_posix(), "generated issue configuration is absent"
                )
            )
        else:
            expected_issues = generate_issue_configuration(base)
            try:
                actual = _load(issue_path)
            except (OSError, json.JSONDecodeError) as exc:
                problems.append(RoadmapProblem("issue-load", issue_path.as_posix(), str(exc)))
            else:
                if actual != expected_issues:
                    problems.append(
                        RoadmapProblem(
                            "issue-drift",
                            issue_path.as_posix(),
                            "run `riopa roadmap generate-issues`",
                        )
                    )

    return tuple(problems)


def generate_issue_configuration(root: str | Path) -> dict[str, Any]:
    """Generate deterministic programme, track, and phase issues from Conductor files."""

    base = Path(root).resolve()
    tracks = {
        track_id: metadata
        for track_id, metadata in load_tracks(base).items()
        if metadata.get("status") != "archived"
    }
    releases = _load(base / "conductor/releases.json")
    programme_version = releases["programme_version"]
    stable_release = releases["stable_release"]
    issues: list[dict[str, Any]] = [
        {
            "key": "program-epic",
            "title": "[Program] RIOPA stable, hardened and supported v1.0",
            "labels": [
                "type:program",
                "v1-critical",
                "provenance",
                "geospatial",
                "maturity:m1",
                f"release:{stable_release}",
            ],
            "body": (
                "Deliver a stable, hardened, independently reproducible and supported RIOPA v1.0: "
                "the provenance/publication platform, New Zealand spatial and planning reference "
                "implementation, accessibility and decision engines, and bounded public pilots.\n\n"
                "## Stable v1 contract\n\n"
                "- Machine-readable maturity, release and global v1 gates.\n"
                "- Every v1-critical track at its target maturity with linked evidence.\n"
                "- Signed releases, clean-room reproduction, external-user validation and "
                "preservation.\n"
                "- Measured operations, performance, recovery, compatibility, security and "
                "support.\n"
                "- Public coverage, uncertainty and limitation reports; no implied legal, clinical "
                "or operational authority.\n\n"
                "## Programme evidence\n\n"
                "- `PROGRAMME_PLAN.md`\n"
                "- `docs/v1-maturity-model.md`\n"
                "- `docs/v1-release-gates.md`\n"
                "- `conductor/tracks.md`\n"
                "- `conductor/releases.json`\n"
                "- `conductor/v1-gate.json`\n\n"
                f"Roadmap configuration version: `{programme_version}`."
            ),
            "project": True,
            "mirror_to_umbrella": True,
            "target_release": stable_release,
            "current_maturity": "M1",
            "maturity_target": "M6",
            "risk": "Critical",
            "stability_class": "Governance",
            "v1_critical": True,
            "priority": "P0",
            "owner_repository": "edithatogo/riopa-infrastructure",
        }
    ]

    sorted_tracks = sorted(
        tracks.items(),
        key=lambda pair: (_semver_key(pair[1]["target_release"]), pair[1]["phase"], pair[0]),
    )
    for track_id, metadata in sorted_tracks:
        track_dir = _track_directory(metadata)
        relative_track_dir = track_dir.relative_to(base).as_posix()
        spec_path = track_dir / "spec.md"
        plan_path = track_dir / "plan.md"
        spec = spec_path.read_text(encoding="utf-8")
        plan = plan_path.read_text(encoding="utf-8")
        title_match = re.search(r"^# Track:\s*(.+?)\s*$", spec, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else track_id
        goal = _section(spec, "Goal")
        acceptance = CHECKBOX_RE.findall(_section(spec, "Acceptance criteria"))
        phase_slug = PHASE_SLUGS[metadata["phase"]]
        labels = [
            "type:track",
            f"phase:{phase_slug}",
            f"maturity:{metadata['current_maturity'].lower()}",
            f"release:{metadata['target_release']}",
            _risk_label(metadata["risk"]),
            _stability_label(metadata["stability_class"]),
        ]
        if metadata.get("v1_critical"):
            labels.append("v1-critical")
        if "provenance" in metadata.get("maturity_dimensions", []):
            labels.append("provenance")
        if any(
            value in metadata.get("maturity_dimensions", [])
            for value in ("data", "analytics", "performance")
        ):
            labels.append("geospatial")
        if any(
            value in metadata.get("maturity_dimensions", []) for value in ("governance", "security")
        ):
            labels.append("rights-governance")

        dependency_text = (
            "\n".join(f"- `{value}`" for value in metadata.get("depends_on", [])) or "- None."
        )
        acceptance_text = "\n".join(f"- [ ] {value}" for value in acceptance)
        parent_body = (
            f"Conductor track: `{track_id}`  \n"
            f"Phase: **{metadata['phase']}**  \n"
            f"Target release: **{metadata['target_release']}**  \n"
            f"Current maturity: **{metadata['current_maturity']}**  \n"
            f"Maturity target: **{metadata['maturity_target']}**  \n"
            f"Stability class: **{metadata['stability_class']}**\n\n"
            f"## Goal\n\n{goal}\n\n"
            f"## Dependencies\n\n{dependency_text}\n\n"
            f"## Acceptance criteria\n\n{acceptance_text}\n\n"
            "## Source of truth\n\n"
            f"- `{relative_track_dir}/spec.md`\n"
            f"- `{relative_track_dir}/plan.md`\n"
            f"- `{relative_track_dir}/metadata.json`\n"
            f"- `{relative_track_dir}/index.md`"
        )
        common_fields = {
            "project": True,
            "phase": metadata["phase"],
            "track_id": track_id,
            "target_release": metadata["target_release"],
            "current_maturity": metadata["current_maturity"],
            "maturity_target": metadata["maturity_target"],
            "risk": metadata["risk"],
            "stability_class": metadata["stability_class"],
            "v1_critical": metadata["v1_critical"],
            "priority": metadata["priority"],
            "owner_repository": metadata["owner_repository"],
            "owner_role": metadata.get("owner_role"),
            "blocking_defects": len(metadata.get("blocking_defects", [])),
        }
        issues.append(
            {
                "key": track_id,
                "title": f"[Track] {title}",
                "parent": "program-epic",
                "blocked_by": metadata.get("depends_on", []),
                "labels": list(dict.fromkeys(labels)),
                "body": parent_body,
                "mirror_to_umbrella": bool(metadata.get("mirror_to_umbrella", False)),
                **common_fields,
            }
        )

        phases = _plan_phases(plan)
        previous_key: str | None = None
        for index, phase in enumerate(phases):
            key = f"{track_id}:phase-{phase['number']}"
            blocked_by = [previous_key] if previous_key else []
            task_text = "\n".join(f"- [ ] {task}" for task in phase["tasks"])
            issues.append(
                {
                    "key": key,
                    "title": f"[{track_id}] {phase['number']}. {phase['title']}",
                    "parent": track_id,
                    "blocked_by": blocked_by,
                    "labels": [
                        "type:validation" if index == len(phases) - 1 else "type:implementation",
                        f"phase:{phase_slug}",
                        _risk_label(metadata["risk"]),
                        f"maturity:{metadata['current_maturity'].lower()}",
                        f"release:{metadata['target_release']}",
                    ],
                    "body": (
                        f"Implementation phase for Conductor track `{track_id}`.\n\n"
                        f"## Tasks\n\n{task_text}\n\n"
                        "## Evidence\n\n"
                        "Link code, tests, reports, decisions, migrations and immutable release "
                        f"artifacts in `{relative_track_dir}/index.md` before closing."
                    ),
                    "mirror_to_umbrella": False,
                    **common_fields,
                }
            )
            previous_key = key

    return {"version": 3, "programme_version": programme_version, "issues": issues}


def write_issue_configuration(root: str | Path, output: str | Path | None = None) -> Path:
    """Write generated GitHub issue configuration."""

    base = Path(root).resolve()
    path = Path(output).resolve() if output else base / "project/issues.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(generate_issue_configuration(base), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def _waiver_is_current(gate: dict[str, Any], now: datetime) -> bool:
    waiver = gate.get("waiver") or {}
    try:
        return bool(waiver.get("reason")) and _parse_datetime(waiver["expires_at"]) > now
    except KeyError, TypeError, ValueError:
        return False


def release_readiness(root: str | Path, version: str) -> ReleaseReadiness:
    """Calculate conservative, stage-aware readiness for one release."""

    base = Path(root).resolve()
    tracks = load_tracks(base)
    plan = _load(base / "conductor/releases.json")
    v1_gate = _load(base / "conductor/v1-gate.json")
    release = next((item for item in plan["releases"] if item["version"] == version), None)
    if release is None:
        raise ValueError(f"unknown release: {version}")

    required_level = release["maturity_level"]
    required_rank = _maturity_rank(required_level)
    required_tracks = release.get("required_tracks", [])
    qualified: list[str] = []
    blockers: list[str] = []
    for track_id in required_tracks:
        track = tracks.get(track_id)
        if not track:
            blockers.append(f"track {track_id} is missing")
            continue
        current_level = track.get("current_maturity", "M0")
        if required_rank < 6 and track.get("status") == "proposed":
            blockers.append(
                f"track {track_id} status {track.get('status')} is incompatible with the release"
            )
            continue
        if _maturity_rank(current_level) < required_rank:
            blockers.append(f"track {track_id} is {current_level}; {required_level} is required")
            continue
        defect_maturity = track.get("blocking_defect_maturity", {})
        applicable_defects = [
            defect
            for defect in track.get("blocking_defects", [])
            if required_rank
            >= _maturity_rank(
                defect_maturity.get(defect, "M0") if isinstance(defect_maturity, dict) else "M0"
            )
        ]
        if applicable_defects:
            blockers.append(f"track {track_id} has blocking defects")
            continue
        if required_rank >= 2 and not track.get("evidence"):
            blockers.append(f"track {track_id} has no linked implementation evidence")
            continue
        if required_rank == 6 and track.get("status") not in {"complete", "archived"}:
            blockers.append(
                f"track {track_id} is {track.get('status')}; complete or archived is required "
                "for stable v1"
            )
            continue
        incomplete_dependencies = [
            dependency
            for dependency in track.get("depends_on", [])
            if _maturity_rank(tracks.get(dependency, {}).get("current_maturity", "M0"))
            < required_rank
        ]
        if incomplete_dependencies:
            blockers.append(
                f"track {track_id} has dependencies below {required_level}: "
                f"{incomplete_dependencies}"
            )
            continue
        qualified.append(track_id)

    gate_status: dict[str, dict[str, Any]] = {}
    evidence_payload: dict[str, Any] | None = None
    evidence_path = base / "conductor/release-evidence" / f"{version}.json"
    if evidence_path.is_file():
        try:
            loaded_evidence = _load(evidence_path)
        except (OSError, json.JSONDecodeError) as exc:
            blockers.append(f"release evidence cannot be read: {exc}")
        else:
            if isinstance(loaded_evidence, dict):
                evidence_payload = loaded_evidence
                gate_status = {
                    item["gate_id"]: item
                    for item in evidence_payload.get("gates", [])
                    if isinstance(item, dict) and isinstance(item.get("gate_id"), str)
                }
            else:
                blockers.append("release evidence is not a JSON object")

    required_gates = [gate for gate in release.get("exit_gates", []) if gate.get("blocking", True)]
    passed_gates = 0
    now = datetime.now(UTC)
    non_waivable = set(v1_gate.get("waiver_policy", {}).get("non_waivable_categories", []))
    max_age = v1_gate.get("evidence_policy", {}).get("maximum_gate_evidence_age_days")
    for gate in required_gates:
        item = gate_status.get(gate["id"])
        if not item:
            blockers.append(f"gate {gate['id']} is not passed with current evidence")
            continue
        status = item.get("status")
        if status == "passed" and item.get("evidence"):
            reviewed_at = item.get("reviewed_at")
            expires_at = item.get("expires_at")
            if version == plan["stable_release"] and (not reviewed_at or not item.get("reviewer")):
                blockers.append(f"gate {gate['id']} lacks stable review evidence")
                continue
            try:
                if expires_at and _parse_datetime(expires_at) <= now:
                    blockers.append(f"gate {gate['id']} evidence has expired")
                    continue
                if version == plan["stable_release"] and max_age and reviewed_at:
                    age_days = (now - _parse_datetime(reviewed_at)).days
                    if age_days > max_age:
                        blockers.append(f"gate {gate['id']} evidence is {age_days} days old")
                        continue
            except TypeError, ValueError:
                blockers.append(f"gate {gate['id']} has invalid evidence dates")
                continue
            passed_gates += 1
            continue
        if status == "waived" and item.get("evidence") and _waiver_is_current(item, now):
            waiver = item.get("waiver") or {}
            waiver_category = waiver.get("category")
            if version == plan["stable_release"] and (
                not item.get("reviewed_at") or not item.get("reviewer")
            ):
                blockers.append(f"gate {gate['id']} lacks stable review evidence")
                continue
            try:
                if version == plan["stable_release"] and max_age:
                    age_days = (now - _parse_datetime(item["reviewed_at"])).days
                    if age_days > max_age:
                        blockers.append(f"gate {gate['id']} evidence is {age_days} days old")
                        continue
                created_at = _parse_datetime(waiver["created_at"])
                expires_at = _parse_datetime(waiver["expires_at"])
                duration_days = (expires_at - created_at).days
            except KeyError, TypeError, ValueError:
                blockers.append(f"gate {gate['id']} has invalid waiver dates")
                continue
            maximum_duration = v1_gate.get("waiver_policy", {}).get("maximum_duration_days", 90)
            if duration_days < 0 or duration_days > maximum_duration:
                blockers.append(
                    f"gate {gate['id']} waiver duration is {duration_days} days; "
                    f"maximum is {maximum_duration}"
                )
                continue
            if waiver_category in non_waivable:
                blockers.append(f"gate {gate['id']} uses non-waivable category {waiver_category}")
                continue
            passed_gates += 1
            continue
        blockers.append(f"gate {gate['id']} is not passed with current evidence")

    if version == plan["stable_release"]:
        if not evidence_payload:
            blockers.append("stable release evidence record is absent")
        else:
            evidence_policy = v1_gate.get("evidence_policy", {})
            if evidence_policy.get(
                "machine_readable_evidence_required"
            ) and not evidence_payload.get("machine_readable"):
                blockers.append("stable evidence is not declared machine-readable")
            if evidence_policy.get(
                "immutable_evidence_identifiers_required"
            ) and not evidence_payload.get("immutable_evidence_identifiers"):
                blockers.append("stable evidence does not require immutable identifiers")

            source_revision = str(evidence_payload.get("source_revision", ""))
            if not source_revision or source_revision.startswith("uncommitted:"):
                blockers.append("stable source revision is absent or not immutable")

            defects = evidence_payload.get("defects", {})
            for policy_field, maximum in v1_gate.get("defect_policy", {}).items():
                evidence_field = policy_field.removeprefix("maximum_")
                value = defects.get(evidence_field) if isinstance(defects, dict) else None
                if value is None:
                    blockers.append(f"stable defect metric {evidence_field} is missing")
                elif value > maximum:
                    blockers.append(
                        f"stable defect metric {evidence_field}={value} exceeds {maximum}"
                    )

            metrics = evidence_payload.get("metrics", {})
            for policy_field, minimum in evidence_policy.items():
                if not policy_field.startswith("minimum_"):
                    continue
                evidence_field = policy_field.removeprefix("minimum_")
                value = metrics.get(evidence_field) if isinstance(metrics, dict) else None
                if value is None:
                    blockers.append(f"stable evidence metric {evidence_field} is missing")
                elif value < minimum:
                    blockers.append(
                        f"stable evidence metric {evidence_field}={value} is below {minimum}"
                    )

            stable_references: list[Any] = []
            for gate in gate_status.values():
                evidence = gate.get("evidence", [])
                if isinstance(evidence, list):
                    stable_references.extend(evidence)
            release_artifacts = evidence_payload.get("release_artifacts", [])
            if isinstance(release_artifacts, list):
                stable_references.extend(release_artifacts)
            if not release_artifacts:
                blockers.append("stable release has no immutable release artifacts")
            for reference in stable_references:
                identifier = _evidence_identifier(reference)
                location = _evidence_location(reference)
                if (
                    not isinstance(reference, dict)
                    or not reference.get("immutable")
                    or not identifier
                ):
                    blockers.append(
                        "stable evidence reference is not immutable: "
                        f"{identifier or location or '<unknown>'}"
                    )
                    continue
                digest = reference.get("sha256")
                is_external = location.startswith(("http://", "https://", "urn:", "doi:", "swh:"))
                if not is_external and not digest:
                    blockers.append(f"stable local evidence lacks a verified digest: {identifier}")
                elif (
                    is_external
                    and not digest
                    and not identifier.startswith(("doi:", "swh:", "urn:sha256:"))
                ):
                    blockers.append(
                        "stable external evidence lacks a digest or content-addressed "
                        f"persistent identifier: {identifier}"
                    )

            required_roles = set(v1_gate.get("release_authority", {}).get("required_roles", []))
            authority_policy = v1_gate.get("release_authority", {})
            stable_reference_ids = {
                _evidence_identifier(reference)
                for reference in stable_references
                if isinstance(reference, dict)
            }
            panel_manifest_ref = evidence_payload.get("agent_panel_manifest_ref")
            if authority_policy.get("agent_panel_advice_required") and (
                not panel_manifest_ref or panel_manifest_ref not in stable_reference_ids
            ):
                blockers.append(
                    "stable release agent-panel manifest is missing from immutable evidence"
                )
            required_panel_roles = set(authority_policy.get("required_panel_roles", []))
            observed_panel_roles = set(evidence_payload.get("agent_panel_roles", []))
            missing_panel_roles = required_panel_roles - observed_panel_roles
            if missing_panel_roles:
                blockers.append(
                    f"stable release agent-panel roles are missing: {sorted(missing_panel_roles)}"
                )
            owner_disposition_ref = evidence_payload.get("owner_dissent_disposition_ref")
            if authority_policy.get("owner_disposition_of_dissent_required") and (
                not owner_disposition_ref or owner_disposition_ref not in stable_reference_ids
            ):
                blockers.append(
                    "stable release owner dissent disposition is missing from immutable evidence"
                )
            approvals = [
                approval
                for approval in evidence_payload.get("approvals", [])
                if isinstance(approval, dict) and approval.get("decision") == "approve"
            ]
            approved_roles = {approval.get("role") for approval in approvals}
            missing_roles = required_roles - approved_roles
            if missing_roles:
                blockers.append(f"stable release approvals missing roles: {sorted(missing_roles)}")
            if authority_policy.get("signed_decision_required"):
                unsigned_roles = sorted(
                    str(approval.get("role"))
                    for approval in approvals
                    if not approval.get("signed_decision_ref")
                )
                if unsigned_roles:
                    blockers.append(f"stable release approvals are unsigned: {unsigned_roles}")

    return ReleaseReadiness(
        version=version,
        name=release["name"],
        maturity_level=release["maturity_level"],
        ready=not blockers,
        qualified_tracks=len(qualified),
        required_tracks=len(required_tracks),
        passed_gates=passed_gates,
        required_gates=len(required_gates),
        blockers=tuple(blockers),
    )


def roadmap_status(root: str | Path, release: str | None = None) -> dict[str, Any]:
    """Return a machine-readable programme and release status summary."""

    base = Path(root).resolve()
    tracks = load_tracks(base)
    plan = _load(base / "conductor/releases.json")
    versions: Iterable[str] = (
        [release] if release else [item["version"] for item in plan["releases"]]
    )
    readiness = [release_readiness(base, version) for version in versions]
    return {
        "programme_version": plan["programme_version"],
        "current_release": plan["current_release"],
        "stable_release": plan["stable_release"],
        "tracks": {
            "total": len(tracks),
            "by_status": dict(sorted(Counter(item["status"] for item in tracks.values()).items())),
            "by_current_maturity": dict(
                sorted(Counter(item["current_maturity"] for item in tracks.values()).items())
            ),
            "by_target_release": dict(
                sorted(
                    Counter(item["target_release"] for item in tracks.values()).items(),
                    key=lambda item: _semver_key(item[0]),
                )
            ),
            "v1_critical": sum(1 for item in tracks.values() if item.get("v1_critical")),
        },
        "releases": [
            {
                "version": item.version,
                "name": item.name,
                "maturity_level": item.maturity_level,
                "ready": item.ready,
                "qualified_tracks": item.qualified_tracks,
                "required_tracks": item.required_tracks,
                "passed_gates": item.passed_gates,
                "required_gates": item.required_gates,
                "blockers": list(item.blockers),
            }
            for item in readiness
        ],
    }


def render_status_markdown(status: dict[str, Any]) -> str:
    """Render roadmap status without implying that planned gates have passed."""

    lines = [
        "# RIOPA Roadmap Status",
        "",
        f"Programme configuration: `{status['programme_version']}`  ",
        f"Current roadmap release: `{status['current_release']}`  ",
        f"Stable target: `{status['stable_release']}`",
        "",
        "## Tracks",
        "",
        f"- Total: **{status['tracks']['total']}**",
        f"- v1-critical: **{status['tracks']['v1_critical']}**",
    ]
    for key, value in status["tracks"]["by_status"].items():
        lines.append(f"- {key}: **{value}**")
    lines.extend(["", "### Current maturity", ""])
    for key, value in status["tracks"]["by_current_maturity"].items():
        lines.append(f"- `{key}`: **{value}**")
    lines.extend(["", "## Release readiness", ""])
    for release in status["releases"]:
        state = "READY" if release["ready"] else "NOT READY"
        lines.extend(
            [
                f"### {release['version']} — {release['name']} ({state})",
                "",
                f"- Maturity gate: `{release['maturity_level']}`",
                f"- Tracks qualified: {release['qualified_tracks']}/{release['required_tracks']}",
                f"- Gates: {release['passed_gates']}/{release['required_gates']} passed",
            ]
        )
        if release["blockers"]:
            lines.append("- Blockers:")
            lines.extend(f"  - {blocker}" for blocker in release["blockers"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
