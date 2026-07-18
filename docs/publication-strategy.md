# Publication and Citation Strategy

## Citable units

Each layer is independently useful and citable:

1. Standards/profile specification release.
2. Reusable provenance/methods software package.
3. NZ spatial source registry and connector catalogue.
4. Dataset snapshots and research objects.
5. Decision-analysis engine releases.
6. Applied study repositories and manuscripts.

## Proposed publication sequence

### Paper A — infrastructure/software

Contribution: a standards-aligned, cross-repository provenance and research-object system that generates publication methods from operational evidence.

Evidence required:

- multiple language/repository adapters;
- conformance and interoperability tests;
- reproducibility demonstration;
- comparison with existing release provenance;
- user-facing methods/citation output.

### Paper B — NZ spatial data descriptor

Contribution: temporally versioned, harmonised council planning spatial layers linked to source plan text and legal-status evidence.

Evidence required:

- national source inventory and coverage metrics;
- reproducible connectors;
- schema/crosswalk and validation;
- rights/attribution inventory;
- spatial/temporal quality analysis;
- limitations in authority and completeness.

### Paper C — supermarket access and health geography

Contribution: reproducible analysis of supermarket access, zoning feasibility, socioeconomic context and area-level health outcomes, followed by constrained location alternatives.

Required distinction:

- descriptive association is not causal effect;
- current placement is not identical to feasible or optimal placement;
- straight-line, network and travel-time access are reported separately;
- model choices, uncertainty and equity trade-offs are explicit.

### Paper D — emergency and hospital facility planning

Contribution: reusable optimisation/simulation framework demonstrated for ambulance posting and/or health-facility configuration.

Required distinction:

- static location-allocation is screened in simulation;
- operational demand data may require controlled access;
- no live operational recommendation is made from public aggregate data alone.

## DOI and identifier policy

- Zenodo or another suitable repository creates version DOI and concept DOI.
- DataCite metadata includes code/dataset relations, SWHIDs and RAiD where available.
- Git tags identify code releases; snapshot IDs identify logical datasets; DOIs identify published research objects.
- `CITATION.cff`, DataCite JSON and repository citation guidance are generated from the same release metadata.

## Authorship and contribution

Record CRediT roles and machine-readable contribution evidence, including connector implementation, data curation, validation, software, methodology, governance and writing. Automated agents/tools may be disclosed in methods and provenance but are not listed as authors.
