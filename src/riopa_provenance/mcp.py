"""Bounded read-only MCP-style transport for local provenance queries.

This adapter deliberately has no network, credential or authorization layer.
It exposes the same deterministic lineage operations as the Python and CLI
interfaces over newline-delimited JSON-RPC for local tooling and fixtures.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from typing import Any, TextIO

from .lineage import LineageError, LineageIndex

_MAX_REQUEST_BYTES = 1_048_576


class McpProtocolError(ValueError):
    """Raised for malformed or unsupported bounded transport requests."""


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


class McpLineageServer:
    """Dispatch bounded MCP-style tools against a read-only lineage index."""

    def __init__(self, index: LineageIndex) -> None:
        self.index = index

    @staticmethod
    def tools() -> list[dict[str, Any]]:
        return [
            {
                "name": "lineage_query",
                "description": "Answer a bounded where, why or how lineage question.",
                "inputSchema": {
                    "type": "object",
                    "required": ["node_id", "question"],
                    "properties": {
                        "node_id": {"type": "string", "minLength": 1},
                        "question": {"type": "string", "enum": ["where", "why", "how"]},
                        "max_depth": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                    "additionalProperties": False,
                },
            },
            {
                "name": "lineage_walk",
                "description": "Walk bounded upstream or downstream lineage.",
                "inputSchema": {
                    "type": "object",
                    "required": ["node_id", "direction"],
                    "properties": {
                        "node_id": {"type": "string", "minLength": 1},
                        "direction": {"type": "string", "enum": ["upstream", "downstream"]},
                        "max_depth": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                    "additionalProperties": False,
                },
            },
            {
                "name": "lineage_impact",
                "description": "Compute bounded downstream rebuild impact for lineage roots.",
                "inputSchema": {
                    "type": "object",
                    "required": ["node_ids"],
                    "properties": {
                        "node_ids": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                            "minItems": 1,
                        },
                        "max_depth": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                    "additionalProperties": False,
                },
            },
        ]

    @staticmethod
    def _arguments(arguments: Any) -> Mapping[str, Any]:
        if not isinstance(arguments, Mapping):
            raise McpProtocolError("arguments must be an object")
        return arguments

    def _call(self, name: Any, arguments: Any) -> dict[str, Any]:
        args = self._arguments(arguments)
        max_depth = args.get("max_depth", 20)
        if not isinstance(max_depth, int) or isinstance(max_depth, bool):
            raise McpProtocolError("max_depth must be an integer")
        if name == "lineage_query":
            node_id, question = args.get("node_id"), args.get("question")
            if not isinstance(node_id, str) or not node_id:
                raise McpProtocolError("node_id must be a non-empty string")
            if question not in {"where", "why", "how"}:
                raise McpProtocolError("question must be one of: where, why, how")
            result = self.index.query(node_id, question=question, max_depth=max_depth)
        elif name == "lineage_walk":
            node_id, direction = args.get("node_id"), args.get("direction")
            if not isinstance(node_id, str) or not node_id:
                raise McpProtocolError("node_id must be a non-empty string")
            if direction == "upstream":
                nodes = self.index.upstream(node_id, max_depth=max_depth)
            elif direction == "downstream":
                nodes = self.index.downstream(node_id, max_depth=max_depth)
            else:
                raise McpProtocolError("direction must be one of: upstream, downstream")
            result = {"node_id": node_id, "direction": direction, "nodes": nodes}
        elif name == "lineage_impact":
            node_ids = args.get("node_ids")
            if (
                not isinstance(node_ids, list)
                or not node_ids
                or not all(isinstance(item, str) and item for item in node_ids)
            ):
                raise McpProtocolError("node_ids must be a non-empty array of strings")
            result = self.index.rebuild_impact(node_ids, max_depth=max_depth)
        else:
            raise McpProtocolError(f"unknown tool: {name}")
        return {"content": [{"type": "text", "text": json.dumps(result, sort_keys=True)}]}

    def handle(self, request: Mapping[str, Any]) -> dict[str, Any] | None:
        """Handle one JSON-RPC request; notifications return ``None``."""

        request_id = request.get("id")
        method = request.get("method")
        if request.get("jsonrpc") != "2.0" or not isinstance(method, str):
            return _error(request_id, -32600, "invalid JSON-RPC request")
        try:
            result: Any
            if method == "initialize":
                result = {
                    "protocolVersion": "riopa-bounded-1",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "riopa-lineage", "version": "0.4.0"},
                }
            elif method == "notifications/initialized":
                return None
            elif method == "tools/list":
                result = {"tools": self.tools()}
            elif method == "tools/call":
                params = request.get("params")
                if not isinstance(params, Mapping):
                    raise McpProtocolError("params must be an object")
                result = self._call(params.get("name"), params.get("arguments", {}))
            else:
                return _error(request_id, -32601, f"method not found: {method}")
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except (McpProtocolError, LineageError) as exc:
            return _error(request_id, -32602, str(exc))


def serve_stdio(
    index: LineageIndex,
    input_stream: TextIO = sys.stdin,
    output_stream: TextIO = sys.stdout,
) -> None:
    """Serve newline-delimited JSON-RPC requests without network access."""

    server = McpLineageServer(index)
    for raw in input_stream:
        response: dict[str, Any] | None
        if len(raw.encode("utf-8")) > _MAX_REQUEST_BYTES:
            response = _error(None, -32600, "request exceeds 1 MiB")
        else:
            try:
                request = json.loads(raw)
                response = (
                    server.handle(request)
                    if isinstance(request, Mapping)
                    else _error(None, -32600, "request must be an object")
                )
            except (json.JSONDecodeError, UnicodeError) as exc:
                response = _error(None, -32700, f"parse error: {exc}")
        if response is not None:
            output_stream.write(json.dumps(response, sort_keys=True) + "\n")
            output_stream.flush()


__all__ = ["McpLineageServer", "McpProtocolError", "serve_stdio"]
