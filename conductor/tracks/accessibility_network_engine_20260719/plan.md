# Plan: accessibility_network_engine_20260719

## 1. Contracts and formulas

- [x] 1.1 Define network, timetable, origin/destination and travel-matrix schemas. (`schemas/accessibility-matrix.schema.json`, `docs/accessibility-contract-v1.md`)
- [x] 1.2 Specify accessibility measures, capacity and missing/unreachable semantics. (`schemas/accessibility-measure.schema.json`, `tests/test_accessibility.py`)
- [x] 1.3 Define uncertainty, subgroup and scenario contracts. A reference-only schema and validator require explicit assumptions, subgroup dimensions, missing-data policy and uncertainty method; real-network and operational qualification remain pending. (`schemas/accessibility-scenario.schema.json`, `src/riopa_provenance/accessibility.py`, `tests/test_accessibility.py`)

## 2. Reference implementations

- [~] 2.1 Implement straight-line, road/walk/cycle and public-transport adapters. The bounded Haversine coordinate adapter is implemented and tested; road, walk/cycle, timetable and real-network adapters remain disabled pending archived inputs and qualification. (`src/riopa_provenance/accessibility.py`, `tests/test_accessibility.py`; `de7a43a`)
- [x] 2.2 Implement cumulative opportunity, gravity and floating-catchment measures in the dependency-free reference core, with hand-calculated fixtures and fail-closed parameter validation. Real-network and operational qualification remain open. (`src/riopa_provenance/accessibility.py`, `tests/test_accessibility.py`, `reports/wp009-reference-solver-cores.md`)
- [x] 2.3 Add opening-hours, capacity and time-dependent calculations. Evidence: `OpeningInterval` and `reachable_capacity_at_departure` in `src/riopa_provenance/accessibility.py` with arrival-based, midnight-wrapping reference tests; no timezone, holiday, routing, timetable or operational claim is enabled.

## 3. Benchmark and scale

- [~] 3.1 Build deterministic comparisons for caller-supplied reference matrices (`src/riopa_provenance/accessibility.py:compare_reference_matrices`, `docs/accessibility-reference-comparison-contract-20260825.json`, `tests/test_accessibility.py`). Named archived inputs, independent real engines, national-scale and operational qualification remain open.
- [~] 3.2 Implement deterministic origin partitioning, fingerprint-aware caching and changed-row incremental recomputation for the dependency-free reference matrix. Real network, timetable, national-scale and operational qualification remain open (`src/riopa_provenance/accessibility.py`, `docs/accessibility-partition-cache-contract-20260825.json`, `tests/test_accessibility.py`).
- [ ] 3.3 Benchmark national-scale performance, storage and cost.
- [x] 3.4 Preserve the complete Stats NZ Meshblock 2026 supporting geography as an immutable input candidate while keeping demand, destination, network and performance claims open.

## 4. Stable accessibility interface

- [~] 4.1 Guard integration behind content-addressed network, timetable, facility and demand archive metadata (`src/riopa_provenance/accessibility.py::validate_content_addressed_archive_bundle`, `docs/accessibility-archive-bundle-readiness-20260825.json`, `tests/test_accessibility.py`). Actual payload integration, rights/authority and operational qualification remain open.
- [~] 4.2 Conduct repository-owned four-lens agent-panel qualification of reference semantics and limitations (`docs/accessibility-agent-panel-qualification-20260825.json`, `tests/test_accessibility_agent_panel_qualification.py`). Real network/timetable qualification, external workflow evidence and operational approval remain open.
- [~] 4.3 Freeze the bounded, reference-only v1 accessibility contract and examples (`docs/accessibility-v1-contract-freeze-20260825.json`, `tests/test_accessibility_v1_contract_freeze.py`). Real archived inputs, independent real-engine qualification, national scale, external workflows, elapsed evidence and accountable authority remain open.

## Track closeout

- [x] C.1 Link implementation, test, review, migration and bounded partition/cache evidence in `index.md` (`docs/accessibility-partition-cache-contract-20260825.json`, `tests/test_accessibility.py`).
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/accessibility-network-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [ ] C.4 Update metadata status and target-release evidence through the Conductor workflow.

## Review fixes

- [x] R1 Apply repository formatter to the straight-line adapter after the local quality review (`2b271c0`).
