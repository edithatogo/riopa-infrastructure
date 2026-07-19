# Compatibility, deprecation and support policy

## Before 1.0

Pre-1.0 interfaces may change, but every breaking change requires a migration note, fixture update and compatibility decision.

## Stable 1.x

- Semantic Versioning applies to the public software API and CLI contract.
- Normative schemas and ontology are independently versioned but follow the same non-breaking 1.x principle.
- Required fields, identifier meaning and normative semantics are not removed or narrowed within 1.x.
- Additive optional fields require fixtures and consumer-tolerance tests.
- A deprecation remains for at least two minor releases or six months, whichever is longer.
- Security and critical correctness fixes are provided for at least twelve months after 1.0 general availability.
- Data snapshots and research objects remain immutable; corrections create successor releases.

A compatibility exception requires public scope, rationale, migration, approver and expiry.
