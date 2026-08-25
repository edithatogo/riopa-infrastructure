# Facility-location bounded v1 API and migration policy

This policy freezes the repository-owned, bounded reference API for the four
facility-location model families. It is a compatibility aid for the technical
preview; it is not a planning, accessibility, operational, or release
qualification decision.

## Supported model registry

The stable model names are `set-cover`, `maximal-cover`, `p-median`, and
`p-center`. They are implemented by the exhaustive reference solver and accept
the typed `Demand`, `Candidate`, `LocationProblem`, and `LocationSolution`
contracts in `src/riopa_provenance/facility_location.py`.

The registry is intentionally small: callers must not infer additional model
families from the `Model` type, solver labels, or fixture names. A future model
family requires a new versioned contract and explicit evidence; silently
reinterpreting an existing name is prohibited.

## Compatibility and migration rules

- Adding optional fields with documented defaults is backward-compatible.
- Adding a new registry model is additive, but consumers must reject it until
  they explicitly support the new name.
- Renaming a model, changing objective or assignment semantics, changing units,
  or changing required fields is a breaking change and requires a new API
  version plus a migration note.
- A migration must preserve source bytes, identify the old and new contract
  versions, enumerate semantic losses, and include deterministic fixture
  comparisons. Missing provenance, rights, or scale evidence is a fail-closed
  migration outcome, not an inferred success.
- Solver-specific labels, timing observations, and bounded fixture outputs are
  not portable performance or equivalence claims.

## Explicit limits

The v1 reference API is limited to bounded public-data technical-preview
workloads. It does not establish national-scale performance, planning or
accessibility authority, operational deployment, external-solver equivalence,
or promotion to beta, RC, stable-v1, or general availability. Those gates
remain separately evidenced and accountable.
