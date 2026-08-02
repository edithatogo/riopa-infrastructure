# Panel qualification plan — publication, methods, interoperability, security and v1 hardening

This plan records the repository-owned path for the five release-critical tracks
assigned to the evidence batch. It uses a three-agent panel in place of a human
reviewer for the bounded public-datasets-only preview. It does not assert that
stable v1 is ready.

## Panel composition

Each run is independent and content-bound:

1. **Reproducer** rebuilds the research object, publication plan and conformance
   corpus from the frozen revision.
2. **Adversarial reviewer** exercises malformed inputs, rights narrowing,
   provenance breaks, dependency tampering and rollback paths.
3. **Evidence auditor** verifies hashes, SBOM/attestation references, methods
   facts, publication receipts and traceability to the release gate.

The orchestrator stores each report, SHA-256 digest, environment, commands,
findings and dissent. A disagreement or digest mismatch fails the panel gate.

## Track exit criteria and current disposition

The machine-readable template [`panel-qualification-report-templates-20260801.json`](panel-qualification-report-templates-20260801.json)
covers every currently open Conductor track. Every entry is explicitly `pending`
with a null disposition until all three panel reports and content-bound evidence
are attached. The template links each track to the release-authority decision
record; it is an evidence index, not a qualification result. Run
`uv run python scripts/validate_panel_reports.py` with report paths for an
executed panel, and use `validate_template_manifest` in CI to detect drift.
The current five-track batch is separately indexed in
[`panel-qualification-batch-20260802.json`](panel-qualification-batch-20260802.json);
it is a pending template with no revision, bundle digest or reports until the
panel executes.
Executed reports must include a stable `report_id`, `track_id`, bounded `scope`,
UTC `evaluated_at` timestamp, `findings` and `evidence_refs` arrays, the exact
40-character source revision and a lowercase 64-character bundle SHA-256. These
fields bind a report to a reproducible run; their presence does not make a
report independent or close any external gate.

| Track | Panel evidence required | Current disposition |
| --- | --- | --- |
| `publication_validation_20260718` | rights-aware plan, deterministic staging, receipt idempotence, preservation DOI | Repository controls present; panel execution and publication receipts remain to be attached. |
| `methods_research_objects_20260718` | RO-Crate closure, generated methods facts, citation and checksum verification | Contracts and generators present; real release object and citation projection remain open. |
| `interoperability_conformance_sdks_20260719` | language-neutral corpus, schema/version checks, two independent runners | Corpus validation is implemented; cross-language runner evidence remains open. |
| `security_supply_chain_20260719` | dependency audit, SBOM, provenance attestation, secret and tamper checks | CI controls exist; signed release attestations and remediation evidence remain open. |
| `v1_release_hardening_20260719` | all upstream gates, rollback/restore, soak, support and release decision | Blocked until upstream evidence and time-based qualification complete. |

## Options and contingencies

* **Recommended:** qualify the bounded preview with the panel and preserve the
  higher-tier gates as open until their evidence exists.
* **Fallback:** if a panel member cannot run, record an incomplete panel and
  retain preview status; never infer a pass from missing output.
* **Reproducibility failure:** preserve both bundles, open a remediation issue,
  and repeat from a new frozen revision.
* **Security or integrity failure:** fail closed, quarantine the candidate and
  require a new attestation/SBOM before any publication.
* **Missing soak or restore evidence:** defer beta/RC/stable promotion; a local
  green test run is not a waiver.

## Non-waivable boundaries

This panel plan does not authorise clinical, dispatch, national-completeness or
operational claims. It does not convert a technical-preview report into a
stable-v1 release decision. Your public-source authority approval applies to
the declared public-datasets-only scope; a future scope expansion creates a
new evidence packet and reopens the affected gates.
