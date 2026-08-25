# Bounded facility-location input adapter

`apply_bounded_reference_inputs` applies an archived, versioned
`AccessibilityMatrix` and an explicit candidate-feasibility mapping to a
`LocationProblem`. Reachable matrix observations become travel pairs; a
declared impedance threshold may censor pairs; candidates marked infeasible are
removed. The existing solver and verifier then operate on the transformed
problem.

This is a repository-owned reference adapter for bounded technical-preview
fixtures. It does not infer roads, timetables, legal status, capacity,
accessibility, or operational availability. It is not a national-scale,
planning-authority, or release-promotion claim. Missing or censored pairs stay
missing and therefore fail closed in models that require coverage.
