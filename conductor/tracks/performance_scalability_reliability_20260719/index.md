# Evidence index: Performance, scalability and reliability qualification

- **Track ID:** `performance_scalability_reliability_20260719`
- **Status:** `specified`
- **Target release:** `0.9.0`
- **Current maturity:** `M1`
- **Maturity target:** `M6`
- **Stability class:** `Operational`
- **Risk / priority:** `Critical` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Release manager
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/134

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-004-resource-envelopes-20260731` | Every sharded archive job has enforced storage and egress ceilings | `src/riopa_provenance/linz_pipeline.py`, `src/riopa_provenance/linz_inventory.py`, `tests/test_linz_pipeline.py`, `tests/test_linz_inventory.py` | Boundary and overrun tests pass; national-scale benchmark remains open |
| `WP-009-small-instance-correctness-oracle-20260731` | Deterministic exhaustive accessibility/location fixtures provide a correctness baseline for later scalable-engine comparisons | `src/riopa_provenance/accessibility.py`, `src/riopa_provenance/facility_location.py`, `tests/test_accessibility.py`, `tests/test_facility_location.py`, `reports/wp009-reference-solver-cores.md` | Small-instance correctness passes; no national-scale performance, cost, soak or recovery claim is made |
| `PERF-HOSTED-OPTIONS-20260802` | Hosted runner and national-workload execution options are explicit and fail closed | `docs/remaining-gates-autonomous-plan-20260802.json`, `.github/workflows/evidence-campaign.yml`, `scripts/record_hosted_evidence.py`, `tests/test_hosted_evidence.py` | GitHub scale-smoke lane implemented; Hugging Face Jobs is a budget-gated fallback; no national run claimed |
| `PERF-HOSTED-SMOKE-20260802` | Exact-revision performance correctness smoke executes in a hosted runner | `docs/hosted-evidence-batch-20260802.json`, [GitHub Actions run 30744487469](https://github.com/edithatogo/riopa-infrastructure/actions/runs/30744487469) | Passed; not a national-scale workload or capacity measurement |
| `PERF-HF-LIBRARY-ASSESSMENT-20260802` | Secondary hosted runner, public workload and measurement-library options are bounded | `docs/hugging-face-evidence-runner-plan-20260802.json`, `docs/remaining-gates-campaign-v2-20260802.md` | No authoritative HF national workload found; `pyperf`/`psutil` remain benchmark-only candidates |
| `PERF-CAMPAIGN-V3-20260802` | Current national-workload, runner and measurement-library options are reconciled without overclaiming | `docs/remaining-gates-campaign-v3-20260802.json`, `docs/remaining-gates-campaign-v3-20260802.md`, `docs/hugging-face-evidence-runner-plan-v2-20260802.json`, `tests/test_campaign_v3.py` | No authoritative workload was selected through HF; retain current stack, source official workload manifests independently and keep national measurement open |
| `PERF-MESHBLOCK-ACQUISITION-20260802` | A full national supporting-geography acquisition runs on hosted infrastructure with content and completeness evidence | [GitHub Actions run 30750165664](https://github.com/edithatogo/open_social_data/actions/runs/30750165664), `docs/public-dataset-archive-incorporation-plan-20260802.json` | 57,575 features captured and published in 5m19s end-to-end; this is acquisition evidence, not an ingestion, accessibility, optimisation, capacity or national-performance benchmark |
| `PERF-NATIONAL-WORKLOAD-MANIFEST-20260803` | A bounded national reference workload links exact immutable geography and population packets | `docs/national-workload-manifest-20260803.json`, `config/archive-sources/stats-nz-subnational-population-2025.json`, [population archive track](https://github.com/edithatogo/open_social_data/tree/9e96300e83b21b78f4116bc00fc141bf5f1efcad/conductor/tracks/stats_nz_population_archive_20260802) | Both packets are revision- and digest-bound; alignment is reference-only and does not establish a population-weighted national benchmark |
| `PERF-CONTRACT-QUALIFICATION-20260803` | Benchmark contract, environment capture, envelopes and resilience boundaries are machine-readable | `examples/wp010-performance-benchmark/contract.json`, `scripts/capture_benchmark_environment.py`, `docs/performance-benchmark-qualification-20260803.json` | Repository contract and regional rehearsal qualify; national-scale measurements, resource/cost instrumentation, production failure injection and panel qualification remain open |
| `PERF-BENCHMARK-CONTRACT-20260821` | Phase 1 benchmark contract, provisional envelopes and reproducible environment capture are directly tested | `examples/wp010-performance-benchmark/contract.json`, `scripts/capture_benchmark_environment.py`, `tests/test_wp010_performance_contract.py`, `tests/test_benchmark_environment_capture.py` | Repository-owned phase complete; measurements, resource/cost instrumentation, resilience and panel gates remain open |
| `PERF-RESILIENCE-MATRIX-20260821` | Load, retry, cancellation, malformed-input and recovery observables are specified in a fail-closed rehearsal matrix | `examples/wp010-performance-benchmark/resilience-matrix.json`, `scripts/validate_resilience_matrix.py`, `tests/test_resilience_matrix.py` | Matrix validated; it is not executed evidence and does not close hosted, soak, recovery, national-scale or external-operator gates |
| `PERF-HOSTED-REHEARSAL-LANE-20260821` | Hosted campaign can execute the bounded deterministic benchmark and preserve its report beside the content-bound receipt | `.github/workflows/evidence-campaign.yml`, `scripts/record_hosted_evidence.py`, `tests/test_hosted_evidence.py` | Lane implemented and locally validated; hosted run and all operational evidence gates remain pending |
| `PERF-HOSTED-SCALE-SMOKE-20260821` | Hosted archived/reference scale-smoke runs the accessibility and facility-location fixture suites on protected main | [GitHub Actions run 32422572545](https://github.com/edithatogo/riopa/riopa-infrastructure/actions/runs/32422572545), artifact `evidence-campaign-agent-workflows-20260821-scale-smoke-32422572545` | Passed at `4228f07`; reference rehearsal only, not national-scale measurement or enabled facility claims |
| `PERF-BOUNDED-RESILIENCE-REHEARSAL-20260822` | Local deterministic concurrency, retry, cancellation, malformed-input and recovery rehearsal | `scripts/run_bounded_resilience_rehearsal.py`, `tests/test_resilience_matrix.py` | All bounded cases pass without live endpoints; hosted infrastructure, elapsed soak, resource/cost and national-scale evidence remain open |

## Blocking defects

- National-scale ingestion/accessibility/optimisation benchmarks, resource and
  cost envelopes, soak tests and stress/recovery evidence remain open.

## Decisions, exceptions and limitations

- Exhaustive reference solvers are validation oracles rather than performance
  implementations.

## Review and handover

Required agent-panel lenses: Performance analyst, Operations analyst, Security analyst, Data-governance analyst, Quantitative methods analyst, Agent workflow analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
