import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_applied_benchmark_reproduction_preserves_projection_boundary() -> None:
    record = json.loads(
        (ROOT / "docs/publication-applied-benchmark-reproduction-20260825.json").read_text(
            encoding="utf-8"
        )
    )
    assert record["status"] == "owner-agent-reproduced-bounded-benchmark"
    assert record["execution"]["result"] == "pass"
    assert record["execution"]["network_contacted"] is False
    assert record["execution"]["independent"] is False
    assert record["interpretation"]["national"] == "projection-not-measurement"
    assert record["promotion_allowed"] is False
    assert len(record["benchmark"]["run_log_sha256"]) == 64
    assert any("national-scale" in gate for gate in record["open_gates"])
