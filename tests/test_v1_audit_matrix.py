import json
from pathlib import Path


def test_v1_repository_audit_matrix_covers_required_domains_fail_closed() -> None:
    root = Path(__file__).resolve().parents[1]
    matrix = json.loads((root / "docs/v1-repository-audit-matrix-20260825.json").read_text())
    assert matrix["status"] == "bounded-repository-audit-complete-external-gates-pending"
    domains = {audit["domain"] for audit in matrix["audits"]}
    assert domains == {"security", "performance", "accessibility", "governance", "documentation"}
    assert all(audit["evidence"] and audit["open_gates"] for audit in matrix["audits"])
    assert matrix["non_claims"]
