from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
DECISION = ROOT / "docs/v0.2.0-technical-preview-release-decision-20260826.json"
ARTIFACT_ROOT = ROOT / "conductor/release-evidence/artifacts/0.2.0"
EXPECTED_SOURCE_REVISION = "4ffe73eb144c5c1a4acad34706a5f5937491d1ad"
PRESERVED_FILES = (
    ".github/workflows/validate.yml",
    "PROGRAMME_PLAN.md",
    "ROADMAP_STATUS.md",
    "conductor/maturity-model.json",
    "conductor/releases.json",
    "conductor/tracks.md",
    "conductor/v1-gate.json",
    "docs/risk-register.md",
    "docs/v1-definition-of-done.md",
    "docs/v1-evidence-and-waiver-policy.md",
    "project/issues.yaml",
    "project/project.yaml",
    "src/riopa_provenance/roadmap.py",
    "tests/test_roadmap.py",
    "tests/test_roadmap_hardening.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_bounded_release_decision_preserves_later_tracks() -> None:
    decision = json.loads(DECISION.read_text(encoding="utf-8"))

    assert decision["release"] == "0.2.0"
    assert decision["channel"] == "technical-preview"
    assert decision["maturity"] == "M1"
    assert decision["source_revision"] == EXPECTED_SOURCE_REVISION
    assert decision["later_track_policy"] == {
        "pre_existing_track_count": 28,
        "effect": "none",
        "requirement": (
            "All pre-existing tracks retain their status, maturity target, "
            "release target and acceptance criteria."
        ),
    }
    assert "stable-v1 readiness" in decision["excluded_claims"]
    assert "independent external reproduction" in decision["excluded_claims"]


def test_preserved_v020_snapshot_is_complete_and_nonempty() -> None:
    for relative_path in PRESERVED_FILES:
        preserved = ARTIFACT_ROOT / relative_path
        assert preserved.is_file(), relative_path
        assert _sha256(preserved) != hashlib.sha256(b"").hexdigest(), relative_path


def test_support_policy_keeps_preview_and_stable_support_separate() -> None:
    policy = (ROOT / "docs/v0.2.0-technical-preview-support-20260826.md").read_text(
        encoding="utf-8"
    )

    assert "twelve calendar months" in policy
    assert "does not convert experimental interfaces into stable contracts" in policy
    assert "does not delay or cancel later Conductor tracks" in policy
