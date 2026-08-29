from __future__ import annotations

import json
from pathlib import Path

import pytest

import riopa_provenance.lineage as lineage_module
from riopa_provenance.lineage import (
    _SCHEMA,
    LineageError,
    LineageIndex,
    LineageQuery,
    QueryCache,
    _identifier,
    _label,
    _normalise_json,
    _role_node_type,
)
from riopa_provenance.validation import ManifestReference, ValidationResult


def seeded_index(tmp_path: Path) -> LineageIndex:
    index = LineageIndex(tmp_path / "lineage.sqlite")
    connection = index._connect()
    connection.executescript(_SCHEMA)
    connection.execute(
        "INSERT INTO manifests VALUES (?, ?, ?, ?, ?)",
        ("manifest-1", "snapshot.json", "a" * 64, "snapshot-1", "dataset-1"),
    )
    index._put_node(connection, "source-1", "source", label="Source")
    index._put_node(connection, "artifact-1", "artifact", label="Artifact")
    index._put_node(connection, "snapshot-1", "snapshot", label="Snapshot")
    index._put_edge(
        connection,
        "source-1",
        "artifact-1",
        "source_of_artifact",
        record_path="artifact.json",
        manifest_id="manifest-1",
    )
    index._put_edge(
        connection,
        "artifact-1",
        "snapshot-1",
        "included_in_snapshot",
        record_path="artifact.json",
        manifest_id="manifest-1",
    )
    connection.commit()
    connection.close()
    return index


def test_transport_neutral_lineage_query_round_trip_is_strict() -> None:
    query = LineageQuery(node_id="source-1", question="where", max_depth=4)
    assert LineageQuery.from_payload(query.to_payload()) == query
    with pytest.raises(LineageError, match="fields must match"):
        LineageQuery.from_payload({**query.to_payload(), "extra": True})
    with pytest.raises(LineageError, match="unsupported"):
        LineageQuery.from_payload({**query.to_payload(), "contract_version": "2.0.0"})

    for invalid in (
        {**query.to_payload(), "node_id": " "},
        {**query.to_payload(), "question": "what"},
        {**query.to_payload(), "max_depth": 0},
        {**query.to_payload(), "max_depth": 101},
        {**query.to_payload(), "node_id": 4},
        {**query.to_payload(), "max_depth": True},
    ):
        with pytest.raises(LineageError):
            LineageQuery.from_payload(invalid)


def test_import_manifest_rejects_non_object_root(monkeypatch, tmp_path: Path) -> None:
    index = LineageIndex(tmp_path / "lineage.sqlite")
    manifest = tmp_path / "manifest.json"
    manifest.write_text("[]")
    monkeypatch.setattr(
        lineage_module,
        "validate_manifest_closure",
        lambda *_args, **_kwargs: ValidationResult(path=manifest, schema=None, errors=()),
    )
    monkeypatch.setattr(lineage_module, "load_json", lambda *_args, **_kwargs: [])
    with pytest.raises(LineageError, match="manifest root"):
        index.import_manifest(manifest)


def test_lineage_walks_are_sorted_and_cycle_safe(tmp_path: Path) -> None:
    index = seeded_index(tmp_path)
    assert [item["node_id"] for item in index.downstream("source-1")] == [
        "artifact-1",
        "snapshot-1",
    ]
    assert [item["node_id"] for item in index.upstream("snapshot-1")] == [
        "artifact-1",
        "source-1",
    ]
    assert index.direct_edges("artifact-1")[0].relation == "source_of_artifact"
    impact = index.rebuild_impact(["source-1"])
    assert impact["roots"] == ["source-1"]
    assert [item["node_id"] for item in impact["impacted"]] == ["artifact-1", "snapshot-1"]
    assert impact["projection"]["lineage_granularities"] == ["dataset"]
    assert "not captured" in impact["projection"]["granularity_limitation"]
    combined = index.rebuild_impact(["source-1", "artifact-1", "snapshot-1"])
    assert [item["node_id"] for item in combined["impacted"]] == ["artifact-1", "snapshot-1"]
    with pytest.raises(LineageError, match="max_depth"):
        index.downstream("source-1", max_depth=0)


