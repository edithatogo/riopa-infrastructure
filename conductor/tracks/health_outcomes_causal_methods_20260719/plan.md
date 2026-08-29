# Plan: health_outcomes_causal_methods_20260719

## 1. Protocol and estimand framework

- [x] 1.1 Define analysis type, DAG, estimand, population, exposure, comparator and outcome records. (`schemas/health-analysis-design.schema.json`, `fixtures/health-analysis-design-synthetic.json`, `tests/test_health_analysis_design.py`; synthetic non-clinical reference only)
- [x] 1.2 Define boundary, denominator, time, missing-data and governance requirements. (`schemas/health-analysis-design.schema.json`, `fixtures/health-analysis-design-synthetic.json`, `tests/test_health_analysis_design.py`; synthetic non-clinical reference only)
- [x] 1.3 Build preregistration and exploratory/confirmatory labeling templates. (`schemas/analysis-preregistration.schema.json`, `fixtures/analysis-preregistration-synthetic.json`, `tests/test_analysis_preregistration.py`; synthetic reference only)

## 2. Reference spatial methods

- [x] 2.1 Implement descriptive mapping, autocorrelation and multilevel/ecological examples. Bounded dependency-free summaries are non-clinical and non-causal; public/synthetic source qualification remains open (`src/riopa_provenance/health_spatial.py`, `tests/test_health_spatial.py`).
- [x] 2.2 Implement spatial confounding, MAUP and measurement-error sensitivity. Bounded diagnostics remain descriptive and non-causal; source, boundary, calibration and empirical qualification remain open (`src/riopa_provenance/health_sensitivity.py`, `tests/test_health_sensitivity.py`).
- [x] 2.3 Add subgroup/equity and small-cell controls. Bounded summaries suppress cells below an explicit threshold and remain descriptive; privacy, representativeness, clinical and causal qualification remain open (`src/riopa_provenance/health_subgroups.py`, `tests/test_health_subgroups.py`).

## 3. Longitudinal and causal designs

- [x] 3.1 Implement event-study/interrupted-time-series or difference-in-differences reference workflow. The event-study wrapper requires a declared reference period and both groups per period; it remains descriptive and non-causal (`src/riopa_provenance/health_longitudinal.py`, `tests/test_health_longitudinal.py`).
- [x] 3.2 Add negative controls, missing-data and assumption diagnostics. Bounded missingness and negative-control summaries are diagnostic only; mechanism, imputation, uncertainty and causal qualification remain open (`src/riopa_provenance/health_diagnostics.py`, `tests/test_health_diagnostics.py`).
- [x] 3.3 Test on public/synthetic opening, closure or zoning-change scenarios. Synthetic opening and closure fixtures exercise the bounded event-study workflow; no real service, zoning or health claim is enabled (`fixtures/health-longitudinal-scenarios-synthetic.json`, `tests/test_health_longitudinal_scenarios.py`).

## 4. Agent-panel qualification and stable methods release

- [x] 4.1 Conduct the repository-owned orchestrated epidemiological/statistical and governance agent-panel assessment. The packet is bounded and explicitly non-qualifying; empirical, clinical and authority gates remain open (`docs/health-methods-panel-qualification-20260825.json`, `tests/test_health_methods_panel_qualification.py`).
- [x] 4.2 Resolve overclaiming, sensitivity and privacy findings for the repository-owned bounded slice. Remediation controls are recorded with promotion disabled; empirical, external and authority gates remain open (`docs/health-methods-panel-remediation-20260825.json`, `tests/test_health_methods_panel_remediation.py`).
- [x] 4.3 Publish a versioned bounded methods, reporting and limitation template. The candidate remains promotion-disabled and requires candidate-specific agent-panel reproduction, elapsed evidence and accountable authority (`docs/health-methods-reporting-template-20260825.json`, `tests/test_health_methods_reporting_template.py`).

## 5. Bounded WP-010 evidence

- [x] 5.1 Cross-check the synthetic estimand and DID contrast with a dependency-free verifier. (bdb3af6)

## Track closeout

- [x] C.1 Link implementation, test, review, migration and release evidence in `index.md`; the bounded evidence register and required agent-panel lenses are linked.
- [x] C.2 Regenerate methods, citation, roadmap status and issue configuration where affected.
- [ ] C.3 Confirm no unresolved blocking gate, expired waiver or undocumented limitation remains.
- [x] C.4 Update metadata status and target-release evidence through the Conductor workflow; status remains active/M1 because empirical and authority gates are unresolved.
- [x] C.5 Close the bounded WP-010 work-package scope under the sole-developer role-separated agent policy; empirical identification, clinical review and promotion authority remain track-level gates (`docs/wp010-single-developer-closeout-20260829.json`, `tests/test_wp010_single_developer_closeout.py`).
