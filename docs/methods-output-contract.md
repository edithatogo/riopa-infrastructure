# Methods and Supplementary Evidence Contract

## Objective

A user should be able to write a concise methods statement by citing a released research object, while reviewers can inspect a complete, machine-verifiable supplement.

## One-sentence output

The generator emits a statement of the form:

> We used RIOPA dataset snapshot `<snapshot-id>` (version `<version>`, DOI `<doi>`), assembled from `<source count>` sources and `<artifact count>` artifact records, transformed with code `<commit/SWHID>`, and released with a hash-linked event stream, rights review, quality evidence, canonical manifest hash and machine-readable methods metadata.

It never invents a DOI, date range, source count, legal status, licence or reproducibility claim.

## Human-readable methods sections

`methods.md` contains:

1. Citable methods statement and study scope.
2. Source discovery, inclusion, exclusion and missing-data handling.
3. Acquisition and archival capture.
4. Harmonisation and exact transformation invocations.
5. Spatial reference systems, geometry and temporal/legal-status handling.
6. Artifacts, materialisations and declared losses.
7. Provenance stream, hashes and snapshot integrity.
8. Quality assurance, results and waivers.
9. Rights, ethics, privacy and Māori data governance.
10. Software/hardware environment, stochasticity and reproducibility.
11. AI-assistance declaration, protocol deviations and limitations.
12. Data/code availability and citation.

## Machine-readable supplement

| File | Purpose |
|---|---|
| `snapshot-manifest.json` | exact release composition and canonical digest |
| `methods-facts.json` | structured methods facts, deviations and limitations |
| `provenance-event*.json` | operational event stream with hash-chain integrity |
| `transformation-run*.json` | code, invocation, parameters, environment and determinism |
| `quality-report.json` | metric-level results, evidence and waivers |
| `rights-inventory.json` | licences, attribution, governance review and publication decision |
| `artifact-*.json` | content identity, availability and verification state |
| `materialization*.json` | representation, fidelity losses and reproducibility class |
| `ro-crate-metadata.json` | RO-Crate 1.3 research-object graph |
| `bundle-manifest.json` | package file inventory and hashes |
| `checksums.sha256` | package integrity check |
| future `datacite.json` / `dcat.jsonld` | DOI and catalogue projections |
| future `sbom.cdx.json` / `attestations/*` | software components and signed release evidence |

## Narrative provenance

Generated prose is a projection of the manifest and its referenced records. A change in exact facts changes the generated text, the affected event or artifact records, and ultimately the snapshot digest.

## Manual manuscript text

Authors may add interpretation, rationale and study-specific detail. They should not manually restate exact versions, hashes or counts when those can be injected from the research object.

## Validation

The generator reports missing evidence explicitly. The release validator fails on broken reference closure, incorrect hashes, undeclared entities, source/right mismatches and inconsistent snapshot subjects. A stable release profile will additionally reject synthetic placeholders and unresolved release-critical governance decisions.
