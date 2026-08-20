# Public ambulance and facility source rights matrix

**Status:** metadata-only discovery (2026-08-01)

This matrix records candidate public sources for the bounded regional pilot. It
does not assert authority, completeness, permission to download, or permission
to redistribute. No source payload was acquired for this inventory.

| Candidate / public URL | Apparent coverage and role | Licence / authority status | Intake disposition |
|---|---|---|---|
| [NZ Ambulance Station Locations prototype](https://www.arcgis.com/home/item.html?id=e5b22c07d197417495c8012e945c41da) | New Zealand station-location prototype; useful for discovery and regional cross-checks only. | Item is labelled CC-BY, but the record identifies it as a prototype and does not establish provider ownership, national completeness, update cadence, or endorsement of derived claims. | Metadata may be cited. Do not acquire or redistribute features until the publisher/custodian confirms licence scope, provenance, freshness and corrections route. |
| [Greater Wellington ambulance-stations layer](https://mapping.gw.govt.nz/arcgis/rest/services/GW/Emergencies_P/MapServer/1) | Greater Wellington regional layer; candidate bounded regional reference. | Official regional endpoint is visible, but licence, attribution, redistribution, update and withdrawal terms require written confirmation. Regional coverage must not be treated as national coverage. | Record endpoint metadata and layer revision only. Request written terms before capture, transformation or publication. |
| Health New Zealand / Te Whatu Ora | Potential national health-system custodian route; no authoritative open station register was established by this inventory. | Authority, dataset identity, access, privacy/safety restrictions and redistribution terms are unconfirmed. | Send the questions in [`source-authority-request-packet.md`](source-authority-request-packet.md); a non-response is `review-required`, not permission. |
| Hato Hone St John and Wellington Free Ambulance | Provider custodian routes for operational ambulance locations and service boundaries. | Provider ownership, authoritative status, publication rights, sensitive-location constraints and correction process are unconfirmed. | Seek written custodian confirmation before acquisition or operational claims. |
| [Stats NZ meshblocks](https://www.stats.govt.nz/geographies/meshblock/) | Geographic denominators and aggregation framework; not an ambulance-source authority. | Stats NZ terms, version and permitted derived-use wording must be checked for the exact release used. | Use only as a denominator/supporting geography after recording release/version and terms; never infer station authority. |
| [LINZ data services](https://www.linz.govt.nz/data) | Supporting facilities/geography layers; not an ambulance-source authority. | LINZ licence and layer-specific conditions vary; exact product, version and attribution must be recorded. | Metadata-only until product terms and source suitability are verified. |

## Fail-closed intake sequence

1. Capture the public landing URL, provider, dataset/layer identifier, visible
   version or update timestamp, access date, coverage and exclusions. Preserve
   this metadata snapshot and its SHA-256; do not fetch restricted payloads.
2. Obtain a written custodian/authority response covering authoritative status,
   geography and time coverage, update/correction cadence, licence and
   attribution, redistribution and derivative-use rights, privacy/sensitive
   location restrictions, retention/takedown, and the permitted claims.
3. Record the response, exact terms URL, named role, decision date and expiry in
   the source-acquisition approval template. Treat missing, ambiguous or stale
   answers as `review-required`.
4. Acquire only the expressly approved revision through the approved mechanism;
   hash the exact payload, record provenance and exclusions, and retain a
   withdrawal/correction route.
5. If authority or rights remain unresolved, keep the source in this matrix as
   a candidate and retain the regional, non-operational pilot posture. Do not
   make national-completeness or operational-safety claims.

The related custodian request packet is [`source-authority-request-packet.md`](source-authority-request-packet.md).
This matrix is evidence preparation, not a substitute for custodian authority,
an independent external operator, or release-authority approval.