def test_page_nodes_is_bounded_and_reports_diagnostics(tmp_path: Path) -> None:
    index = seeded_index(tmp_path)
    page = index.page_nodes(limit=1, offset=1)
    assert page["pagination"] == {"limit": 1, "offset": 1, "total": 3, "next_offset": 2}
    assert len(page["nodes"]) == 1
    assert page["diagnostics"]["projection_sha256"]
    assert "no remote authorization" in page["access_control"]
    with pytest.raises(LineageError, match="limit"):
        index.page_nodes(limit=0)
    with pytest.raises(LineageError, match="offset"):
        index.page_nodes(offset=-1)


@pytest.mark.parametrize("value", [1.5, "1", True])
def test_page_nodes_rejects_non_integer_pagination_inputs(tmp_path: Path, value: object) -> None:
    index = seeded_index(tmp_path)
    with pytest.raises(LineageError, match="limit"):
        index.page_nodes(limit=value)  # type: ignore[arg-type]
    with pytest.raises(LineageError, match="offset"):
        index.page_nodes(offset=value)  # type: ignore[arg-type]


def test_query_cache_is_bounded_and_projection_fingerprint_aware(tmp_path: Path) -> None:
    index = seeded_index(tmp_path)
    first = index.query_cached("source-1", question="where")
    second = index.query_cached("source-1", question="where")
    assert first["cache"]["hit"] is False
    assert second["cache"]["hit"] is True
    assert second["answer"] == first["answer"]
    connection = index._connect()
    index._put_node(connection, "new-node", "artifact")
    connection.commit()
    connection.close()
    changed = index.query_cached("source-1", question="where")
    assert changed["cache"]["hit"] is False


def test_query_cache_rejects_invalid_size_and_evicts_oldest() -> None:
    with pytest.raises(LineageError, match="max_entries"):
        QueryCache(0)
    cache = QueryCache(1)
    cache.put(("a", "node", "where", 1), {"answer": [1]})
    cache.put(("b", "node", "where", 1), {"answer": [2]})
    assert cache.size == 1
    assert cache.get(("a", "node", "where", 1)) is None


def test_export_duckdb_preserves_projection_rows_and_digest_binding(tmp_path: Path) -> None:
    duckdb = pytest.importorskip("duckdb")
    index = seeded_index(tmp_path)
    target = tmp_path / "lineage.duckdb"
    receipt = index.export_duckdb(target)

    assert receipt["manifests"] == 1
    assert receipt["nodes"] == 3
    assert receipt["edges"] == 2
    assert len(receipt["sha256"]) == 64
    assert receipt["projection_fingerprint"] == index.projection_fingerprint()
    with duckdb.connect(str(target), read_only=True) as connection:
        assert connection.execute("SELECT count(*) FROM manifests").fetchone() == (1,)
        assert connection.execute("SELECT count(*) FROM nodes").fetchone() == (3,)
        assert connection.execute("SELECT count(*) FROM edges").fetchone() == (2,)
        assert connection.execute(
            "SELECT count(*) FROM edges WHERE source_id = 'source-1'"
        ).fetchone() == (1,)


def test_export_duckdb_rejects_same_projection_path(tmp_path: Path) -> None:
    index = seeded_index(tmp_path)
    with pytest.raises(LineageError, match="must differ"):
        index.export_duckdb(index.path)
    empty = LineageIndex(tmp_path / "empty.sqlite")
    connection = empty._connect()
    connection.executescript(_SCHEMA)
    connection.close()
    receipt = empty.export_duckdb(tmp_path / "empty.duckdb")
    assert receipt["manifests"] == receipt["nodes"] == receipt["edges"] == 0


def test_projection_fingerprint_is_stable_across_rebuilds_and_reimports(tmp_path: Path) -> None:
    first = seeded_index(tmp_path / "first")
    second = seeded_index(tmp_path / "second")
    assert first.projection_fingerprint() == second.projection_fingerprint()
    before = first.projection_fingerprint()
    connection = first._connect()
    connection.execute("CREATE TABLE migration_sentinel (version INTEGER)")
    connection.execute("INSERT INTO migration_sentinel VALUES (1)")
    connection.commit()
    connection.close()
    assert first.projection_fingerprint() == before


def test_export_prov_jsonld_is_deterministic_and_not_authoritative(tmp_path: Path) -> None:
    index = seeded_index(tmp_path / "source")
    first = index.export_prov_jsonld(tmp_path / "one.jsonld")
    second = index.export_prov_jsonld(tmp_path / "two.jsonld")
    assert first["nodes"] == 3
    assert first["edges"] == 2
    assert first["projection_fingerprint"] == second["projection_fingerprint"]
    assert first["sha256"] == second["sha256"]
    payload = json.loads((tmp_path / "one.jsonld").read_text())
    assert payload["riopa:promotionAllowed"] is False
    with pytest.raises(LineageError, match="must differ"):
        index.export_prov_jsonld(index.path)
    assert len(payload["@graph"]) == 5
    assert any(item["@type"] == "riopa:LineageRelation" for item in payload["@graph"])


