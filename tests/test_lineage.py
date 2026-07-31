from __future__ import annotations

from pathlib import Path

import pytest

from riopa_provenance.lineage import _SCHEMA, LineageError, LineageIndex


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
    assert index.rebuild_impact(["source-1"]) == {
        "roots": ["source-1"],
        "impacted": [
            {
                "node_id": "artifact-1",
                "depth": 1,
                "node_type": "artifact",
                "label": "Artifact",
                "record_path": None,
            },
            {
                "node_id": "snapshot-1",
                "depth": 2,
                "node_type": "snapshot",
                "label": "Snapshot",
                "record_path": None,
            },
        ],
    }


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
