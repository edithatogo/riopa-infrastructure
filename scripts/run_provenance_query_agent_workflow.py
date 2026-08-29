#!/usr/bin/env python3
"""Run bounded agent-user questions against a local provenance projection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from riopa_provenance.lineage import LineageIndex


def run(manifest: Path, schema_dir: Path | None, database: Path) -> dict[str, Any]:
    """Answer representative provenance questions without remote access control."""

    index = LineageIndex(database)
    index.import_manifest(manifest, schema_dir=schema_dir)
    nodes = index.nodes()
    if not nodes:
        raise ValueError("lineage projection contains no nodes")
    node_id = nodes[0].node_id
    questions = ("where", "why", "how")
    answers: list[dict[str, Any]] = []
    for question in questions:
        result = index.query_cached(node_id, question=question)
        answers.append(
            {
                "question": question,
                "answer_keys": sorted(result),
                "answer_count": len(result.get("answer", [])),
                "cache_hit": result.get("cache", {}).get("hit"),
                "has_projection_diagnostic": bool(result.get("projection")),
            }
        )
    impact = index.rebuild_impact([node_id])
    page = index.page_nodes(limit=10, offset=0)
    return {
        "evidence_id": "PROVENANCE-QUERY-AGENT-WORKFLOW-20260825",
        "record_type": "provenance-query-agent-workflow",
        "status": "bounded-local-agent-workflow",
        "node_id": node_id,
        "node_count": len(nodes),
        "questions": answers,
        "impact_count": len(impact.get("impacted", [])),
        "page_total": page["pagination"]["total"],
        "projection": index.projection_metadata(),
        "claim_classification": "repository-reference-only",
        "promotion_allowed": False,
        "open_gates": [
            "owner-authorized agent-operated user/operator workflows",
            "remote access-control qualification",
            "MCP transport qualification",
            "production-scale and release-authority evidence",
        ],
        "nonclaims": [
            (
                "Agent-user questions exercise the local interface and do not substitute "
                "for external participants."
            ),
            "The projection is not an authoritative source of truth or a production service.",
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
    print(f"Provenance query agent workflow written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
