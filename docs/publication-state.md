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

Rights decisions are inherited from source records through artifact records.
Path and target-specific reviewed decisions may narrow that inherited decision
but cannot widen it. Unknown sources, decisions, targets, or conflicting
receipts fail closed.

This contract does not perform network publication and does not prove that any
GitHub release, Hugging Face revision, Zenodo deposit, or DOI exists.
