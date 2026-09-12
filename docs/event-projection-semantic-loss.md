# Native event projection retention and semantic loss

This report qualifies the current builders against the repository's native
provenance-event schema. It is a bounded loss assessment of synthetic reference
inputs, not PROV/OpenLineage standards certification, full profile parity or
release approval. Native evidence remains normative.

## Field dispositions

`docs/event-projection-loss-evidence-20260912.json` classifies every top-level
native-event property and binds the schema, builder and qualification tests.
Qualification fails if the schema adds an unclassified field or an asserted
retained value changes in the projected output.

| Native field | OpenLineage projection | Disposition |
|---|---|---|
| event_id | run.runId | Exact value; target-standard run identity semantics unqualified |
| stream_id | run facet streamId and job namespace | Exact value |
| sequence | run facet sequence | Exact value |
| recorded_at | eventTime | Exact value; occurred_at is not retained |
| event_hash | run facet eventHash | Exact digest value; omitted content cannot be recovered from a digest |
| inputs / outputs | Dataset names under namespace riopa | Exact ordered identifier lists; target dataset semantics unqualified |
| status | eventType | Many-to-one: partial and reviewed both become OTHER |
| activity | job.name | Only activity_type retained; activity_id, name, description and extensions omitted |
| All remaining event properties | Absent | Omitted, individually listed in the receipt |

Omitted properties include schema version, event type, occurred time, agents,
parameters, environment, schema/classification/rights/quality references, valid
time, previous-event hash, signature reference and diagnostics. A consumer
cannot reconstruct the native hash preimage, causal chain, rights disposition,
reviewer identity or signature evidence from this projection alone.

PROV output currently reads artifact and transformation records; it does not
read native event records. Changing native status, agents, rights or activity
identity leaves that PROV output unchanged. This is a native-event loss finding;
artifact and transformation field mappings need their own qualification.
The separate RO-Crate Action projection is outside this assessment.

The collision test changes status, agents, rights and activity identity and
recomputes the native hash. OpenLineage changes only its hash facet, while PROV
is unchanged. All six native status mappings and retained-value drift are
exercised. No fixture rights change is a real rights decision.

## Reproduction and next gates

```bash
uv run python -m scripts.build_event_projection_loss_evidence --output /tmp/event-loss.json
```

Compare with the dated receipt. Keep original events in the research object;
do not use interoperability projections as replacement archival evidence.

The core platform maintainer can next qualify artifact/transformation mappings
and event validation across runtimes, using field/loss reports and adversarial
fixtures. Candidate qualification then needs a digest-bound inventory and the
required advisory lenses, with dependency gates still evaluated separately.
These repository actions are authorized; they confer no publication, signing
or accountable release authority. The operations maintainer still needs an
actual successful post-fix scheduled campaign receipt; no new dispatch is implied.
Foundation and provenance remain validating at M2.

Validation: all 10 focused qualification tests passed; the full suite passed
2,014 tests with one skipped and 90.71% branch-aware coverage. Quality, packaging
and roadmap checks passed. Advisory review found no misclassification within
the stated scope. The receipt reproduces from the current builders.
