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
| `PROVENANCE-QUERY-DUCKDB-20260825` | Deterministic DuckDB-compatible relational lineage export with source/projection digest binding | `src/riopa_provenance/lineage.py::LineageIndex.export_duckdb`, `tests/test_lineage.py` | Repository projection export is validated; graph equivalence, interface/access-control, performance and real-release evidence remain open |

## Blocking defects

- None recorded.

## Decisions, exceptions and limitations

- None recorded.

## Review and handover

Required agent-panel lenses: API/schema analyst, Provenance analyst, Operations analyst, External-user workflow analyst.

This index is deliberately bounded while the track remains `active`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
