# Stable v1 requirements

## Programme and compatibility

- **R-001** Every component has an authoritative responsibility, owner repository and version axis.
- **R-002** Software, schemas, ontology, datasets, models and research objects are independently versioned and explicitly related.
- **R-003** Stable 1.x interfaces follow the published compatibility and deprecation policy.
- **R-004** Every breaking pre-1.0 change has migration fixtures and an explicit version decision.
- **R-005** Every v1-critical track has machine-readable status, dependencies, risk, maturity target and release evidence.

## Capture, provenance and lineage

- **R-010** Every captured artifact records stable identity, source locator, retrieval time, method, relevant request/response evidence, media type, byte size and cryptographic digest.
- **R-011** Raw bytes are preserved before a successful capture event is emitted.
- **R-012** Retry, resume, pagination, idempotency, stream/partition and partial-failure semantics are explicit.
- **R-013** Every transformation records code identity, environment, lock/container digest, command, parameters, inputs, outputs and timing.
- **R-014** Manual and AI-assisted activities record tool/model identity, evidence, review and decision.
- **R-015** Every output is traceable to source evidence at declared dataset, partition, feature or row granularity.
- **R-016** Unsupported lineage precision is rejected rather than inferred.
- **R-017** Provenance projects to PROV/OpenLineage/attestation forms without making those projections authoritative.
- **R-018** Canonical hashing uses a named cross-language algorithm and golden fixtures.

## Domain model and ontology

- **R-020** Authorities, services, layers, plans, provisions, features, facilities, assertions, mappings, reviews and analytical runs have stable schemas.
- **R-021** Changeable entities distinguish identity from version identity.
- **R-022** Original labels, classifications, coordinates, geometries and source assertions are retained.
- **R-023** Crosswalks record method, evidence, confidence, reviewer and valid time.
- **R-024** Unknown, disputed, inapplicable and missing values remain distinguishable.
- **R-025** A versioned SKOS/JSON-LD ontology and SHACL shapes validate canonical semantics.

## Spatial and temporal data

- **R-030** Raw, canonical and materialised layers are separate.
- **R-031** Canonical vectors are publishable as GeoParquet and queryable in DuckDB Spatial.
- **R-032** Spatial features carry source identity, source-feature identity where available, geometry digest and bitemporal fields.
- **R-033** Original and repaired geometry are separately identifiable and repair effects are measured.
- **R-034** Published, retrieved, observed, valid, operative and superseded times are not conflated.
- **R-035** Spatial features may link to plan/provision versions without claiming legal authority.
- **R-036** Proposed, appealed, partly operative, transitional and superseded planning states are representable.
- **R-037** Boundary concordance, denominator versions, MAUP and temporal reconstruction uncertainty are available for area analysis.

## Facilities, accessibility and analytics

- **R-040** Facility registries preserve immutable source assertions separately from reconciled identities.
- **R-041** Facility matches record evidence, method/model, confidence, reviewer and temporal state.
- **R-042** Travel matrices identify network/timetable, mode, engine/version, profile, parameters, time and exclusions.
- **R-043** Accessibility formulas, capacity semantics and missing/unreachable handling are explicit.
- **R-044** Facility-location problems and solutions have language-neutral contracts.
- **R-045** Set cover, maximal cover, p-median, p-center and capacity models share a verified core interface.
- **R-046** Equity, robustness, competition, multi-period and MCDA choices are explicit and inspectable.
- **R-047** Solutions record solver, status, bound, gap, tolerance, seed and independent feasibility evidence.
- **R-048** Stochastic simulation records inputs, seeds, replications, warm-up, calibration, validation and uncertainty.
- **R-049** Static models are not used where queueing/dispatch/congestion invalidates their assumptions without simulation or explicit limitation.

## Research methods and health outcomes

- **R-050** Analyses declare descriptive, predictive, causal or prescriptive intent.
- **R-051** Causal analyses declare DAG, estimand, assumptions and sensitivity/falsification plan.
- **R-052** Exposure, outcome, population, denominator, geography and time versions are fixed in the analysis manifest.
- **R-053** Spatial confounding, autocorrelation, MAUP, ecological inference and measurement error are assessed where relevant.
- **R-054** Sensitive/small-cell outputs are controlled by privacy and governance policy.
- **R-055** Applied emergency/hospital reference models carry a conspicuous non-operational limitation.

## Publication and reproducibility

- **R-060** Every referenced bundle record is schema validated independent of filename.
- **R-061** Every local reference is path safe and every bundled payload has verified size/digest.
- **R-062** Research objects include methods facts, concise/full methods, citation, quality, rights, provenance, software/environment, SBOM, attestations and preservation metadata.
- **R-063** Package manifests and checksums use a documented non-circular integrity design.
- **R-064** External conformance is claimed only when the representation is emitted and validated.
- **R-065** Stable releases have immutable version identity, DOI-ready metadata and correction/supersession relationships.
- **R-066** At least one external party reproduces a real-data release and an applied benchmark before v1 GA.
- **R-067** Every local stable-v1 evidence reference has a verified digest; every external stable-v1 evidence reference has a digest or recognised content-addressed persistent identifier.

## Governance, rights and safety

- **R-070** Public visibility is never treated as redistribution permission.
- **R-071** Rights, privacy, ethics, applicable cultural or community review, legal-status and safety decisions travel with sources and releases.
- **R-072** Publication fails closed when required governance decisions are unresolved.
- **R-073** Controlled and public data pathways are technically separated and tested.
- **R-074** Corrections and withdrawals stop inappropriate distribution while preserving explanatory provenance.
- **R-075** Derived products receive benefit/harm and governance review, not only their source datasets.

## Security and operations

- **R-080** Release CI uses least privilege, protected environments and immutable action/dependency identity.
- **R-081** Stable artifacts carry signed checksums, SBOMs and provenance attestations.
- **R-082** No unmitigated critical or high vulnerability remains at v1 release.
- **R-083** Scheduled jobs are observable, idempotent, recoverable and safely quarantined on drift/failure.
- **R-084** Source freshness, capture/release success, quality, fixity, alerts, restore readiness and cost are measured.
- **R-085** Stable releases have independent preservation copies or documented exception.
- **R-086** Restore, disaster recovery, correction, withdrawal and compromised-release exercises pass.
- **R-087** Beta SLO evidence spans at least ninety consecutive days before release candidate.

## Usability, adoption and support

- **R-090** Greenfield and brownfield repository setup is documented, testable and non-destructive.
- **R-091** Generated configuration has clear ownership and drift detection.
- **R-092** At least three existing repositories dual-emit the profile, two package research objects and one reaches independent reproduction.
- **R-093** At least two external users complete distinct stable workflows from documentation.
- **R-094** V1 has named maintainers, support/security channels, correction process and a twelve-month critical-fix window.
