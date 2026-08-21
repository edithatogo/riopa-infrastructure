# Schema-drift runbook

Trigger this runbook when a source schema, field type, endpoint contract, or
profile version changes.

1. Preserve the source-faithful failed capture and its digest.
2. Compare the observed schema with the pinned contract and classify additive,
   corrective, or breaking change.
3. Add positive, negative, and migration fixtures before changing a normative
   schema or adapter.
4. Rebuild only from the new digest-bound input and record compatibility impact.

Stop conditions: ambiguous mapping, semantic loss, or missing migration and
rollback evidence.
