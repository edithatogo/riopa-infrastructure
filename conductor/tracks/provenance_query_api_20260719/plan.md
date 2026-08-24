# Plan: provenance_query_api_20260719

## 1. Query contract

- [x] 1.1 Define why, where, how, downstream and rebuild-impact query semantics. (`src/riopa_provenance/lineage.py`, `docs/change-and-impact-queries.md`)
- [x] 1.2 Define granularity, freshness, uncertainty and access-control responses. (`src/riopa_provenance/lineage.py`, `docs/change-and-impact-queries.md`, `tests/test_lineage.py`)
- [x] 1.3 Build a language-neutral query conformance corpus. Evidence: `docs/provenance-query-conformance-corpus-20260822.json`, `tests/test_provenance_query_corpus.py`; Python reference answers are deterministic over a synthetic SQLite projection.

## 2. Projection implementation

- [~] 2.1 Implement relational lineage tables and indexes in DuckDB-compatible form. `LineageIndex.export_duckdb` preserves manifests, nodes, edges, indexes and source/projection digests; graph equivalence and production-scale qualification remain open (`src/riopa_provenance/lineage.py`, `tests/test_lineage.py`).
- [x] 2.2 Implement a deterministic optional PROV-JSON-LD projection with explicit non-authority boundaries (`src/riopa_provenance/lineage.py`, `tests/test_lineage.py`, `docs/provenance-query-prov-jsonld-contract-20260825.json`). RDF/SHACL, semantic-loss, external-client, access-control, scale and authority gates remain open.
- [x] 2.3 Add deterministic rebuild and schema-migration tests using a logical projection fingerprint (`src/riopa_provenance/lineage.py`, `tests/test_lineage.py`, `docs/provenance-query-rebuild-contract-20260825.json`). Interface, access-control, production-scale, real-release and external-user gates remain open.

## 3. Interfaces and performance

- [~] 3.1 Implement CLI, Python and MCP interfaces. The Python reference and
  CLI lineage build/walk/impact/export commands are repository-owned; an MCP
  transport and cross-interface equivalence remain open.
- [~] 3.2 Add caching, pagination, access filtering and diagnostics. Deterministic local pagination and projection diagnostics are implemented; caching, remote authorization and access filtering remain open (`src/riopa_provenance/lineage.py`, `src/riopa_provenance/cli.py`, `docs/provenance-query-pagination-diagnostics-contract-20260825.json`).
- [~] 3.3 Benchmark representative release and impact queries. A deterministic local timing harness covers where/why/impact/page cases; representative release-scale, second-environment and production measurements remain open (`scripts/benchmark_lineage_queries.py`, `tests/test_provenance_query_benchmark.py`).

## 4. Stable query release

- [ ] 4.1 Validate equivalent answers across interfaces and projections.
- [ ] 4.2 Conduct user testing on real provenance questions.
- [ ] 4.3 Freeze the v1 query contract and publish migration guidance.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
