# Remaining release-gate evidence matrix

This matrix records the evidence still required after the deterministic WP-010
successor deposit. The internal subagent panel may prepare, reproduce and audit
evidence, but it is not a substitute for an accountable external operator,
source custodian, or release authority.

For the current public-datasets-only bounded technical preview, the
programme-owner-authorised panel report may close the pilot validation gate.
The beta, release-candidate and stable-v1 gates remain governed by the stricter
requirements below.

| Gate | Required closing evidence | Panel contribution | What the panel cannot substitute for | Owner / contingency |
| --- | --- | --- | --- | --- |
| External reproduction (issue #149) | A clean-room operator outside the implementation run completes the documented workflow from the frozen revision, records environment and deviations, and publishes an adverse-findings or no-findings report with exact hashes. Required for beta, release candidate and stable v1. | Rebuild the packet twice, run the scripted workflow, perform an adversarial review, and prepare a ready-to-run operator bundle and report template. | A subagent run is not an independent person/operator reproduction and cannot attest to usability for an external operator. | Release owner solicits an external operator and records the response. If unavailable, keep the project at regional technical-preview status and mark the gate open. |
| National ambulance source authority | Written confirmation from the responsible custodian(s) of dataset authority, geographic coverage, version/freshness, licence and redistribution rights, sensitive-location restrictions, correction route, and permitted claims; preserve the exact authorised payload and hash. | Search official public catalogues, build a candidate rights/provenance matrix, and draft custodian requests without activating acquisition or redistribution. | Panel findings cannot confer authority, licence permission, completeness, or a correction commitment. Public metadata alone cannot support national-completeness claims. | Data/source steward requests confirmation from Health NZ/Te Whatu Ora and provider custodians. If no response, retain only the bounded regional public-data pilot and state the limitation. |
| Release authority | Named accountable authority signs a tier-specific decision covering scope, exclusions, safety posture, evidence links, expiry/review date, and rollback/withdrawal conditions. | Assemble the release-evidence index, check traceability and identify unresolved risks or stale artefacts. | A panel recommendation is not an approval, accountability assignment, or authorization to represent the system as operational. | Release authority (to be nominated) decides beta/RC/v1. If absent, publish no higher tier and retain the technical-preview label. |
| Ontology and conformance | Versioned ontology/semantic contract, fixture-backed conformance results, mapping assumptions, and review of all equations, heuristics and parameters against cited sources. | Cross-check mappings, run conformance fixtures and adversarially test unknown/ambiguous values; report gaps and provenance. | Panel agreement cannot establish domain ownership or validate an ontology for operational use where a custodian or accountable domain authority is required. | Technical lead owns the contract; domain authority confirms semantics. If confirmation is unavailable, limit claims to the documented pilot vocabulary and fail closed on unknowns. |

## Panel operating protocol

The orchestrator should collect separate signed (content-hashed) outputs from a
reproduction agent, an adversarial reviewer and an evidence/rights auditor.
Each output must identify the source revision, packet digest, tools and
limitations. The orchestrator then publishes one panel report that links each
finding to the gate above and preserves dissent; it must not change a gate's
status from open to closed without the required external or accountable
evidence.

## Review and expiry

Re-run the matrix when scope, source rights, source status or safety changes and
at the bounded-pilot review date (2026-08-31, or sooner on change). A stale
manifest, changed packet digest, or withdrawn source re-opens the affected gate
until the successor evidence is recorded.