@pytest.mark.parametrize("depth", [0, 101])
def test_lineage_depth_and_identity_fail_closed(tmp_path: Path, depth: int) -> None:
    index = seeded_index(tmp_path)
    with pytest.raises(LineageError, match="max_depth"):
        index.downstream("source-1", max_depth=depth)
    with pytest.raises(LineageError, match="unknown lineage node"):
        index.downstream("missing")


def test_conflicting_concrete_node_types_are_rejected(tmp_path: Path) -> None:
    index = seeded_index(tmp_path)
    connection = index._connect()
    with pytest.raises(LineageError, match="conflicting types"):
        index._put_node(connection, "source-1", "artifact")
    connection.close()


def test_normative_queries_report_evidence_granularity_and_freshness(tmp_path: Path) -> None:
    index = seeded_index(tmp_path)
    why = index.query("snapshot-1", question="why")
    assert [item["node_id"] for item in why["answer"]] == ["artifact-1", "source-1"]
    assert why["projection"]["authoritative_evidence"] == [
        {
            "manifest_id": "manifest-1",
            "manifest_sha256": "a" * 64,
            "snapshot_id": "snapshot-1",
            "dataset_id": "dataset-1",
        }
    ]
    assert len(why["projection"]["projection_sha256"]) == 64
    assert why["projection"]["freshness"] == "current-for-listed-authoritative-evidence"
    assert index.query("source-1", question="where")["answer"][0]["node_id"] == "artifact-1"
    assert index.query("artifact-1", question="how")["answer"][0]["relation"] == (
        "source_of_artifact"
    )
    with pytest.raises(LineageError, match="where, why, how"):
        index.query("source-1", question="when")
    with pytest.raises(LineageError, match="unknown lineage node"):
        index.query("missing", question="how")


def test_projection_reconciliation_removes_only_unreferenced_nodes(tmp_path: Path) -> None:
    index = seeded_index(tmp_path)
    connection = index._connect()
    index._put_node(connection, "stale-2", "artifact")
    index._put_node(connection, "stale-1", "artifact")
    connection.commit()
    connection.close()

    assert index.reconcile_projection() == {
        "removed_stale_node_ids": ["stale-1", "stale-2"],
        "removed_count": 2,
        "policy": "remove nodes unreferenced by every authoritative manifest edge",
    }
    assert [node.node_id for node in index.nodes()] == [
        "artifact-1",
        "snapshot-1",
        "source-1",
    ]


def test_record_helpers_use_first_valid_identity_and_safe_fallbacks() -> None:
    assert _identifier({"event_id": "", "run_id": "run-1"}) == "run-1"
    assert _identifier({"event_id": 1}) is None
    assert _label({"title": "", "name": "Readable"}) == "Readable"
    assert _label({"title": 1}) is None
    assert _role_node_type("domain_record", {"record_type": "facility"}) == "facility"
    assert _role_node_type("domain_record", {}) == "domain_record"
    assert _role_node_type("artifact", {}) == "artifact"
    assert _normalise_json({"é": [2, 1]}) == '{"é":[2,1]}'


