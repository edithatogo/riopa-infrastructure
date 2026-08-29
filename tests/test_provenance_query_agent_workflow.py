import json
import subprocess
import sys
from pathlib import Path


def test_bounded_provenance_query_agent_workflow_preserves_external_gate() -> None:
    root = Path(__file__).parents[1]
    output = root / ".tmp-provenance-query-agent-workflow.json"
    database = root / ".tmp-provenance-query-agent-workflow.sqlite"
    try:
        subprocess.run(
            [
                sys.executable,
                "scripts/run_provenance_query_agent_workflow.py",
                "--manifest",
                "examples/minimal/snapshot-manifest.json",
                "--schema-dir",
                "schemas",
                "--database",
                str(database),
                "--output",
                str(output),
            ],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads(output.read_text(encoding="utf-8"))
        assert report["status"] == "bounded-local-agent-workflow"
        assert [item["question"] for item in report["questions"]] == ["where", "why", "how"]
        assert all(item["has_projection_diagnostic"] for item in report["questions"])
        assert report["claim_classification"] == "repository-reference-only"
        assert report["promotion_allowed"] is False
        assert "owner-authorized agent-operated user/operator workflows" in report["open_gates"]
    finally:
        output.unlink(missing_ok=True)
        database.unlink(missing_ok=True)
