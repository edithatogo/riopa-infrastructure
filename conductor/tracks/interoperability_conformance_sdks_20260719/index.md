# Evidence index: Interoperability, conformance suites and supported SDKs

- **Track ID:** `interoperability_conformance_sdks_20260719`
- **Status:** `validating`
- **Target release:** `0.6.0`
- **Current maturity:** `M1`
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

## Blocking defects

- None recorded for the bounded WP-008 adapter slice.

## Remaining maturity gates

Implementation evidence is bounded to the recorded conformance slices. Rust,
full-schema, standards-projection, external-client, signed-report, and
release-authority evidence remain open; the track must not be marked complete
or archived until its M2–M6 acceptance evidence is recorded.

## Decisions, exceptions and limitations

- The adapters do not upgrade approximate, extension-only or unmapped fields to
  exact equivalence and do not constitute a full conformance certificate.

## Review and handover

Required agent-panel lenses: API/schema analyst, Provenance analyst, Interoperability analyst, External-user workflow analyst, Research-object analyst.

This index is deliberately non-assertive while the track remains `specified`. Status may advance only through `conductor/workflow.md`; evidence must be immutable or version-addressed, agent-panel qualified where required, and sufficient for the applicable release gates.
