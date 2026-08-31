# Resumable publication state

RIOPA separates deterministic publication planning and staging from authenticated
remote publication. `riopa_provenance.publication` provides the state contract
used by GitHub, Hugging Face and Zenodo publisher adapters.

Each target receives an operation key derived from the exact publication-plan
hash and target identity. A publisher must use that key as its idempotency key
where supported, and must reconcile remote state before creating a new release
or deposit.

A successful target receipt records the target ID and operation key, exact plan
hash, immutable remote identifier and revision, observation timestamp, and a
canonical receipt hash. Recording the same receipt again is a no-op. A different
receipt for an already completed target fails closed, preventing a retry from
silently creating or adopting a second deposit. Overall state becomes
`published` only when every planned target has a verified receipt.

Restored journals are validated before any reconciliation, including an empty
receipt batch. The state digest, target operation keys, nested receipt digests,
target statuses and aggregate status must agree. A supplied receipt digest is
checked, never silently replaced. Legacy unhashed receipt inputs remain accepted
and receive their canonical digest on ingestion. Identifiers and revisions are
non-empty opaque strings; the provider adapter must establish their actual
existence and immutability. Journal validation is not provider verification.

Before resuming a specific plan, use `build_publication_resume_plan` to require
that the journal matches that exact plan and all its targets. The deterministic
projection separates recorded receipts from targets requiring provider
reconciliation; neither disposition authorizes a remote write. See
`docs/publication-plan-bound-resume-20260831.md` for the lost-response and
duplicate-deposit boundaries.

Staging requires a fresh directory disjoint from the research object and plan.
Existing output directories and symlinked destinations are rejected without
deleting anything. To retry an interrupted staging operation, retain its evidence
and select a new output directory; remote publication resumability is separate
from replacing a local staging tree.

Rights decisions are inherited from source records through artifact records.
Path and target-specific reviewed decisions may narrow that inherited decision
but cannot widen it. Unknown sources, decisions, targets, or conflicting
receipts fail closed.

This contract does not perform network publication and does not prove that any
GitHub release, Hugging Face revision, Zenodo deposit, or DOI exists.
