# Evidence index: Interoperability, conformance suites and supported SDKs

- **Track ID:** `interoperability_conformance_sdks_20260719`
- **Status:** `validating`
- **Target release:** `0.6.0`
- **Current maturity:** `M2`
- **Maturity target:** `M6`
- **Stability class:** `Platform`
- **Risk / priority:** `High` / `P0`
- **V1 critical:** `yes`
- **Owner repository:** `edithatogo/riopa-infrastructure`
- **Owner role:** Core platform maintainer
- **GitHub issue:** https://github.com/edithatogo/riopa-infrastructure/issues/64

## Evidence register

| Evidence ID | Acceptance criterion or gate | Artifact, persistent identifier or URL | Review state |
|---|---|---|---|
| `WP-006-python-node-conformance-20260731` | Independent Python and Node runners reproduce canonical hashes and positive/negative schema outcomes from one language-neutral corpus | `conformance/v1/corpus.json`, `scripts/conformance_node.mjs`, `tests/test_conformance.py`, `docs/conformance-and-release-verification.md` | Bounded corpus passes; Rust, full JSON Schema, standards projections, external client and signed conformance report remain open |
| `WP-008-fyi-adapter-conformance-20260731` | `fyi-cli` and `fyi-archive` native fields are classified without treating approximate or extension-only mappings as exact | `conformance/adapters/fyi-cli.json`, `conformance/adapters/fyi-archive.json`, `conformance/adapters/report.json`, `tests/test_adapters.py`, `reports/wp008-cross-repository-adapters.md` | Central schema, semantic and deterministic aggregate checks pass; related PRs #285 and #319 are merged |
| `INTEROP-CONTRACT-20260822` | Language-neutral positive, negative and migration fixtures plus conservative profile/version negotiation | `schemas/interoperability-conformance-contract.schema.json`, `docs/interoperability-conformance-contract-20260822.json`, `docs/interoperability-conformance-contract-20260822.md`, `conformance/v1/corpus.json`, `tests/test_interoperability_conformance_contract.py` | Tasks 1.1–1.3 pass repository validation; Rust, standards projections, external-client and signed-report gates remain open |
| `PYTHON-SDK-20260825` | Deterministic Python producer-side validation for schema and bounded crosswalk contracts | `src/riopa_provenance/sdk.py`, `tests/test_sdk.py`, `docs/python-reference-sdk-20260825.md` | Local fixture and semantic checks pass; this does not establish independent implementation, external-client, signed-report or release conformance |
| `LINEAGE-QUERY-CONTRACT-20260825` | Strict, versioned, transport-neutral lineage query request | `src/riopa_provenance/lineage.py`, `tests/test_lineage.py` | Local serialization round-trip passes; no remote endpoint, authorization, external client or release evidence is claimed |
| `INTEROP-COMPATIBILITY-MATRIX-20260825` | Cross-version/tool compatibility status is recorded from the bounded Python/Node corpus | `scripts/build_interoperability_matrix.py`, `docs/ontology/interoperability-compatibility-matrix-20260825.json`, `tests/test_interoperability_matrix.py` | Python/Node parity observed locally; Rust, standards round-trips and external producer/consumer exercises remain unobserved |
| `INTEROP-STANDARDS-ROUNDTRIP-20260825` | Bounded PROV-O-shaped, OpenLineage-shaped, RO-Crate and DSSE/in-toto payloads round-trip through repository validators | `docs/interoperability-standards-roundtrip-contract-20260825.json`, `tests/test_standards_roundtrip_contract.py` | Repository-owned round-trips pass; external producer/consumer interoperability, full validator qualification and trusted signing remain open |
| `INTEROP-RUST-MODEL-20260825` | Rust typed crosswalk, migration model and canonical corpus hash runner validate bounded contract failures | `rust/riopa-conformance/`, `docs/rust-conformance-model-contract-20260825.json`, `docs/rust-corpus-parity-20260825.json`, `.github/workflows/validate.yml` | Local/hosted typed-model and five-case canonical-hash parity tests pass; schema-validity parity, full numeric RFC 8785 handling, independent producer/consumer interoperability and signed release conformance remain open |
| `INTEROP-PRODUCER-CONSUMER-20260825` | Dependency-free Rust/Python producer and consumer exchange exercise passes in both directions | `rust/riopa-conformance/src/bin/conformance_exchange.rs`, `tests/test_rust_producer_consumer.py`, `docs/interop-producer-consumer-exercise-20260825.json` | Repository-owned wire-format exercise passes; external independent implementations, standards-complete serialization and signed release conformance remain open |
| `INTEROP-FINDINGS-LEDGER-20260825` | Fail-closed semantic-loss and migration findings ledger derived from the compatibility matrix | `scripts/build_interoperability_findings.py`, `tests/test_interoperability_findings.py`, `docs/interoperability-findings-ledger-contract-20260825.json`, `docs/rust-corpus-parity-20260825.json` | Migration-corpus and bounded Rust/Python hash-parity findings resolve; external producer/consumer, standards-round-trip and signed-report gates remain open |
| `RUST-CORPUS-PARITY-20260825` | Rust runner matches all five canonical corpus SHA-256 fixtures | `rust/riopa-conformance/src/bin/conformance_corpus.rs`, `docs/rust-corpus-parity-20260825.json`, `tests/test_rust_producer_consumer.py` | Bounded canonical-hash parity passes; schema-validity parity, full numeric RFC 8785 handling, external implementation, signing, preservation and authority remain open |
| `INTEROP-V1-SDK-SUPPORT-20260825` | Bounded Python/Rust SDK surfaces, compatibility policy and conformance-report fields | `docs/interoperability-v1-sdk-support-and-reporting-20260825.md`, `docs/interoperability-v1-sdk-support-contract-20260825.json`, `tests/test_interoperability_v1_support.py` | Support surface and report template are explicit; broader standards conformance, trusted stable-candidate signing and preservation, and release promotion remain open |
| `INTEROP-CLOSEOUT-EVIDENCE-20260825` | Link implementation, tests, review, migration and release-candidate exercise evidence for the bounded interoperability slice | `docs/interoperability-closeout-evidence-20260825.json`, `tests/test_interoperability_closeout_evidence.py` | Evidence categories are linked and fail-closed; external implementations, signing, preservation and authority gates remain open |
| `WP006-EXTERNAL-ROCRATE-VALIDATION-20260829` | Independently maintained RO-Crate validator checks published and remediated research objects | `docs/wp006-external-rocrate-validation-20260829.json`, `src/riopa_provenance/crate.py`, `tests/test_crate.py` | v0.3.0 failure preserved; prospective output passes 65/65 required RO-Crate 1.2 checks; separate producer/consumer, preservation and release gates remain open |
| `WP006-HOSTED-SBOM-VALIDATION-20260829` | Exact merged revision executes strict CycloneDX 1.6 validation in a dedicated hosted security lane | `docs/wp006-hosted-sbom-validation-20260829.json`, [run 33232065327](https://github.com/edithatogo/riopa-infrastructure/actions/runs/33232065327) | Hosted run and digest-bearing artifact pass; the official locked validator is not represented as a separate external implementation |
| `SEPARATE-RUST-CLIENT-WORKFLOW-20260829` | Separately implemented client completes capture, validation and lineage-query workflows | `rust/riopa-conformance/src/bin/client_workflow.rs`, `conformance/v1/client-workflow.json`, `tests/test_rust_producer_consumer.py`, `docs/separate-rust-client-workflow-20260829.json` | Repository-owned Rust implementation passes positive and negative workflows; satisfies the separately implemented branch without claiming external authorship, live operation or release conformance |
| `INTEROP-M2-TECHNICAL-PREVIEW-20260829` | Owner-approved experimental M2 transition and protected technical-preview conformance asset | `scripts/build_release_conformance_report.py`, `.github/workflows/release.yml`, `tests/test_v040_release_preparation.py` | M2/validating only; M3-M6, programme 0.4.0 data gates, preservation and stable-v1 gates remain open |
| `V040-PUBLICATION-20260829` | Exact merged technical preview is built, checksummed, OIDC-attested, published, downloaded and independently reverified | `docs/v0.4.0-release-publication-20260829.json`, [release](https://github.com/edithatogo/riopa-infrastructure/releases/tag/v0.4.0), [run 33236124879](https://github.com/edithatogo/riopa-infrastructure/actions/runs/33236124879) | Public prerelease passes GitHub publication and 65/65 RO-Crate checks; Zenodo/Hugging Face were not attempted in the historical receipt; stable-v1 gates remain open |
| `V040-RELEASE-MIRROR-20260829` | Preserve a successor receipt for the byte-preserving Hugging Face mirror without mutating the historical publication receipt | `docs/v0.4.0-release-mirror-20260829.json`, [Hugging Face commit ebecf6d3](https://huggingface.co/datasets/edithatogo/riopa-evidence-campaign/commit/ebecf6d38084aa459b27ef2bf753505003b08a16) | All six release assets plus bounded metadata are anonymously byte-reverified; this is not DOI/Zenodo preservation and does not close stable-v1 gates |
| `V040-ZENODO-PRESERVATION-20260829` | Preserve the exact six release assets with a DOI and anonymously reverify the public record without mutating predecessor receipts | `docs/v0.4.0-zenodo-preservation-20260829.json`, [DOI 10.5281/zenodo.22156988](https://doi.org/10.5281/zenodo.22156988) | Zenodo record is published and all six files pass byte equality plus the release SHA-256 manifest; programme data, elapsed-operation and stable-v1 gates remain open |
| `V040-PRESERVATION-WP006-RECONCILIATION-20260829` | Recalculate WP-006 against both immutable successor receipts | `docs/v0.4.0-preservation-wp006-reconciliation-20260829.json`, `tests/test_v040_preservation_wp006_reconciliation.py` | Public-preview preservation is complete; broader claimed-profile conformance and a trusted signed exact-stable-candidate report remain open |

The same revision’s Conductor regeneration receipt records the methods hash,
roadmap status, generated issue graph and full quality harness. This closes only
the bookkeeping task; it does not establish external conformance or signed
release evidence (`docs/interoperability-conductor-regeneration-20260825.json`).

## Blocking defects

- No defect blocks the bounded experimental M2 slice. Remaining WP-006 maturity
  gates are broader claimed-profile standards conformance, a trusted signed
  exact-stable-candidate report, stable-candidate preservation and authority.

## Remaining maturity gates

Implementation evidence is bounded to the recorded conformance slices. Full-schema,
standards-complete projection, a trusted signed exact-stable-candidate report,
stable-candidate preservation and release-authority evidence remain open; the track must not be marked complete
or archived until its M2–M6 acceptance evidence is recorded.

## Decisions, exceptions and limitations

- The adapters do not upgrade approximate, extension-only or unmapped fields to
  exact equivalence and do not constitute a full conformance certificate.

The 2026-08-25 closeout packet links the bounded SDK, Rust/Python exchange,
compatibility, findings and report-guidance evidence. It does not establish an
external implementation, signed conformance release or stable-v1 promotion.

## Review and handover

Required agent-panel lenses: API/schema analyst, Provenance analyst, Interoperability analyst, User-workflow analyst, Research-object analyst.

This index is deliberately bounded while the track remains `validating`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
