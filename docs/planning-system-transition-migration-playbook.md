# Planning-system transition migration playbook

Transition records are append-only. A rename, merger, split, replacement or
partial continuity claim creates a new record and never rewrites the
predecessor. Each record carries separate `valid_time` and `recorded_time`
windows, an explicit planning state, scope where continuity is partial, and
version-addressed evidence.

Analyses must select one perspective explicitly:

- `valid_time`: when the transition was legally or operationally effective;
- `recorded_time`: when the archive recorded the evidence;
- `as_known_at`: the recorded-time view at a historical cutoff.

Unknown dates, unsupported states, missing evidence, reversed windows and
unscoped partial continuity fail closed. A new planning-system reform is
migrated by adding successor records, validating the transition schema and
preserving the prior fixture and evidence digest.

This contract describes data continuity and does not provide legal advice or
assert that two instruments are legally equivalent.
