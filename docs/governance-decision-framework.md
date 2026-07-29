# Rights, privacy and Māori data sovereignty decision framework

This framework records a decision about a source, artifact, transformation,
model or release. It does not certify tikanga, consent, legal compliance or
Māori approval. Those determinations remain with appropriately engaged people
and accountable institutions.

## Data classes

| Class | Default pathway | Examples / controls |
|---|---|---|
| `public` | public only after rights and governance review | open source metadata, non-sensitive derived summaries |
| `restricted` | controlled or metadata-only | licence, registration or access-condition restrictions |
| `sensitive` | controlled; minimise and aggregate | health, personal, household or culturally sensitive geography |
| `controlled` | approved compute and named users only | contractual, statutory or community-controlled access |
| `prohibited` | capture/transformation/publication blocked | explicit prohibition, unlawful target or unresolvable harm |

## Trigger matrix

| Trigger | Minimum evidence | Independent action that may be blocked |
|---|---|---|
| licence or attribution uncertainty | licence/source record and legal-status note | redistribution and publication |
| public visibility without reuse permission | source terms and access evidence | capture, redistribution and inference |
| personal or health information | privacy/ethics review and disclosure assessment | linkage, analysis and release |
| Māori data or Māori-relevant derived classification | appropriately engaged governance review and benefit/harm record | capture, transformation, linkage and release |
| culturally sensitive place or knowledge | sensitivity assessment and access controls | granularity, mapping and publication |
| safety or operational risk | threat/safety assessment and mitigation | analysis, recommendation and release |
| correction, withdrawal or supersession request | authenticated request, scope and successor evidence | distribution and downstream reuse |

## Decision outcomes

`allow`, `allow-with-conditions`, `metadata-only`, `controlled-only`,
`withdraw`, `superseded`, `prohibited` and `review-required` are distinct
outcomes. Missing, expired or conflicting evidence yields `review-required`;
it never silently yields `allow`.

Each decision records the reviewer role, evidence references, scope, date,
expiry, conflict-of-interest declaration, rationale, conditions and successor
or withdrawal references where applicable.

## Release separation

Public and controlled outputs use separate manifests, directories and target
credentials. A controlled decision cannot be overridden by a public target
flag. Public visibility of an input does not grant redistribution permission.

## Correction and withdrawal

Withdrawal stops future distribution, records the affected artifact/target
scope and creates a successor or tombstone record without rewriting prior
provenance. Existing copies require a bounded takedown/reconciliation action;
the system preserves the fact and reason for the withdrawal.
