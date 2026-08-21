import json
from pathlib import Path

from riopa_provenance.lineage import _SCHEMA, LineageIndex

ROOT = Path(__file__).resolve().parents[1]


def _seed(tmp_path: Path) -> LineageIndex:
    index = LineageIndex(tmp_path / "lineage.sqlite")
    connection = index._connect()
    connection.executescript(_SCHEMA)
    connection.execute(
        "INSERT INTO manifests VALUES (?, ?, ?, ?, ?)",
        ("manifest-1", "snapshot.json", "a" * 64, "snapshot-1", "dataset-1"),
    )
    index._put_node(connection, "source-1", "source")
    index._put_node(connection, "artifact-1", "artifact")
    index._put_node(connection, "snapshot-1", "snapshot")
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


def test_language_neutral_query_corpus_matches_python_reference(tmp_path: Path) -> None:
    corpus = json.loads(
        (ROOT / "docs/provenance-query-conformance-corpus-20260822.json").read_text()
    )
    index = _seed(tmp_path)
    for case in corpus["cases"]:
        if case["question"] == "impact":
            result = index.rebuild_impact([case["node_id"]])
            actual = [item["node_id"] for item in result["impacted"]]
            assert actual == case["expected_answer_ids"]
        else:
            result = index.query(case["node_id"], question=case["question"])
            if "expected_answer_ids" in case:
                assert [item["node_id"] for item in result["answer"]] == case["expected_answer_ids"]
            else:
                assert result["answer"] == case["expected_relations"]
        assert result["projection"]["freshness"] == "current-for-listed-authoritative-evidence"
