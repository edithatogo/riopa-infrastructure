# Plan: supermarket_health_pilot_20260718

## 1. Protocol and reproduction

- [x] 1.1 Preregister baseline estimands, geography, population, exclusions and discrepancy handling as a synthetic/non-clinical reference template. (`docs/supermarket-health-preregistration-20260825.json`, `tests/test_supermarket_preregistration.py`; `d309f4c`)
- [x] 1.2 Implement the fail-closed density and population-normalised reference calculation over caller-supplied records (`src/riopa_provenance/supermarket.py`, `tests/test_supermarket_density.py`, `docs/supermarket-density-reference-contract-20260825.json`). Real supermarket archives, motivating-study reproduction and population authority remain open.
- [x] 1.3 Publish a transparent descriptor comparison with the motivating work, without claiming reproduction when the motivating-study source payload is absent. (`src/riopa_provenance/supermarket.py`, `tests/test_supermarket_density.py`, `docs/supermarket-reference-comparison-20260825.json`; rights-cleared source archives, factual external reproduction and empirical health evidence remain open)

## 2. Access and health geography

- [ ] 2.1 Build versioned supermarket registry and multimodal accessibility measures.
  - [x] Implement a fail-closed integration contract requiring a versioned, public-only, non-authoritative supermarket assertion snapshot and distinct distance, network, multimodal, capacity and competition measures. (`src/riopa_provenance/supermarket_pilot.py`, `tests/test_supermarket_pilot.py`; `2904517`)
- [ ] 2.2 Analyse deprivation, demographic, rurality, competition/capacity and health outcomes.
  - [x] Implement bounded area-record binding that separates context, access and explicitly ecological aggregate-health records while retaining denominators, source references and small-cell status. (`src/riopa_provenance/supermarket_pilot.py`, `tests/test_supermarket_pilot.py`; `2904517`)
- [ ] 2.3 Run spatial, boundary, facility and causal-sensitivity analyses.
  - [x] Require spatial-confounding, MAUP and measurement-error sensitivity evidence in the bounded reference packet; empirical boundary/facility sensitivity remains pending. (`src/riopa_provenance/supermarket_pilot.py`, `tests/test_supermarket_pilot.py`; `2904517`)

## 3. Planning feasibility and alternatives

- [ ] 3.1 Construct candidate sites from linked plans/rules and documented exclusions.
  - [x] Implement citation-digest validation and fail-closed exclusion of prohibited or unresolved planning candidates. (`src/riopa_provenance/supermarket_pilot.py`, `tests/test_supermarket_pilot.py`; `2904517`)
- [ ] 3.2 Run coverage, p-median/p-center, capacity, equity and robust alternatives.
  - [x] Bind caller-supplied alternatives to a complete average, worst-case, subgroup, capacity, competition, cost and robustness metric contract. Representative solver execution remains pending. (`src/riopa_provenance/supermarket_pilot.py`, `tests/test_supermarket_pilot.py`; `2904517`)
- [ ] 3.3 Report Pareto trade-offs and non-modelled commercial/community constraints.
  - [x] Implement deterministic Pareto reporting that requires market, land, community and consent constraints and cannot select or promote a preferred site. (`src/riopa_provenance/supermarket_pilot.py`, `tests/test_supermarket_pilot.py`; `2904517`)

## 4. Independent publication

- [ ] 4.1 Conduct methods, planning, governance and reproducibility review.
- [ ] 4.2 Generate complete methods, data and software research objects.
- [ ] 4.3 Publish manuscript/preprint, limitations and correction path.

## 5. Bounded WP-010 evidence

- [x] 5.1 Register public-data candidates and fail closed where supermarket source rights are undeclared. (bdb3af6)
- [x] 5.2 Capture a local-only OSM regional sensitivity observation without authoritative or completeness claims. (37510dd)

## Track closeout

- [x] C.1 Link current implementation, test and Conductor review evidence in `index.md`; migration, empirical and release evidence remain explicitly unavailable.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected. The locked methods generation, roadmap status, issue graph and full quality harness passed; the methods output was temporary and not a release artifact (`docs/supermarket-conductor-regeneration-20260825.json`).
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; metadata remains `active`/M1 for target release `0.8.0`, with rights-cleared supermarket data, empirical health linkage, preservation and accountable-authority gates unresolved.
- [x] C.5 Close the bounded WP-010 work-package scope under the sole-developer role-separated agent policy; empirical health, national completeness, operative planning and promotion authority remain track-level gates (`docs/wp010-single-developer-closeout-20260829.json`, `tests/test_wp010_single_developer_closeout.py`).

## Review fixes

- [x] R1 Wrap the preregistration test path so the repository quality gate passes (`9db5186`).
- [x] R2 Reject negative measures, protect suppressed small-cell rates, re-derive planning dispositions from cited rules, validate metric domains and preserve domain-specific errors for malformed alternatives. (`25ac176`)
