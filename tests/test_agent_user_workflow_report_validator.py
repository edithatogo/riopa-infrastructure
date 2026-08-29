import json
from pathlib import Path

from scripts.run_agent_user_workflows import run
from scripts.validate_agent_user_workflow_report import validate_report

ROOT = Path(__file__).resolve().parents[1]


def test_agent_workflow_report_has_bounded_shape(tmp_path: Path) -> None:
    report = run(tmp_path)
    assert validate_report(report) == ()


def test_agent_workflow_report_rejects_duplicate_workflows(tmp_path: Path) -> None:
    report = run(tmp_path)
    report["workflows"][1]["workflow_id"] = report["workflows"][0]["workflow_id"]
    assert any("must be unique" in error for error in validate_report(report))


def test_agent_workflow_report_rejects_missing_nonclaims() -> None:
    report = json.loads(
        (ROOT / "docs/v1-agent-operated-journeys-20260825.json").read_text(encoding="utf-8")
    )
    assert any("external participant boundary" in error for error in validate_report(report))


def test_agent_workflow_report_rejects_status_exit_mismatch(tmp_path: Path) -> None:
    report = run(tmp_path)
    report["workflows"][0]["status"] = "passed"
    report["workflows"][0]["exit_code"] = 1
    assert any("requires exit_code 0" in error for error in validate_report(report))


def test_agent_workflow_report_rejects_non_string_command_and_bool_exit(tmp_path: Path) -> None:
    report = run(tmp_path)
    report["workflows"][0]["command"] = ["python", {"argv": "bad"}]
    report["workflows"][0]["exit_code"] = False
    errors = validate_report(report)
    assert any("command must contain non-empty strings" in error for error in errors)
    assert any("exit_code must be an integer" in error for error in errors)


def test_agent_workflow_report_rejects_non_object() -> None:
    assert validate_report([]) == ("report must be a JSON object",)
