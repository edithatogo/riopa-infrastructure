# Track: Documentation, developer experience and user support readiness

Track ID: `documentation_developer_experience_20260719`  
Phase: **Publication**  
Target release: **0.9.0**  
Maturity target: **M6**  
Stability class: **Platform**  
V1 critical: **yes**

## Goal

Ensure that people outside the founding team can install, understand, operate, extend, reproduce and safely apply the stable v1 system without undocumented institutional knowledge.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `repository_template_adoption_20260718`
- `methods_research_objects_20260718`
- `provenance_query_api_20260719`
- `interoperability_conformance_sdks_20260719`
- `nz_spatial_archive_operations_20260719`
- `accessibility_network_engine_20260719`
- `facility_location_engine_20260718`

## Scope

- Task-oriented user, operator, contributor, maintainer and migration documentation.
- Executable tutorials and reference examples for the principal v1 workflows.
- API/CLI/schema references generated from normative sources where possible.
- Troubleshooting, diagnostics, support channels and issue triage expectations.
- Documentation accessibility, terminology, limitations and safety review.

## Out of scope

- Claiming that documentation alone makes reference analytics fit for operational or clinical use.
- Supporting every deployment environment or bespoke downstream workflow.

## Requirements

- **R01.** Every stable public interface has reference, task and migration documentation.
- **R02.** Tutorials are executed in CI or scheduled clean environments against released artifacts.
- **R03.** Examples use public or synthetic data and state rights, limitations and intended use.
- **R04.** Support scope, response expectations, escalation and end-of-life are explicit.
- **R05.** User research includes people not involved in implementation and records unresolved friction.

## Acceptance criteria

- [ ] Two owner-authorized agents complete distinct end-to-end workflows using only released documentation.
- [ ] An owner-authorized agent completes installation, scheduled update, failure diagnosis and restore exercises.
- [ ] All executable tutorials and examples pass against the release candidate in clean environments.
- [ ] API, CLI, schema, ontology, configuration, migration and troubleshooting references are complete and versioned.
- [ ] Documentation passes link, code-example, terminology, accessibility and limitation checks.
- [ ] Named support channels, triage rules, maintainer responsibilities and sustainability bounds are published.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, representative agent-operated use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, isolated role-separated clean-room agent reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Documentation inventory and automated documentation test results.
- Agent-operated user and operator validation reports.
- Accessibility, terminology and limitation review.
- Support, triage and maintainer ownership policy.

## Risks

- Documentation reflects intended rather than actual behaviour.
- Successful workflows depend on undocumented credentials or local state.
- Examples encourage causal, legal or clinical overinterpretation.
- Support promises are broader than sustainable maintainer capacity.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
