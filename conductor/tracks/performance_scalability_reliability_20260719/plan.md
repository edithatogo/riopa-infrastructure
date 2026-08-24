# Plan: performance_scalability_reliability_20260719

## 1. Benchmark contract

- [x] 1.1 Define reference datasets, workloads, correctness checks and measurement protocol. (`examples/wp010-performance-benchmark/contract.json`, `examples/wp010-performance-benchmark/workload.json`)
- [x] 1.2 Set provisional latency, throughput, resource and cost envelopes. (`examples/wp010-performance-benchmark/contract.json`, `docs/performance-benchmark-qualification-20260803.json`)
- [x] 1.3 Implement reproducible benchmark environment capture. (`scripts/capture_benchmark_environment.py`, `tests/test_benchmark_environment_capture.py`)
- [x] 1.4 Record the hosted full Meshblock 2026 acquisition as workload-shaping evidence without promoting its elapsed time to a national performance benchmark.
- [x] 1.5 Freeze a bounded national reference workload manifest linking the immutable Meshblock geography and provisional subnational population packets without an unsupported geographic join (`docs/national-workload-manifest-20260803.json`).

## 2. Load and resilience qualification

- The repository-owned rehearsal matrix is now validated, but execution remains gated on hosted infrastructure and elapsed observation; operator workflows are owner-authorized agent executions (`examples/wp010-performance-benchmark/resilience-matrix.json`).
- A `performance-rehearsal` hosted campaign lane now runs the deterministic benchmark and retains its report; its national value remains explicitly a projection.
- [x] 2.1 Run bounded local ingestion/query/accessibility rehearsal; hosted and national-scale measurement remain open. (`scripts/run_bounded_resilience_rehearsal.py`, `tests/test_resilience_matrix.py`)
- [x] 2.2 Run bounded local concurrency, retry-storm, cancellation and malformed-input rehearsal; hosted soak remains open. (`scripts/run_bounded_resilience_rehearsal.py`, `tests/test_resilience_matrix.py`)
- [x] 2.3 Record bounded deterministic recovery observables; hosted queue, storage and memory behaviour remain open. (`scripts/run_bounded_resilience_rehearsal.py`, `tests/test_resilience_matrix.py`)

## 3. Regression and capacity controls

- [x] 3.1 Add a deterministic noise-aware performance regression gate. Evidence: `src/riopa_provenance/benchmark_gates.py`, `docs/performance-noise-gate-contract-20260824.json`, `tests/test_benchmark_gates.py`; hosted soak and national-scale qualification remain pending. (contract commit: `3571af92af89474024c37834358a15e7f19d7ad8`)
- [x] 3.2 Publish bounded synthetic capacity, scaling and cost models. Evidence: `src/riopa_provenance/capacity_models.py`, `docs/performance-capacity-model-contract-20260824.json`, `tests/test_capacity_models.py`; empirical national measurements remain pending. (contract commit: `5ca8f4f95cb28cfa06a91aa8d72acbd80ac9bdb2`)
- [x] 3.3 Resolve bottlenecks without weakening correctness or provenance. A bounded diagnostic classifier now emits remediation hints; empirical bottleneck resolution remains pending. (`src/riopa_provenance/capacity_models.py`, `tests/test_capacity_models.py`)

## 4. Agent-panel v1 qualification

- [ ] 4.1 Repeat benchmarks in a second environment.
- [x] 4.2 Complete the repository-owned orchestrated method-and-results agent-panel qualification. Four bounded lenses assess the existing contracts and preserve open national, second-environment, resource/cost, elapsed and authority gates; this is not independent external evidence (`docs/performance-panel-qualification-20260825.json`, `tests/test_performance_panel_qualification.py`).
- [x] 4.3 Freeze v1 performance envelopes, limitations and operational actions. (`docs/performance-v1-envelope-freeze-20260825.json`, `tests/test_performance_v1_envelope_freeze.py`; bounded candidate only, promotion remains disallowed)

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md` for the repository-owned slice; hosted and panel gates remain explicitly pending.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains `active`/M1 because the documented gates are unresolved.
