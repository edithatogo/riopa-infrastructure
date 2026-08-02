# Track: Research objects, methods supplements and citation automation

Track ID: `methods_research_objects_20260718`  
Phase: **Core**  
Target release: **0.4.0**  
Maturity target: **M6**  
Stability class: **Platform**  
V1 critical: **yes**

## Goal

Generate concise citable methods and publication-grade supplementary evidence from the same validated release facts and package them as complete, externally verifiable research objects.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `provenance_profile_v1_20260718`
- `security_supply_chain_20260719`

## Scope

- Schema-driven validation of arbitrary research bundles and every referenced record.
- RO-Crate and workflow/run projections, DataCite metadata, CFF, PROV and OpenLineage exports.
- Methods facts, concise methods, full supplementary methods and limitation generation.
- SBOMs, signatures, attestations, checksums, preservation and clean-room rebuild evidence.
- Deterministic packaging without cyclic or incomplete file metadata.

## Out of scope

- Generating unsupported scientific or legal claims from missing evidence.
- Bundling restricted payloads merely because their metadata are public.

## Requirements

- **R01.** The generator reports missing evidence and fails stable publication rather than inventing text.
- **R02.** All local references are path-safe, schema-validated and integrity checked.
- **R03.** Package indexes have a documented non-circular integrity design.
- **R04.** Citation and methods outputs are derived from one facts record and checked for consistency.
- **R05.** External profile conformance is claimed only when the corresponding representation is present and validated.

## Acceptance criteria

- [ ] The validator discovers record schemas generically and rejects malformed records regardless of filename.
- [ ] A complete real-data research object passes external RO-Crate and metadata validation.
- [ ] Short methods, full supplement, methods facts, citation and manifest agree under automated checks.
- [ ] The bundle includes payload or resolvable-content evidence, quality, rights, SBOM, attestations, environment and preservation records.
- [ ] Two clean builds are content-identical or have declared and verified tolerance differences.
- [ ] A clean-room agent analyst can verify and cite the release without repository-specific knowledge.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, external use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, independent review, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, external reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Positive and negative arbitrary-bundle fixtures.
- External RO-Crate/DataCite/conformance reports.
- Deterministic package and checksum reports.
- Clean-room reproduction and citation usability review.

## Risks

- Package manifests or hashes become cyclic and unverifiable.
- Methods prose drifts from machine facts.
- Conformance URLs are declared before profiles are actually emitted.
- Publication tooling leaks restricted source content.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.