def test_minimal_manifest_import_exercises_supported_lineage_relations(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    index = LineageIndex(tmp_path / "imported.sqlite")

    manifest_id = index.import_manifest(root / "examples/minimal/snapshot-manifest.json")

    assert manifest_id == "urn:riopa:snapshot:nz-spatial-example:2026.07.18:example"
    relations = {
        edge.relation for node in index.nodes() for edge in index.direct_edges(node.node_id)
    }
    assert {
        "has_snapshot",
        "included_in_snapshot",
        "captured_as",
        "source_of_artifact",
        "used_by_run",
        "generated_by_run",
        "used_by_event",
        "generated_by_event",
        "generated_materialization",
        "describes_artifact",
    } <= relations
    assert [node.node_id for node in index.nodes(node_type="source")] == [
        "urn:riopa:source:linz-data-service"
    ]

    # Re-importing the same authoritative snapshot replaces its projection
    # transactionally rather than duplicating edges.
    edge_count = sum(len(index.direct_edges(node.node_id)) for node in index.nodes())
    assert index.import_manifest(root / "examples/minimal/snapshot-manifest.json") == manifest_id
    assert sum(len(index.direct_edges(node.node_id)) for node in index.nodes()) == edge_count


def test_invalid_manifest_and_unknown_direct_edge_query_fail_closed(tmp_path: Path) -> None:
    index = LineageIndex(tmp_path / "lineage.sqlite")
    with pytest.raises(LineageError, match="manifest validation failed"):
        index.import_manifest(tmp_path / "missing.json")

    index = seeded_index(tmp_path)
    with pytest.raises(LineageError, match="unknown lineage node"):
        index.direct_edges("missing")


def test_projection_reports_feature_granularity_and_enriches_external_stub(
    tmp_path: Path,
) -> None:
    index = seeded_index(tmp_path)
    connection = index._connect()
    index._put_node(connection, "feature-1", "external")
    index._put_node(
        connection,
        "feature-1",
        "feature",
        label="Feature",
        record_path="feature.json",
        metadata={"feature_id": 1},
    )
    # An external mention cannot erase a concrete node's metadata.
    index._put_node(connection, "feature-1", "external")
    index._put_edge(
        connection,
        "feature-1",
        "snapshot-1",
        "included_in_snapshot",
        record_path="feature.json",
        manifest_id="manifest-1",
    )
    connection.commit()
    connection.close()

    assert index.nodes(node_type="feature")[0].label == "Feature"
    metadata = index.projection_metadata()
    assert metadata["lineage_granularities"] == ["dataset", "feature"]
    assert metadata["granularity_limitation"] is None


def test_rebuild_impact_keeps_shortest_path_for_shared_descendant(tmp_path: Path) -> None:
    index = seeded_index(tmp_path)
    connection = index._connect()
    index._put_edge(
        connection,
        "source-2",
        "snapshot-1",
        "direct_rebuild",
        record_path=None,
        manifest_id="manifest-1",
    )
    connection.commit()
    connection.close()

    result = index.rebuild_impact(["source-2", "source-1", "source-1"])
    assert result["roots"] == ["source-1", "source-2"]
    snapshot = next(item for item in result["impacted"] if item["node_id"] == "snapshot-1")
    assert snapshot["depth"] == 1


def test_manifest_import_maps_causal_and_relationship_edges_and_ignores_noise(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest_path = tmp_path / "manifest.json"
    event_path = tmp_path / "event.json"
    anonymous_path = tmp_path / "anonymous.json"
    manifest_path.write_text("{}", encoding="utf-8")
    event_path.write_text("{}", encoding="utf-8")
    anonymous_path.write_text("{}", encoding="utf-8")
    manifest = {
        "snapshot_id": "snapshot",
        "dataset_id": "dataset",
        "sources": [
            "not-an-object",
            {"source_id": 3},
            {"source_id": "source", "capture_ids": [4, "capture"]},
        ],
        "relationships": [
            "not-an-object",
            {"identifier": 4, "relation": "ignored"},
            {"identifier": "related", "relation": "is_version_of"},
        ],
    }
    event = {
        "event_id": "event",
        "inputs": [3, "input"],
        "outputs": [4, "output"],
        "causal_parent_event_ids": [5, "parent"],
    }
    records = {
        manifest_path: manifest,
        event_path: event,
        anonymous_path: {"description": "anonymous extension"},
    }
    references = [
        ManifestReference("event.json", None, "provenance_event"),
        ManifestReference("anonymous.json", None, "domain_record"),
    ]
    monkeypatch.setattr(
        lineage_module,
        "validate_manifest_closure",
        lambda *_args, **_kwargs: ValidationResult(manifest_path, None, ()),
    )
    monkeypatch.setattr(lineage_module, "load_json", lambda path: records[Path(path)])
    monkeypatch.setattr(lineage_module, "manifest_reference_specs", lambda _manifest: references)

    index = LineageIndex(tmp_path / "lineage.sqlite")
    assert index.import_manifest(manifest_path) == "snapshot"
    relations = {
        (edge.source_id, edge.target_id, edge.relation)
        for node in index.nodes()
        for edge in index.direct_edges(node.node_id)
    }
    assert ("parent", "event", "causal_predecessor") in relations
    assert ("event", "output", "generated_by_event") in relations
    assert ("input", "event", "used_by_event") in relations
    assert ("source", "capture", "captured_as") in relations
    assert ("snapshot", "related", "is_version_of") in relations
    assert any(node.node_id.startswith("urn:riopa:record:") for node in index.nodes())
