import json
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

import riopa_provenance
from riopa_provenance.roadmap import release_readiness

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.3.0"


def test_current_software_versions_are_synchronized_after_v030() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    codemeta = json.loads((ROOT / "codemeta.json").read_text(encoding="utf-8"))
    releases = json.loads((ROOT / "conductor/releases.json").read_text(encoding="utf-8"))
    programme_releases = json.loads((ROOT / "programme/releases.json").read_text(encoding="utf-8"))
    setup = json.loads((ROOT / "conductor/setup_state.json").read_text(encoding="utf-8"))

    assert pyproject["project"]["version"] == "0.4.0"
    assert riopa_provenance.__version__ == "0.4.0"
    assert citation["version"] == "0.4.0"
    assert str(citation["date-released"]) == "2026-08-29"
    assert codemeta["version"] == "0.4.0"
    assert releases["programme_version"] == releases["current_release"] == VERSION
    assert programme_releases == releases
    assert setup["programme_version"] == VERSION
    assert setup["current_maturity"] == "M2"


def test_v030_readiness_remains_historical_and_current_tag_matches() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/check_release_version.py"),
            "--tag",
            "v0.4.0",
            "--pyproject",
            str(ROOT / "pyproject.toml"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Release tag matches package version: v0.4.0" in result.stdout
    assert release_readiness(ROOT, VERSION).ready is True
    for version in ("0.4.0", "0.5.0", "0.6.0", "0.7.0", "0.8.0", "0.9.0", "1.0.0"):
        readiness = release_readiness(ROOT, version)
        assert readiness.ready is False
        assert readiness.blockers


def test_v030_release_notes_preserve_nonclaims() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    section = changelog.split("## 0.3.0 — 2026-08-27", maxsplit=1)[1].split(
        "## Unreleased handoff", maxsplit=1
    )[0]
    normalized = " ".join(section.split())

    assert "five required tracks and four" in normalized
    assert "without waivers" in normalized
    assert "independent external reproduction" in normalized
    assert "All five core tracks remain `validating` toward M6 and unarchived" in normalized


def test_v0_tags_are_published_as_github_prereleases() -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")

    checkout = workflow.index("Check out tagged source for tag verification")
    download = workflow.index("Download verified release candidate", checkout)
    publish = workflow.index("Publish GitHub release", download)
    assert checkout < download < publish
    assert '[[ "$RELEASE_TAG" == v0.* || "$RELEASE_TAG" == *-* ]]' in workflow
    assert "release_flags+=(--prerelease)" in workflow
    assert '"${release_flags[@]}"' in workflow
