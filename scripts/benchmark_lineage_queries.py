#!/usr/bin/env python3
"""Run a deterministic local lineage-query timing harness.

The output is an environment-bound observation for regression comparison. It is
not a national-scale or production-capacity claim.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path
from typing import Any

from riopa_provenance.lineage import LineageIndex


def run(manifest: Path, schema_dir: Path | None, database: Path) -> dict[str, Any]:
    index = LineageIndex(database)
    index.import_manifest(manifest, schema_dir=schema_dir)
    nodes = index.nodes()
    if not nodes:
        raise ValueError("lineage projection contains no nodes")
    node_id = nodes[0].node_id
    cases = (
        ("where", lambda: index.query(node_id, question="where")),
        ("why", lambda: index.query(node_id, question="why")),
        ("impact", lambda: index.rebuild_impact([node_id])),
        ("page", lambda: index.page_nodes(limit=100, offset=0)),
    )
    observations: list[dict[str, Any]] = []
    for name, operation in cases:
        started = time.perf_counter_ns()
        result = operation()
        elapsed = time.perf_counter_ns() - started
        observations.append(
            {"case": name, "elapsed_ns": elapsed, "result_type": type(result).__name__}
        )
    return {
        "benchmark_id": "urn:riopa:benchmark:provenance-query:local:1.0.0",
        "status": "environment-bound-observation",
        "node_id": node_id,
        "node_count": len(nodes),
        "projection": index.projection_metadata(),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "observations": observations,
        "nonclaims": [
            "This is not a national-scale or production-capacity measurement.",
            (
                "Timings are not comparable across environments without matching hardware "
                "and software."
            ),
            "The result does not establish release, soak or authority gates.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--schema-dir", type=Path)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run(args.manifest, args.schema_dir, args.database)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Lineage benchmark written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
