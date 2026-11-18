# Track: Interoperability, conformance suites and supported SDKs

Track ID: `interoperability_conformance_sdks_20260719`  
Phase: **Core**  
Target release: **0.6.0**  
Maturity target: **M6**  
Stability class: **Platform**  
V1 critical: **yes**

## Goal

Make the v1 contracts independently implementable and testable across languages, repositories and standards projections rather than coupling them to one Python implementation.

## v1 role

This track is part of the stable v1 release contract. It is complete only when its implementation, compatibility, quality, security/governance, operational and reproducibility evidence satisfy both this specification and every applicable blocking gate in `conductor/releases.json` and `conductor/v1-gate.json`.

## Dependencies


- `provenance_profile_v1_20260718`
- `canonical_domain_schemas_ontology_20260719`
- `methods_research_objects_20260718`
- `repository_template_adoption_20260718`

## Scope

- Language-neutral golden fixtures, negative fixtures and profile-version discovery.
- Reference Python SDK, Rust models/validator and a transport-neutral query client contract.
- Conformance runners for schemas, event streams, research objects and lineage responses.
- Round-trip and bounded-loss tests for PROV-O, OpenLineage, RO-Crate and release attestations.
- Published compatibility matrix, implementation badges and extension-registration process.

## Out of scope

- Guaranteeing every third-party library or standards implementation behaves identically.
- Maintaining unlimited language SDKs without named ownership and support commitments.

## Requirements

- **R01.** Normative fixtures and expected results are independent of any implementation language.
- **R02.** A producer can declare profile, schema, extension and compatibility versions unambiguously.
- **R03.** At least two independent implementations validate the same positive and negative corpus.
- **R04.** Standards projections identify semantic loss and never claim unsupported conformance.
- **R05.** Supported SDK surfaces follow the published v1 compatibility and deprecation policy.

## Acceptance criteria

- [ ] The Python and Rust validators pass the same normative fixture suite with identical outcomes.
- [ ] At least one external or separately implemented client completes capture, validation and lineage-query workflows.
- [ ] PROV-O, OpenLineage, RO-Crate and attestation projections pass round-trip or documented bounded-loss tests.
- [ ] A versioned compatibility matrix covers schemas, CLI/API, SDKs, storage/materialisation versions and standards profiles.
- [ ] Conformance reports are machine-readable, signed with releases and suitable for independent verification.
- [ ] SDK support, deprecation and end-of-life responsibilities are named and sustainable for v1.x.

## Hardening and maturity gates

- M2 requires executable proof, negative tests and traceable evidence; interfaces may remain experimental.
- M3 requires real-data integration, migration evidence and representative failure handling.
- M4 requires repeated operation, representative agent-operated use, SLO evidence and bounded compatibility changes.
- M5 requires frozen interfaces, orchestrated agent-panel qualification, security/performance/recovery qualification and release-candidate soak.
- M6 requires supported compatibility, signed and preserved releases, isolated role-separated clean-room agent reproduction, named maintainers and post-release verification.
- Exceptions must be machine-readable, scoped, approved, time-limited and visible in release evidence.

## Evidence required

- Normative positive and negative fixture corpus.
- Cross-language conformance and standards projection reports.
- Compatibility matrix and implementation-support policy.
- Independent client or implementation validation report.

## Risks

- Reference implementation quirks accidentally become the de facto specification.
- Standards projections overstate semantic equivalence.
- Too many SDK promises create an unsustainable maintenance burden.
- Version negotiation is added too late for cross-repository migration.

## Completion rule

The track may enter `complete` only after every acceptance criterion is evidenced in `index.md`, all blocking dependencies are complete, required migrations and documentation are published, and the target release readiness evaluator reports no track-specific blocker.

## Serde suitability for conformance contracts — 18 November 2026

`rust/riopa-conformance/Cargo.toml` already depends on `serde_json`, `serde_json_canonicalizer`, `jsonschema` and SHA-256. `src/lib.rs` explicitly marks `Crosswalk::to_wire/from_wire` as a **restricted tab-delimited fixture alphabet**, not a production interchange format. **Retain this intentional constraint**. Serde cannot replace RFC 8785 canonicalization, JSON Schema checks, SHA-256, confidence/source validations or real conformance tests.

- [ ] First establish a genuine public cross-language DTO consumer and a versioned exchange schema; only then evaluate adding `serde` derive for new typed JSON values in a separate adapter. Do not retrofit Serde into the existing restricted TSV fixture or broaden claims without contract negotiation.
- [ ] Preserve JCS canonical hash vectors, Unicode ordering, float representations, duplicate key rejection, malformed/oversize input and domain-separated digest semantics; keep schema validity distinct from source truth or scientific equivalence.
- [ ] Test pinned independent Python/Rust fixtures and published crosswalk identifiers/rights. Demonstrate actual reduction of duplicated serialization code; no-go is permitted if direct JSON Value + JCS remains simpler.
- [ ] Treat source licensing, Māori data sovereignty, source provenance and human review as separate governance gates; exact-head CI and downstream consumer acceptance required. No implementation has been completed by this note.
