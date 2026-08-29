import hashlib
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
    assert len(report["source_revision"]) == 40
    assert all(char in "0123456789abcdef" for char in report["source_revision"])
    for binding in report["evidence_bindings"]:
        evidence_path = ROOT / binding["path"]
        assert evidence_path.is_file()
        assert binding["sha256"] == hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    assert "not newly executed results" in report["interpretation"]
    assert report["limitations"]

    repeat = tmp_path / "report-repeat.json"
    subprocess.run(
        [sys.executable, "scripts/build_release_conformance_report.py", str(repeat)],
        cwd=ROOT,
        check=True,
    )
    assert output.read_bytes() == repeat.read_bytes()


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


def test_v040_report_accepts_workflow_relative_evidence_paths(tmp_path):
    output = tmp_path / "report.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/build_release_conformance_report.py",
            str(output),
            "--evidence",
            "docs/rust-corpus-parity-20260825.json",
        ],
        cwd=ROOT,
        check=True,
    )
    binding = json.loads(output.read_text())["evidence_bindings"][0]
    assert binding["path"] == "docs/rust-corpus-parity-20260825.json"


def test_v040_release_workflow_attests_conformance_report():
    workflow = (ROOT / ".github/workflows/release.yml").read_text()
    assert "scripts/build_release_conformance_report.py" in workflow
    assert "dist/release/riopa-conformance-report.json" in workflow


def test_v040_publication_receipt_preserves_preview_boundaries():
    receipt = json.loads((ROOT / "docs/v0.4.0-release-publication-20260829.json").read_text())
    assert receipt["release_workflow"]["conclusion"] == "success"
    assert len(receipt["assets"]) == 6
    assert receipt["post_publication_verification"]["all_six_oidc_attestations_verified"]
    assert receipt["post_publication_verification"]["ro_crate_1_2_required_checks"] == {
        "passed": 65,
        "failed": 0,
        "total": 65,
    }
    assert receipt["preservation"]["zenodo"].startswith("not_attempted")
    assert receipt["preservation"]["hugging_face"].startswith("not_attempted")
    assert any("90-day beta" in claim for claim in receipt["non_claims"])


def test_v040_mirror_receipt_is_a_successor_record() -> None:
    receipt_path = ROOT / "docs/v0.4.0-release-publication-20260829.json"
    mirror = json.loads((ROOT / "docs/v0.4.0-release-mirror-20260829.json").read_text())
    assert mirror["source_publication_receipt"] == {
        "path": "docs/v0.4.0-release-publication-20260829.json",
        "sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
    }
    assert mirror["mirror"]["release_assets"] == 6
    assert mirror["mirror"]["public_anonymous_byte_matches"] == 7
    assert mirror["mirror"]["sha256sums_passed"] is True
    assert mirror["qualification"]["classification"] == "byte_preserving_public_mirror"
