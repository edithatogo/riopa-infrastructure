# Track: Council planning spatial-to-rule linkage

Track ID: `planning_rules_linkage_20260718`  
Phase: **NZ Spatial**  
Target release: **0.6.0**  
Maturity target: **M6**  
Stability class: **Reference**  
V1 critical: **yes**

## Goal

Link zoning, overlays, precincts and other planning geometries to versioned plans and provisions with transparent evidence, review, confidence and legal-status limitations.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `nz_spatial_archive_mvp_20260718`
- `canonical_domain_schemas_ontology_20260719`

## Scope

- Plan, plan-version, chapter, provision and rule identities.
- Spatial-feature to provision-version relationships and evidence.
- Extraction, citation, link confidence, agent-panel review and disagreement.
- Zone/overlay/precinct/designation crosswalks that preserve original meaning.
- Feasibility queries that distinguish permitted, discretionary, prohibited and unresolved states.

## Out of scope

- Automated legal advice or definitive consent outcomes.
- Replacing source plan text with a simplified national code.

## Requirements

- **R01.** Spatial and textual sources remain separately preserved and cited.
- **R02.** A link is a sourced assertion with method, confidence, reviewer and valid period.
- **R03.** Overlays and provisions can combine without flattening exceptions or hierarchy.
- **R04.** Unresolved, appealed or partly operative states remain representable.
- **R05.** Feasibility outputs expose all relevant rule sources and uncertainty.

## Acceptance criteria

- [ ] Stable identifiers represent plan/version/provision and survive document repagination where possible.
- [ ] At least two councils with materially different plan structures complete spatial-to-rule linkage.
- [ ] Automated or AI-assisted extraction records model/tool evidence and receives review by a multi-agent panel before release.
- [ ] Orchestrated agent-panel qualification samples quantify missing and incorrect links.
- [ ] Feasibility queries return cited rules, status, confidence and caveats rather than one unsupported boolean.
- [ ] Cross-council mappings preserve original classes and provenance.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Plan/provision identity and linkage schemas.
- Linked council examples with source citations.
- Orchestrated agent-panel qualification, false-link and missing-link analysis.
- Feasibility query fixtures and limitation report.

## Risks

- GIS labels do not map cleanly to plan provisions.
- Document structure or page numbering changes.
- AI extraction appears authoritative despite uncertainty.
- Combined rules create context-dependent feasibility not captured by simple categories.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
