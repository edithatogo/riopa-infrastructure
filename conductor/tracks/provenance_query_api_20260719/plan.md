# Plan: provenance_query_api_20260719

## 1. Query contract

- [x] 1.1 Define why, where, how, downstream and rebuild-impact query semantics. (`src/riopa_provenance/lineage.py`, `docs/change-and-impact-queries.md`)
- [x] 1.2 Define granularity, freshness, uncertainty and access-control responses. (`src/riopa_provenance/lineage.py`, `docs/change-and-impact-queries.md`, `tests/test_lineage.py`)
- [ ] 1.3 Build a language-neutral query conformance corpus.

## 2. Projection implementation

- [ ] 2.1 Implement relational lineage tables and indexes in DuckDB-compatible form.
- [ ] 2.2 Implement optional PROV/RDF or property-graph projection.
- [ ] 2.3 Add deterministic rebuild and schema-migration tests.

## 3. Interfaces and performance

- [ ] 3.1 Implement CLI, Python and MCP interfaces.
- [ ] 3.2 Add caching, pagination, access filtering and diagnostics.
- [ ] 3.3 Benchmark representative release and impact queries.

## 4. Stable query release

- [ ] 4.1 Validate equivalent answers across interfaces and projections.
- [ ] 4.2 Conduct user testing on real provenance questions.
- [ ] 4.3 Freeze the v1 query contract and publish migration guidance.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
