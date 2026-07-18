# Track: Research objects, methods supplements and citation automation

Track ID: `methods_research_objects_20260718`  
Phase: **Core**

## Goal

Generate concise citable methods and publication-grade supplementary evidence from the same machine-readable release facts.

## Dependencies

- `provenance_profile_v1_20260718`

## Scope

- RO-Crate 1.3 projection and workflow-run entities.
- DataCite 4.7, DCAT, Croissant and Frictionless metadata views.
- Methods JSON/Markdown generation and evidence anchors.
- Rights inventory, checksums, SBOM and attestations.
- DOI/release integration and correction relationships.

## Out of scope

- Automated scientific interpretation.
- Inventing missing facts or legal conclusions.

## Acceptance criteria

- [ ] A clean example release contains the mandatory research-object files.
- [ ] Generated methods include exact versions, sources, time ranges, quality status and limitations.
- [ ] Missing required evidence fails closed or is explicitly stated as missing.
- [ ] DataCite and RO-Crate validators pass.
- [ ] A corrected release preserves and links the superseded release.

## Risks

- Narrative drifting from evidence.
- Metadata views disagreeing.
- DOI workflow publishing incomplete artifacts.
