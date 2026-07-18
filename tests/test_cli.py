from __future__ import annotations

from pathlib import Path

import pytest

from riopa_provenance import cli
from riopa_provenance.validation import ValidationResult


def test_validate_command_reports_success(capsys: pytest.CaptureFixture[str]) -> None:
    root = Path(__file__).resolve().parents[1]
    with pytest.raises(SystemExit) as exc:
        cli.main(["validate", "--root", str(root)])
    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "PASS" in output
    assert "0 failure(s)" in output


def test_validate_command_reports_failures(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    results = [
        ValidationResult(tmp_path / "valid.json", None, ()),
        ValidationResult(tmp_path / "invalid.json", None, ("broken", "also broken")),
    ]
    monkeypatch.setattr(cli, "validate_bundle", lambda _root: results)
    with pytest.raises(SystemExit) as exc:
        cli.main(["validate", "--root", str(tmp_path)])
    assert exc.value.code == 1
    output = capsys.readouterr().out
    assert "PASS" in output
    assert "FAIL" in output
    assert "broken" in output
    assert "1 failure(s)" in output


def test_methods_command_writes_output(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "nested" / "METHODS.md"
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "methods",
                "--manifest",
                str(root / "examples/minimal/snapshot-manifest.json"),
                "--output",
                str(output),
            ]
        )
    assert exc.value.code == 0
    assert "Citable methods statement" in output.read_text(encoding="utf-8")
    assert "Methods written" in capsys.readouterr().out


def test_research_object_command_writes_output(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "research-object"
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "research-object",
                "--manifest",
                str(root / "examples/minimal/snapshot-manifest.json"),
                "--output-dir",
                str(output),
            ]
        )
    assert exc.value.code == 0
    assert (output / "ro-crate-metadata.json").is_file()
    assert "Research object written" in capsys.readouterr().out
