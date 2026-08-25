"""Run the pinned bounded SHACL validation for the canonical golden fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
from typing import Any

from pyshacl import validate
from rdflib import RDF, Graph, Literal, Namespace, URIRef

RIOPA = Namespace("https://w3id.org/riopa/ontology/")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_fixture_graph(fixture: dict[str, Any]) -> Graph:
    """Convert one canonical JSON mapping into the declared RDF validation graph."""

    graph = Graph()
    subject = URIRef(str(fixture["mapping_id"]))
    graph.add((subject, RDF.type, RIOPA.CrosswalkClaim))
    for field, predicate in (
        ("mapping_id", RIOPA.mappingId),
        ("canonical_id", RIOPA.canonicalId),
        ("method", RIOPA.method),
        ("confidence", RIOPA.confidence),
        ("reviewer", RIOPA.reviewer),
    ):
        graph.add((subject, predicate, Literal(fixture[field])))
    for evidence in fixture["evidence"]:
        graph.add((subject, RIOPA.evidence, Literal(evidence)))
    return graph


def validate_fixture(fixture_path: Path, shape_path: Path) -> dict[str, Any]:
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    data_graph = build_fixture_graph(fixture)
    shapes_graph = Graph().parse(shape_path, format="turtle")
    conforms, _, results_text = validate(
        data_graph,
        shacl_graph=shapes_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
    )
    return {
        "evidence_id": "CANONICAL-SHACL-EXECUTION-20260825",
        "runtime": {"pyshacl": version("pyshacl"), "rdflib": version("rdflib")},
        "fixture": str(fixture_path),
        "fixture_sha256": _sha256(fixture_path),
        "shape": str(shape_path),
        "shape_sha256": _sha256(shape_path),
        "conforms": bool(conforms),
        "results_text": results_text.strip(),
        "promotion_allowed": False,
        "nonclaims": [
            "This is a bounded RDF/SHACL execution for the supplied fixture.",
            "It is not external semantic qualification, publication or authority approval.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--shape", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate_fixture(args.fixture, args.shape)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["conforms"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
