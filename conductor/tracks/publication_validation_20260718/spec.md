# Track: Independent validation, release and publication programme

Track ID: `publication_validation_20260718`  
Phase: **Publication**  
Target release: **0.9.0**  
Maturity target: **M6**  
Stability class: **Reference**  
V1 critical: **yes**

## Goal

Convert infrastructure, data and applied work into independently validated, citable releases and manuscripts with reproducible evidence and transparent correction.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `repository_template_adoption_20260718`
- `nz_spatial_archive_mvp_20260718`
- `methods_research_objects_20260718`
- `security_supply_chain_20260719`

## Scope

- Agent-panel conformance, clean-room reproduction and agent-user workflow validation protocols.
- Software, schema, ontology, dataset, model and research-object release coordination.
- DOI/citation, preprint/manuscript, data-descriptor and methods-paper packages.
- Publication-feedback response, correction, supersession and retraction evidence.
- Evidence coverage, claim-to-artifact traceability and publication ethics.

## Out of scope

- Treating a DOI or passing unit tests as sufficient independent reproduction.
- Coupling every software release to a manuscript release.

## Requirements

- **R01.** Each scientific claim has a traceable analysis, data, code, environment and limitation record.
- **R02.** Separately prompted advisory agents use preserved public inputs and documented interfaces; their output is repository-owned advice, not independent human or external validation.
- **R03.** Failures and deviations are published rather than normalised away.
- **R04.** Software, schemas, data and papers cite exact immutable versions.
- **R05.** Corrections preserve prior versions and explain downstream impact.

## Acceptance criteria

- [ ] At least one complete real-data release and one applied benchmark are reproduced by an owner-authorized agent.
- [ ] RO-Crate, DataCite, provenance, SBOM, attestation and archive validations pass with exact validator versions recorded.
- [ ] Infrastructure/methods, spatial data descriptor and applied-study publication packages are complete or have explicit post-v1 sequencing.
- [ ] Claim-to-evidence matrices identify unsupported, exploratory and confirmatory statements.
- [ ] Correction and supersession exercises update citations and downstream impact without erasing history.
- [ ] Agent-operated workflows can discover, install, query, reproduce and cite releases from public documentation.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, agent reproduction, a named owner and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- External validation and clean-room reproduction reports.
- Claim-to-evidence matrices and publication packages.
- DOI/citation and preservation records.
- Correction/supersession and user-validation exercises.

## Risks

- Agent analysts unknowingly rely on local caches or unpublished credentials.
- Publication schedules pressure maintainers to weaken release gates.
- Manuscript claims drift from final release artifacts.
- Corrections fragment citations or leave downstream users unaware.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
