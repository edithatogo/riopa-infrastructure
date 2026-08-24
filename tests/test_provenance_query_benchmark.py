from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_local_lineage_query_benchmark_is_explicitly_bounded(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "benchmark.json"
    subprocess.run(
        [
            sys.executable,
            "scripts/benchmark_lineage_queries.py",
            "--manifest",
            "examples/minimal/snapshot-manifest.json",
            "--schema-dir",
            "schemas",
            "--database",
            str(tmp_path / "lineage.sqlite"),
            "--output",
            str(output),
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["status"] == "environment-bound-observation"
    assert report["node_count"] > 0
    assert {item["case"] for item in report["observations"]} == {"where", "why", "impact", "page"}
    assert all(item["elapsed_ns"] >= 0 for item in report["observations"])
    assert "national-scale" in report["nonclaims"][0]
