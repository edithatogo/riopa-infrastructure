# Publication journal recovery hardening

Track: `publication_validation_20260718`, issue #129, WP-003.

The pure publication journal now validates restored checkpoints before single
receipt replay and before every batch, including an empty batch. Validation binds
the state hash, plan digest, target operation keys, nested receipt hashes and
aggregate status. Supplied receipt hashes must match; legacy unhashed receipt
inputs still acquire their canonical hash at ingestion. Required receipt values
must be non-empty strings and observation timestamps must include a timezone.

The three-provider tests cover partial progress, deterministic resume, identical
replay, conflicting receipts, corrupted checkpoints, resealed inconsistent state
and recovery from the unchanged original checkpoint. Rejection does not mutate
the supplied journal. Provider identifiers remain opaque: consistency is not
authentication, existence, immutability or accepted remote publication.

Staging now requires a fresh, input-disjoint directory and rejects symlinked paths.
It never deletes an existing output tree. Interrupted staging is retained for
inspection; retry into a fresh directory. Sentinel-based regression tests prohibit
recursive deletion even if the implementation regresses, and verify that source,
plan and unrelated destination bytes remain unchanged.

These fixes improve repository-owned replay safety. Generalized authenticated
multi-provider reconciliation, remote conflict/recovery acceptance, preservation
and exact stable-candidate qualification remain open. No provider operation,
deposit or release was performed by these tests.
