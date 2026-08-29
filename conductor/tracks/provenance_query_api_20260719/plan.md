# Plan: provenance_query_api_20260719

## 1. Query contract

- [x] 1.1 Define why, where, how, downstream and rebuild-impact query semantics. (`src/riopa_provenance/lineage.py`, `docs/change-and-impact-queries.md`)
- [x] 1.2 Define granularity, freshness, uncertainty and access-control responses. (`src/riopa_provenance/lineage.py`, `docs/change-and-impact-queries.md`, `tests/test_lineage.py`)
- [x] 1.3 Build a language-neutral query conformance corpus. Evidence: `docs/provenance-query-conformance-corpus-20260822.json`, `tests/test_provenance_query_corpus.py`; Python reference answers are deterministic over a synthetic SQLite projection.

## 2. Projection implementation

- [x] 2.1 Implement relational lineage tables and indexes in DuckDB-compatible form. `LineageIndex.export_duckdb` preserves manifests, nodes, edges, indexes and source/projection digests, including the logical projection fingerprint; graph equivalence and production-scale qualification remain open (`src/riopa_provenance/lineage.py`, `tests/test_lineage.py`; commit `811c5e9`).
- [x] 2.2 Implement a deterministic optional PROV-JSON-LD projection with explicit non-authority boundaries (`src/riopa_provenance/lineage.py`, `tests/test_lineage.py`, `docs/provenance-query-prov-jsonld-contract-20260825.json`). RDF/SHACL, semantic-loss, external-client, access-control, scale and authority gates remain open.
- [x] 2.3 Add deterministic rebuild and schema-migration tests using a logical projection fingerprint (`src/riopa_provenance/lineage.py`, `tests/test_lineage.py`, `docs/provenance-query-rebuild-contract-20260825.json`). Interface, access-control, production-scale, real-release and agent-user-journey gates remain open.

## 3. Interfaces and performance

- [~] 3.1 Implement CLI, Python and MCP interfaces. The Python reference, bounded
  CLI commands and local read-only MCP-style stdio transport are repository-owned;
  bounded cross-interface equivalence is now tested, while remote transport/authorization
  and external-client qualification remain open (`src/riopa_provenance/cli.py`,
  `src/riopa_provenance/mcp.py`,
  `tests/test_provenance_query_mcp.py`, `docs/provenance-query-cli-contract-20260825.json`,
  `docs/provenance-query-mcp-transport-contract-20260826.json`).
- [~] 3.2 Add caching, pagination, access filtering and diagnostics. Deterministic local pagination, projection diagnostics and fingerprint-aware bounded caching are implemented; remote authorization and access filtering remain open (`src/riopa_provenance/lineage.py`, `src/riopa_provenance/cli.py`, `docs/provenance-query-pagination-diagnostics-contract-20260825.json`, `docs/provenance-query-cache-contract-20260825.json`).
- [~] 3.3 Benchmark representative release and impact queries. A deterministic local timing harness covers where/why/impact/page cases; representative release-scale, second-environment and production measurements remain open (`scripts/benchmark_lineage_queries.py`, `tests/test_provenance_query_benchmark.py`).

## 4. Stable query release

- [x] 4.1 Validate equivalent answers across the bounded Python/CLI/MCP interfaces and SQLite/DuckDB/PROV-JSON-LD projections. Evidence: `docs/provenance-query-equivalence-contract-20260825.json`, `tests/test_provenance_query_equivalence.py`; remote access filtering, real-release and agent-user-journey gates remain open.
- [x] 4.2 Run a bounded owner-authorized agent-user workflow over representative where/why/how provenance questions. The deterministic workflow and content-bound report are repository-owned evidence; agent-operated user/operator journeys, remote access control, MCP and release evidence remain open (`scripts/run_provenance_query_agent_workflow.py`, `docs/provenance-query-agent-workflow-20260825.json`, `tests/test_provenance_query_agent_workflow.py`).
- [x] 4.3 Publish bounded migration guidance for the 1.0.0 query contract. Compatibility rules and explicit breaking-change boundaries are documented as repository-owned guidance; v1 freeze, MCP/remote qualification, exact-candidate agent-user journey evidence and release approval remain open (`docs/provenance-query-migration-guidance-20260825.md`, `tests/test_provenance_query_migration.py`).

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned closeout slice; remote access-control, exact-candidate agent-user journey, scale and authority gates remain explicitly pending (`docs/provenance-query-closeout-evidence-20260825.json`, `tests/test_provenance_query_closeout_evidence.py`; `8ec0385`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/provenance-query-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; metadata is `active`/M1 for target release `0.6.0`, with remote access, scale, agent-user-journey and authority gates unresolved.

### Review fixes (2026-08-29)

- [x] Reject non-integer pagination `limit` and `offset` values before slicing;
  local negative-contract coverage passes (`PROVENANCE-QUERY-PAGINATION-INPUT-VALIDATION-20260829`).
- [ ] Keep C.3 and remote/scale/authority gates open; this is repository-owned
  input hardening, not external conformance evidence.
