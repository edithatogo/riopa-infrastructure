# Simulation v1 bounded reference contract

The v1 technical-preview simulation surface consists of the deterministic
FCFS queue engine, seeded replication and convergence helpers, synthetic
dispatch/coverage adapters, capacity-resilience calculations, and the
caller-supplied calibration and sensitivity workflows already linked in the
simulation track. Their inputs, seeds, result fields, and limitations are
versioned by the existing analysis protocol schema and tests.

Consumers must pin the protocol version and master seed, retain the declared
parameter evidence class, and preserve uncertainty and missingness fields.
Changing event ordering, queue metrics, seed derivation, confidence semantics,
or result units is a breaking contract change requiring a new version and
migration evidence. Additive optional metadata is compatible only when it does
not alter computed results.

This is a bounded synthetic/reference contract. It does not establish real or
clinical calibration, independent implementation equivalence, published
benchmark agreement, dispatch or operational readiness, national-scale
performance, or beta/RC/stable-v1 promotion. Those gates remain open and
fail-closed.
