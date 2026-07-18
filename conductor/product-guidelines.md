# Product Guidelines

## Scientific invariants

1. **Raw evidence is immutable.** Original bytes, service metadata, HTTP metadata and cryptographic digests are retained or referenced in a preservation system.
2. **Every derived artifact declares its parents.** No published result may be disconnected from source versions and transformation runs.
3. **Reproduction is tested, not asserted.** Release candidates undergo clean-room rebuild or equivalent deterministic verification where technically possible.
4. **Uncertainty is data.** Missingness, ambiguity, positional error, classification confidence and model uncertainty are preserved rather than rounded away.
5. **A methods sentence is a view over evidence.** Human-readable methods are generated from machine-readable provenance, not maintained as an independent narrative.

## Architectural guidelines

- Use stable logical identifiers independent of file paths and storage backends.
- Maintain separate code, schema, dataset-snapshot and publication versions.
- Prefer append-only events and immutable snapshots; publish corrected successors rather than silently rewriting history.
- Treat graphs, indexes and databases as projections over canonical snapshots.
- Require artifact-level lineage; require partition/layer-level lineage for spatial data; add feature/row lineage only when it is reliable and useful.
- Expose standards-compatible exports while keeping the internal profile intentionally small.
- Add domain adapters rather than expanding the core with source-specific fields.

## Rights and governance

- Record source licence, attribution, access conditions, redistribution status and any uncertainty at capture time.
- Do not infer open redistribution from public accessibility.
- Apply Māori data sovereignty principles and governance review where data is for, from or about Māori, including derived classifications and geographic aggregations.
- Apply privacy-by-design and disclosure controls to health and social outcomes.
- Keep legally operative plan text, explanatory material and derived machine interpretations distinct.

## Decision-analysis guidelines

- Separate feasibility constraints, objectives, weights, uncertainty assumptions and stakeholder value judgements.
- Report Pareto alternatives where objectives conflict; do not collapse all trade-offs into one score by default.
- Use MCDA for explicit deliberative preferences, not as a substitute for coverage, location-allocation, capacity or simulation models.
- For emergency services, validate location models in discrete-event or agent-based simulation before operational recommendation.
- Report subgroup and geographic equity effects, not only population averages.

## Contribution guideline

A module is successful when another repository can consume it through a documented contract without copying its internals.
