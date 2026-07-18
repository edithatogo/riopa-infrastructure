# Track: New Zealand spatial source and authority registry

Track ID: `nz_spatial_source_registry_20260718`  
Phase: **NZ Spatial**

## Goal

Create a versioned national inventory of authoritative national sources, councils, plans, GIS/ePlan services, documents, rights and connector health.

## Dependencies

- `provenance_profile_v1_20260718`
- `governance_maori_data_sovereignty_20260718`

## Scope

- Authority and plan registry with historical identity changes.
- Automated discovery of ArcGIS, WFS/Koordinates, ePlan and static sources.
- Service capability, layer schema and terms snapshots.
- National source adapters for LINZ, Stats NZ, MfE and Gazette/DigitalNZ.
- Coverage and connector-health reporting.

## Out of scope

- Assuming every public viewer permits bulk redistribution.
- Canonicalising planning meaning before source evidence is stable.

## Acceptance criteria

- [ ] All current regional and territorial authorities have source-registry records.
- [ ] Each authority has a plan/publication mechanism classification and rights status.
- [ ] At least four heterogeneous councils have reproducible source discovery.
- [ ] National source records and service metadata snapshots are versioned and hashed.
- [ ] Coverage, freshness and unresolved-rights dashboards are generated.

## Risks

- Endpoint anti-automation controls.
- Changing local-government structure.
- Undocumented service URLs and mixed licences.
