from pathlib import Path

from scripts.check_tracked_secrets import secret_findings
from scripts.check_workflow_lint import workflow_lint_errors

ROOT = Path(__file__).resolve().parents[1]


def test_repository_workflows_satisfy_portable_lint_contract() -> None:
    assert workflow_lint_errors(ROOT) == []


def test_repository_has_no_high_confidence_tracked_credentials() -> None:
    assert secret_findings(ROOT) == []


def test_workflow_lint_rejects_missing_timeout(tmp_path: Path) -> None:
    workflow = tmp_path / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "bad.yml").write_text(
        "name: bad\non: [push]\npermissions: {contents: read}\n"
        "jobs:\n  test:\n    steps: [{run: echo ok}]\n",
        encoding="utf-8",
    )
    assert any("timeout-minutes" in error for error in workflow_lint_errors(tmp_path))


def test_secret_scan_detects_private_key(tmp_path: Path) -> None:
    (tmp_path / "secret.txt").write_text(
        "-----BEGIN " + "PRIVATE KEY-----\nnot-a-key\n", encoding="utf-8"
    )
    (tmp_path / ".git").mkdir()
    import subprocess

    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "secret.txt"], check=True)
    assert any("private key" in error for error in secret_findings(tmp_path))
