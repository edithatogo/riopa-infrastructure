# Risk Register

| Risk | Consequence | Control | Trigger/owner |
|---|---|---|---|
| Council endpoint/viewer changes | broken capture and coverage gaps | capability snapshots, health checks, connector adapters, archived raw evidence | connector health track |
| Publicly viewable but restricted data | unlawful redistribution/licence laundering | **Closed for current public-datasets-only scope**; no restricted/non-public payload acquisition or publication is authorised. Re-open on scope expansion. | rights review / scope change |
| GIS layer differs from statutory plan | incorrect legal interpretation | preserve source disclaimer; link, do not merge, spatial and textual authority; legal-status evidence | planning linkage track |
| Retrieval date mistaken for operative date | invalid temporal analysis | bitemporal fields and sourced assertions; null rather than inference | schema/QA |
| Inconsistent zone semantics | false national comparisons | National Planning Standards crosswalk plus council-specific meaning and mapping confidence | ontology/crosswalk review |
| Geometry repair alters meaning | area/topology bias | retain original geometry, derived repair, metrics and algorithm version | spatial QA |
| Facility duplicate/misclassification | biased access estimates | probabilistic match evidence, manual review sample and sensitivity analysis | facility registry |
| Health ecological inference | overclaiming individual/causal effects | preregistered estimand, explicit ecological limitations, sensitivity analyses | applied study |
| Māori data harms or loss of governance | inequitable or inappropriate reuse | Māori data sovereignty assessment, governance involvement, rights/benefit review | governance track |
| Provenance volume explodes | unusable storage/queries | tiered granularity and partition lineage; feature lineage only when justified | architecture review |
| Knowledge graph becomes critical dependency | operational fragility | event log and manifests remain authoritative; graph rebuild tested | core track |
| Non-deterministic ML/optimisation | irreproducible results | seeds, solver/model versions, tolerances, input hashes and solution verification | analytics track |
| Facility model optimises averages only | worsened inequity | p-center/equity constraints, subgroup reporting and Pareto alternatives | optimisation review |
| Ambulance static model used operationally | unsafe recommendations | simulation validation and operational-data boundary | emergency pilot |
| Standards churn | broken interoperability | pinned profile versions, adapters and conformance fixtures | release review |
| New Zealand planning/local-government reform | changing authority/source structures | versioned authority registry, bitemporal source identity and migration track | programme review |
