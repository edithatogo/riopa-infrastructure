# Source-rights archive and publication decisions

This is the sole repository owner's permissive-by-default decision for source
preservation and public reuse. It separates copyright permission from source
authority, completeness, freshness, privacy, safety and legal effect. The
machine-readable record is
[`source-rights-publication-decision-matrix-20260829.json`](source-rights-publication-decision-matrix-20260829.json).

## Decision tiers

| Tier | Maximum lawful disposition | Trade-off and contingency |
|---|---|---|
| A | Public payload, metadata, receipts and permitted derivatives. | Maximises reproducibility and preservation. Preserve the exact licence, attribution, item/version and digest; an item-specific exception overrides a publisher-wide licence. |
| B | Public metadata, URLs, terms snapshots, receipts and digests now; payload after exact-item qualification. | Preserves discovery and auditability without licence laundering. Promote to A as soon as the exact licence is bound; use C/D/E if narrower terms or risks emerge. |
| C | Private payload only when acquisition and retention are permitted; public non-reconstructive evidence. | Improves recoverability but creates access control and takedown obligations. Delete or narrow access if terms require it. |
| D | Public discovery record only; do not acquire payload. | Least reproducible, but appropriate where acquisition or retention is prohibited or unclear. Revisit on new terms or permission. |
| E | Public metadata or safe aggregate only. | Applies where privacy, safety or operational sensitivity warrants a narrower release even if copyright permits reuse. Reassess against a documented risk review. |

The default for uncertainty is B, not silence: public facts about a source,
public URLs, licence-gap records, terms snapshots and non-reconstructive hashes
should remain public unless their own terms or sensitivity require otherwise.
Fair dealing is not the basis for routine bulk public payload publication.

## Missing or incomplete licence decisions

| Group | Options | Recommendation and rationale | Contingency |
|---|---|---|---|
| Churton Park Village Supermarket | A under the exact WCC ArcGIS item's CC BY 3.0 NZ notice; B only if a successor item loses that binding; D if later terms prohibit capture. | **A now.** Archive and publish the exact layer, licence receipt and derivatives with WCC attribution. The data.govt.nz record omitted the licence, but its exact linked ArcGIS item supplies it. | Quarantine affected components if the item terms change or third-party content is identified. |
| NZ ambulance prototype | A for exact ArcGIS item `e5b22c07d197417495c8012e945c41da`, which expressly grants CC BY 4.0 sharing and adaptation; B-D for other provider candidates; E for documented sensitivity. | **A for the prototype.** Archive and publish it with attribution and the original mixed-source, accuracy and non-ownership caveats. Copyright permission does not make it authoritative. | Quarantine affected features if provenance or licensor authority is successfully challenged; use E if a safety review identifies sensitive operational detail. |
| Health NZ, Hato Hone St John and Wellington Free Ambulance candidates | A under explicit open dataset terms; B for public discovery and terms evidence; C/D for restricted content; E for sensitive operations. | **B now.** Public websites support discovery, not bulk dataset rights or operational authority. | A later permission can open payloads without changing the non-authority claims; safety can still require E. |
| LINZ catalogue generally | A per exact openly licensed item; B for catalogue/terms records; C/D/E for personal, DVR, owner-name or specially licensed content. | **B at catalogue level, A item by item.** LINZ is not uniformly licensed, so this maximises public metadata while preventing restricted classes from inheriting CC BY. | Exact licence receipts promote eligible items automatically; special terms always override. |
| Hamilton and Marlborough food-register packets | A if preserved receipts expressly permit payload redistribution; B for public records and bounded assertions; C if retention-only. | **B pending explicit receipt evaluation.** Existing source-specific terms evidence is useful but the current record does not state a payload-publication conclusion. | Audit the archived receipt once; promote to A or quarantine payload while retaining public evidence. |

## Existing licence decisions

| Group | Existing basis | Recommendation and trade-off | Contingency |
|---|---|---|---|
| Stats NZ | Publisher-produced material is CC BY 4.0 unless specifically stated otherwise. | **A.** Publicly archive exact payloads and derivatives with the prescribed written attribution. Do not reproduce logos and do not imply official-statistic status. | Any item-specific statement overrides the general licence. |
| Ministry for the Environment | Website-produced copyright material is generally CC BY 4.0. | **A.** Archive publication bytes and derivatives publicly. Exclude logos, imagery, design elements and identified third-party content. | Split mixed works so open components remain A and exceptions use B-D. |
| Ministry of Health certified-public-hospital CSV | Item-level CC BY 4.0 decision is recorded. | **A.** Archive the exact CSV and permitted derivatives publicly; certification is not completeness, capacity or operational suitability. | Personal/confidential or third-party additions use E or the narrower exact terms. |
| OpenStreetMap | ODbL 1.0. | **A.** Publicly archive bounded extracts with contributor attribution and applicable share-alike notices. The compliance overhead is worth the preservation benefit. | Track whether an output is a database, derivative database or produced work; exclude incompatible mirror additions. |
| Greater Wellington GIS | Official site says all data is CC BY 4.0 unless specifically stated otherwise. | **A after checking the item for an exception.** This replaces the earlier blanket demand for written permission; copyright permission does not establish national or operational authority. | A specific layer notice overrides the general term and may downgrade it. |
| Wellington City GIS | GIS metadata identifies CC BY 3.0 NZ. | **A where bound to the exact layer.** Archive the 2024 District Plan layer publicly with attribution and no legal-status inference. | Unbound catalogue entries remain B until the same licence is proven applicable. |
| Rangitīkei public facilities | CC BY 4.0 and a public Zenodo packet are recorded. | **A.** Keep the bounded three-point packet public with attribution and its strong non-authority/non-operational statement. | Withdraw or supersede if exact source terms change; preserve the decision trail. |
| LINZ primary-parcels metadata | Exact CC BY 4.0 licence endpoint is recorded for metadata-only capture. | **A for the captured metadata.** Public geometry requires its own item/version receipt; owner-name, personal and restricted products do not inherit this decision. | Promote each exact geometry payload independently or keep it B/C/D/E. |

## Attribution and public-repository controls

Public repositories must keep the source name, exact item/version, access date,
payload digest, licence identifier and URL, required attribution wording,
modification notice, exclusions, and non-claims beside the payload. ODbL
database outputs must retain attribution and applicable share-alike treatment.
CC licences do not cover logos or imply endorsement. A rights change triggers
quarantine and a new decision; it does not erase the historical decision
record unless retaining that record is itself prohibited.

These recommendations are rights dispositions, not legal advice. They allow
more public archiving while retaining source-specific exceptions and factual
limits on authority, safety and completeness.
