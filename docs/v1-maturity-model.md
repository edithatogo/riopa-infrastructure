# Stable v1 evidence maturity model

RIOPA uses seven evidence levels, **M0–M6**. The normative machine-readable model is `conductor/maturity-model.json`; this document explains its intent.

Maturity is multidimensional. A component can be well tested yet immature in governance, operations, performance, interoperability or scientific interpretation. Stable v1 is therefore evaluated across 12 dimensions: governance, contracts, provenance, security, data, operations, performance, interoperability, publication, usability, analytics and science.

## Levels

### M0 — concept

The problem, intended users, assumptions and initial rights, ethical and safety issues are identified. No implementation or delivery commitment is implied.

### M1 — specified prototype

Scope, non-goals, dependencies, interfaces, acceptance criteria, failure tests and evidence requirements are explicit. A deterministic prototype plan exists, but real integration and operational evidence do not.

### M2 — integrated alpha

Executable software works against representative or real evidence. Positive, negative and failure-path tests pass; rights, security, provenance and migration implications are exercised. Interfaces remain experimental.

### M3 — operational beta

The capability runs repeatedly with monitoring, quarantine, recovery, migration, correction and external-use evidence. Coverage, quality, cost and limitations are measured, but compatibility may still change with notice.

### M4 — hardened beta

The feature set is substantially complete. Security, performance, resilience, preservation, compatibility, scientific-method and orchestrated agent-panel qualification have no unresolved beta blocker. Interfaces are approaching freeze.

### M5 — release candidate

Normative interfaces and conformance fixtures are frozen. No P0, P1, critical security, governance prohibition or release-blocking correctness/reproducibility defect remains. Migration, rollback, restore, external reproduction and candidate soak are underway or complete.

### M6 — stable v1 general availability

Supported 1.x compatibility, deprecation, security and incident policies are in force. Signed and preserved artifacts, persistent citation records, named maintainers, external reproduction, measured service boundaries and post-release verification obligations are active.

## Advancement rules

- Progression is monotonic; regression requires a recorded incident or reclassification decision.
- Every transition requires linked, version-addressed evidence.
- Dependencies must reach the maturity needed by the consuming track.
- M5 and M6 cannot rely solely on self-attestation.
- Expired evidence or waivers block release.
- A track marked complete must have reached its declared target maturity.
- M6 requires all applicable programme dimensions; a strong average cannot conceal a failed security, governance or integrity dimension.

## Anti-patterns

- A large test count does not establish operational maturity.
- A DOI does not establish independent reproducibility.
- A signed build does not establish scientific validity.
- A national source inventory does not establish national data completeness.
- Closing every issue does not establish a compatibility or support contract.
- A successful optimisation run does not establish feasibility, equity or model validity.
