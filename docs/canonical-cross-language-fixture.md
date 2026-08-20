# Canonical cross-language fixture

`fixtures/canonical-crosswalk-golden.json` is the frozen semantic fixture for
cross-language implementations. Python verifies its JSON Schema and RFC 8785
canonical JSON digest. Other runtimes must independently reproduce the same
digest before this can count as a round-trip or compatibility claim; no such
external runtime evidence is asserted by this repository fixture.
