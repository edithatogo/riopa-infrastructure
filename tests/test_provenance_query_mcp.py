from __future__ import annotations

import io
import json
from pathlib import Path

from riopa_provenance.lineage import _SCHEMA, LineageIndex
from riopa_provenance.mcp import McpLineageServer, serve_stdio


def _seed(tmp_path: Path) -> LineageIndex:
    index = LineageIndex(tmp_path / "lineage.sqlite")
    connection = index._connect()
    connection.executescript(_SCHEMA)
    connection.execute(
        "INSERT INTO manifests VALUES (?, ?, ?, ?, ?)",
        ("manifest-1", "snapshot.json", "a" * 64, "snapshot-1", "dataset-1"),
    )
    index._put_node(connection, "source-1", "source", label="Source")
    index._put_node(connection, "artifact-1", "artifact", label="Artifact")
    index._put_edge(
        connection,
        "source-1",
        "artifact-1",
        "source_of_artifact",
        record_path="artifact.json",
        manifest_id="manifest-1",
    )
    connection.commit()
    connection.close()
    return index


def test_tools_and_query_match_python_reference(tmp_path: Path) -> None:
    index = _seed(tmp_path)
    server = McpLineageServer(index)
    assert {tool["name"] for tool in server.tools()} == {
        "lineage_query",
        "lineage_walk",
        "lineage_impact",
    }
    response = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "lineage_query",
                "arguments": {"node_id": "source-1", "question": "where"},
            },
        }
    )
    assert response is not None
    payload = json.loads(response["result"]["content"][0]["text"])
    assert payload == index.query("source-1", question="where")


def test_stdio_handles_notifications_and_errors(tmp_path: Path) -> None:
    index = _seed(tmp_path)
    requests = (
        "\n".join(
            [
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}),
                json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {"name": "bad", "arguments": {}},
                    }
                ),
                "not-json",
            ]
        )
        + "\n"
    )
    output = io.StringIO()
    serve_stdio(index, io.StringIO(requests), output)
    responses = [json.loads(line) for line in output.getvalue().splitlines()]
    assert responses[0]["result"]["serverInfo"]["name"] == "riopa-lineage"
    assert responses[1]["error"]["code"] == -32602
    assert responses[2]["error"]["code"] == -32700


def test_server_dispatches_walk_impact_listing_and_validation(tmp_path: Path) -> None:
    index = _seed(tmp_path)
    server = McpLineageServer(index)

    listed = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert listed is not None
    assert len(listed["result"]["tools"]) == 3

    downstream = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "lineage_walk",
                "arguments": {"node_id": "source-1", "direction": "downstream"},
            },
        }
    )
    assert downstream is not None
    assert json.loads(downstream["result"]["content"][0]["text"])["nodes"]

    upstream = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "lineage_walk",
                "arguments": {"node_id": "artifact-1", "direction": "upstream"},
            },
        }
    )
    assert upstream is not None
    assert json.loads(upstream["result"]["content"][0]["text"])["nodes"]

    impact = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "lineage_impact", "arguments": {"node_ids": ["source-1"]}},
        }
    )
    assert impact is not None
    assert "impacted" in json.loads(impact["result"]["content"][0]["text"])

    assert (
        server.handle({"jsonrpc": "2.0", "id": 5, "method": "unknown"})["error"]["code"] == -32601
    )
    assert (
        server.handle({"jsonrpc": "1.0", "id": 6, "method": "tools/list"})["error"]["code"]
        == -32600
    )
    assert (
        server.handle({"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {}})["error"][
            "code"
        ]
        == -32602
    )


def test_server_rejects_invalid_arguments_and_bounds(tmp_path: Path) -> None:
    server = McpLineageServer(_seed(tmp_path))
    requests = [
        {"name": "lineage_query", "arguments": "bad"},
        {"name": "lineage_query", "arguments": {"node_id": "", "question": "where"}},
        {"name": "lineage_query", "arguments": {"node_id": "source-1", "question": "bad"}},
        {"name": "lineage_walk", "arguments": {"node_id": "", "direction": "upstream"}},
        {"name": "lineage_walk", "arguments": {"node_id": "source-1", "direction": "sideways"}},
        {"name": "lineage_impact", "arguments": {"node_ids": []}},
        {"name": "lineage_query", "arguments": {"node_id": "missing", "question": "where"}},
        {
            "name": "lineage_query",
            "arguments": {"node_id": "source-1", "question": "where", "max_depth": "bad"},
        },
    ]
    for number, arguments in enumerate(requests, start=10):
        response = server.handle(
            {
                "jsonrpc": "2.0",
                "id": number,
                "method": "tools/call",
                "params": arguments,
            }
        )
        assert response is not None
        assert response["error"]["code"] == -32602

    params_error = server.handle(
        {"jsonrpc": "2.0", "id": 20, "method": "tools/call", "params": "bad"}
    )
    assert params_error is not None
    assert params_error["error"]["code"] == -32602

    output = io.StringIO()
    serve_stdio(_seed(tmp_path / "large"), io.StringIO("{}\n" + "x" * 1_048_577 + "\n"), output)
    responses = [json.loads(line) for line in output.getvalue().splitlines()]
    assert responses[0]["error"]["code"] == -32600
    assert responses[1]["error"]["code"] == -32600
