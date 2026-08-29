import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _build(tmp_path: Path) -> Path:
    output = tmp_path / "report.json"
    subprocess.run(
        [sys.executable, "scripts/build_release_conformance_report.py", str(output)],
        cwd=ROOT,
        check=True,
    )
    return output


def test_release_conformance_report_validates_local_bindings(tmp_path: Path) -> None:
    report = _build(tmp_path)
    result = subprocess.run(
        [sys.executable, "scripts/validate_release_conformance_report.py", str(report)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_release_conformance_report_rejects_tampered_binding(tmp_path: Path) -> None:
    report = _build(tmp_path)
    payload = json.loads(report.read_text())
    payload["evidence_bindings"][0]["sha256"] = "0" * 64
    report.write_text(json.dumps(payload))
    result = subprocess.run(
        [sys.executable, "scripts/validate_release_conformance_report.py", str(report)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "does not match" in result.stdout


def test_release_conformance_report_rejects_path_escape(tmp_path: Path) -> None:
    report = _build(tmp_path)
    payload = json.loads(report.read_text())
    payload["evidence_bindings"][0]["path"] = "../outside.json"
    report.write_text(json.dumps(payload))
    result = subprocess.run(
        [sys.executable, "scripts/validate_release_conformance_report.py", str(report)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "escapes repository root" in result.stdout


def test_release_conformance_report_rejects_missing_boundary(tmp_path: Path) -> None:
    report = _build(tmp_path)
    payload = json.loads(report.read_text())
    payload.pop("limitations")
    report.write_text(json.dumps(payload))
    result = subprocess.run(
        [sys.executable, "scripts/validate_release_conformance_report.py", str(report)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "limitations" in result.stdout


def test_release_conformance_report_rejects_tampered_fixture_digest(tmp_path: Path) -> None:
    report = _build(tmp_path)
    payload = json.loads(report.read_text())
    payload["fixture_sha256"] = "0" * 64
    report.write_text(json.dumps(payload))
    result = subprocess.run(
        [sys.executable, "scripts/validate_release_conformance_report.py", str(report)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "fixture_sha256 does not match" in result.stdout
