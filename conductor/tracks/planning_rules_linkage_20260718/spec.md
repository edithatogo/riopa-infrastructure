# Track: Council planning spatial-to-rule linkage

Track ID: `planning_rules_linkage_20260718`  
Phase: **NZ Spatial**

## Goal

Link zoning and planning geometries to versioned source plan documents and provisions with transparent evidence and uncertainty.

## Dependencies

- `nz_spatial_archive_mvp_20260718`

## Scope

- Plan/document/provision identity and versioning.
- Publisher identifiers and deterministic links where available.
- Rule-based/model-assisted candidate links with human review.
- National Planning Standards crosswalk and council-specific semantics.
- Legal-status assertions and caveats.

## Out of scope

- Automated legal advice.
- Collapsing plan text and GIS into one supposedly authoritative object.

## Acceptance criteria

- [ ] Every pilot spatial layer links to its source plan/version and captured documents.
- [ ] Provision links state method, evidence, confidence and review status.
- [ ] National zone crosswalk retains local meaning and mapping uncertainty.
- [ ] Evaluation reports precision/recall or reviewed accuracy on a gold sample.
- [ ] Public documentation clearly separates publisher facts, extracted structure and interpretation.

## Risks

- Ambiguous plan structure.
- PDF/OCR errors.
- Appeals/partial operativity and local terminology.
