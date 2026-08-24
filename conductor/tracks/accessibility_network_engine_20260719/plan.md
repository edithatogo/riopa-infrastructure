# Plan: accessibility_network_engine_20260719

## 1. Contracts and formulas

- [x] 1.1 Define network, timetable, origin/destination and travel-matrix schemas. (`schemas/accessibility-matrix.schema.json`, `docs/accessibility-contract-v1.md`)
- [x] 1.2 Specify accessibility measures, capacity and missing/unreachable semantics. (`schemas/accessibility-measure.schema.json`, `tests/test_accessibility.py`)
- [x] 1.3 Define uncertainty, subgroup and scenario contracts. A reference-only schema and validator require explicit assumptions, subgroup dimensions, missing-data policy and uncertainty method; real-network and operational qualification remain pending. (`schemas/accessibility-scenario.schema.json`, `src/riopa_provenance/accessibility.py`, `tests/test_accessibility.py`)

## 2. Reference implementations

- [~] 2.1 Implement straight-line, road/walk/cycle and public-transport adapters. The bounded Haversine coordinate adapter is implemented and tested; road, walk/cycle, timetable and real-network adapters remain disabled pending archived inputs and qualification. (`src/riopa_provenance/accessibility.py`, `tests/test_accessibility.py`; `de7a43a`)
- [x] 2.2 Implement cumulative opportunity, gravity and floating-catchment measures in the dependency-free reference core, with hand-calculated fixtures and fail-closed parameter validation. Real-network and operational qualification remain open. (`src/riopa_provenance/accessibility.py`, `tests/test_accessibility.py`, `reports/wp009-reference-solver-cores.md`)
- [ ] 2.3 Add opening-hours, capacity and time-dependent calculations.

## 3. Benchmark and scale

- [ ] 3.1 Build public reference instances and cross-engine comparisons from named archived network, timetable, demand and facility snapshots.
- [ ] 3.2 Implement partitioning, caching and incremental recomputation.
- [ ] 3.3 Benchmark national-scale performance, storage and cost.
- [x] 3.4 Preserve the complete Stats NZ Meshblock 2026 supporting geography as an immutable input candidate while keeping demand, destination, network and performance claims open.

## 4. Stable accessibility interface

- [ ] 4.1 Integrate only with content-addressed real NZ archive, network/timetable and facility-registry versions.
- [ ] 4.2 Conduct scientific-methods and user-workflow agent-panel qualification of semantics and limitations.
- [ ] 4.3 Freeze the v1 accessibility contract and examples.

## Track closeout

- [ ] C.1 Link implementation, test, review, migration and release evidence in `index.md`.
- [ ] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.
