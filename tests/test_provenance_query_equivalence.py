from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from riopa_provenance.lineage import LineageIndex


def test_python_cli_and_disposable_projections_have_equivalent_bounded_answers(
    tmp_path: Path,
) -> None:
    duckdb = pytest.importorskip("duckdb")
    root = Path(__file__).resolve().parents[1]
    index = LineageIndex(tmp_path / "lineage.sqlite")
    index.import_manifest(root / "examples/minimal/snapshot-manifest.json")
    source_id = index.nodes(node_type="source")[0].node_id
    python_nodes = [item["node_id"] for item in index.downstream(source_id)]

    cli = subprocess.run(
        [
            sys.executable,
            "-m",
            "riopa_provenance.cli",
            "lineage",
            "walk",
            "--database",
            str(index.path),
            "--node-id",
            source_id,
            "--direction",
            "downstream",
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    cli_nodes = [item["node_id"] for item in json.loads(cli.stdout)["nodes"]]
    assert cli_nodes == python_nodes

    duckdb_path = tmp_path / "lineage.duckdb"
    receipt = index.export_duckdb(duckdb_path)
    assert receipt["projection_fingerprint"] == index.projection_fingerprint()
    with duckdb.connect(str(duckdb_path), read_only=True) as connection:
        duck_edges = connection.execute(
            "SELECT source_id, target_id, relation FROM edges "
            "ORDER BY manifest_id, source_id, target_id, relation"
        ).fetchall()
    sqlite_edges = sorted(
        (edge.source_id, edge.target_id, edge.relation)
        for node in index.nodes()
        for edge in index.direct_edges(node.node_id)
    )
    assert sorted(set(duck_edges)) == sorted(set(sqlite_edges))

    prov_path = tmp_path / "lineage.jsonld"
    index.export_prov_jsonld(prov_path)
    payload = json.loads(prov_path.read_text(encoding="utf-8"))
    prov_edges = sorted(
        (
            item["riopa:source"]["@id"],
            item["riopa:target"]["@id"],
            item["riopa:relation"],
        )
        for item in payload["@graph"]
        if item["@type"] == "riopa:LineageRelation"
    )
    assert prov_edges == sorted(set(sqlite_edges))
    assert payload["riopa:projectionFingerprint"] == index.projection_fingerprint()


def test_equivalence_contract_is_bounded_and_non_assertive() -> None:
    root = Path(__file__).resolve().parents[1]
    contract = json.loads(
        (root / "docs/provenance-query-equivalence-contract-20260825.json").read_text()
    )
    assert contract["promotion_allowed"] is False
    assert "MCP transport equivalence" in contract["open_gates"]
