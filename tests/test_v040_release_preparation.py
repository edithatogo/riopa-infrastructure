import json
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

import riopa_provenance

ROOT = Path(__file__).resolve().parents[1]


def test_v040_software_versions_and_m2_boundary():
    assert tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"] == "0.4.0"
    assert riopa_provenance.__version__ == "0.4.0"
    assert yaml.safe_load((ROOT / "CITATION.cff").read_text())["version"] == "0.4.0"
    assert json.loads((ROOT / "codemeta.json").read_text())["version"] == "0.4.0"
    metadata = json.loads(
        (
            ROOT / "conductor/tracks/interoperability_conformance_sdks_20260719/metadata.json"
        ).read_text()
    )
    assert (metadata["status"], metadata["current_maturity"]) == ("validating", "M2")


def test_v040_tag_and_conformance_report(tmp_path):
    assert (
        subprocess.run(
            [sys.executable, "scripts/check_release_version.py", "--tag", "v0.4.0"], cwd=ROOT
        ).returncode
        == 0
    )
    output = tmp_path / "report.json"
    subprocess.run(
        [sys.executable, "scripts/build_release_conformance_report.py", str(output)],
        cwd=ROOT,
        check=True,
    )
    report = json.loads(output.read_text())
    assert report["release"] == "0.4.0"
    assert report["channel"] == "technical-preview"
    assert "results" not in report
    assert len(report["evidence_bindings"]) == 3
    assert all(binding["sha256"] for binding in report["evidence_bindings"])
    assert "not newly executed results" in report["interpretation"]
    assert report["limitations"]


def test_v040_report_fails_closed_for_missing_evidence(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_release_conformance_report.py",
            str(tmp_path / "report.json"),
            "--evidence",
            str(tmp_path / "missing.json"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "evidence receipt not found" in result.stderr


def test_v040_release_workflow_attests_conformance_report():
    workflow = (ROOT / ".github/workflows/release.yml").read_text()
    assert "scripts/build_release_conformance_report.py" in workflow
    assert "dist/release/riopa-conformance-report.json" in workflow
