# Evidence index: Queryable provenance and impact-analysis API

- **Track ID:** `provenance_query_api_20260719`
- **Status:** `active`
- **Target release:** `0.6.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `High` / `P1`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Core platform maintainer
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/69

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-005-lineage-query-envelope-20260731` | Where, why, how and rebuild-impact responses state authoritative evidence, projection hash and actual granularity | `src/riopa_provenance/lineage.py`, `tests/test_lineage.py`, `docs/change-and-impact-queries.md` | Python/SQLite synthetic conformance passes; CLI, MCP, graph equivalence, access control and real-release evidence remain open |
| `PROVENANCE-QUERY-CONTRACT-20260822` | Query semantics and evidence envelopes for where/why/how/impact responses | `src/riopa_provenance/lineage.py`, `docs/change-and-impact-queries.md`, `tests/test_lineage.py` | Repository-owned Python/SQLite contract passes; language-neutral corpus, interface equivalence, access control and real-release evidence remain open |
| `PROVENANCE-QUERY-CORPUS-20260822` | Language-neutral where/why/how/impact cases with deterministic expected answers and evidence envelopes | `docs/provenance-query-conformance-corpus-20260822.json`, `tests/test_provenance_query_corpus.py` | Synthetic SQLite/Python reference passes; graph equivalence, interfaces, access control, performance and real-release evidence remain open |
| `PROVENANCE-QUERY-REBUILD-20260825` | Deterministic logical projection fingerprint and migration/rebuild equivalence contract | `src/riopa_provenance/lineage.py`, `tests/test_lineage.py`, `docs/provenance-query-rebuild-contract-20260825.json` | Repository contract passes; graph/interface equivalence, access control, scale, real-release and external-user gates remain open |
| `PROVENANCE-QUERY-DUCKDB-20260825` | Deterministic DuckDB-compatible relational lineage export with source/projection digest binding | `src/riopa_provenance/lineage.py::LineageIndex.export_duckdb`, `tests/test_lineage.py` | Repository projection export is validated; graph equivalence, interface/access-control, performance and real-release evidence remain open |
| `PROVENANCE-QUERY-DUCKDB-FINGERPRINT-20260825` | DuckDB export receipts retain the logical SQLite projection fingerprint alongside file and source digests | `src/riopa_provenance/lineage.py::LineageIndex.export_duckdb`, `tests/test_lineage.py` | Cross-projection identity is explicitly bound; graph equivalence, interface/access-control, performance and real-release evidence remain open |
| `PROVENANCE-QUERY-PROV-JSONLD-20260825` | Deterministic PROV-JSON-LD projection with digest binding and explicit non-authority controls | `src/riopa_provenance/lineage.py`, `tests/test_lineage.py`, `docs/provenance-query-prov-jsonld-contract-20260825.json` | Projection contract passes; RDF/SHACL, semantic-loss, external-client, access, scale and authority gates remain open |
| `PROVENANCE-QUERY-CLI-20260825` | CLI access to the bounded lineage query and PROV-JSON-LD projection surfaces | `src/riopa_provenance/cli.py`, `tests/test_cli.py` | CLI commands pass repository tests; MCP transport, cross-interface equivalence, access-control and external-user evidence remain open |
| `PROVENANCE-QUERY-PAGINATION-20260825` | Bounded deterministic node pagination with projection diagnostics | `src/riopa_provenance/lineage.py`, `src/riopa_provenance/cli.py`, `tests/test_lineage.py`, `tests/test_cli.py`, `docs/provenance-query-pagination-diagnostics-contract-20260825.json` | Local contract passes; caching, remote authorization, scale, MCP, external-user and authority gates remain open |
| `PROVENANCE-QUERY-BENCHMARK-20260825` | Environment-bound timing harness for where/why/impact/page queries | `scripts/benchmark_lineage_queries.py`, `tests/test_provenance_query_benchmark.py` | Local harness passes; release-scale, second-environment, access-control, MCP, external-user and authority gates remain open |
| `PROVENANCE-QUERY-EQUIVALENCE-20260825` | Bounded Python/CLI answers and SQLite/DuckDB/PROV-JSON-LD edge projections agree on the synthetic manifest | `docs/provenance-query-equivalence-contract-20260825.json`, `tests/test_provenance_query_equivalence.py` | Repository-owned equivalence passes; MCP transport, remote access filtering, real-release and external-user evidence remain open |
| `PROVENANCE-QUERY-CACHE-20260825` | In-process query cache is bounded, deep-copying and keyed by logical projection fingerprint | `src/riopa_provenance/lineage.py::QueryCache`, `src/riopa_provenance/lineage.py::LineageIndex.query_cached`, `docs/provenance-query-cache-contract-20260825.json`, `tests/test_lineage.py` | Local cache contract passes; distributed/persistent cache, remote authorization, access filtering and production-scale performance remain open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: API/schema analyst, Provenance analyst, Operations analyst, External-user workflow analyst.

This index is deliberately bounded while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
