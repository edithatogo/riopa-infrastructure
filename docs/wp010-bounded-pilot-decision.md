# WP-010 bounded pilot decision packet

**Status: approved bounded pilot; panel validation accepted for this public-datasets-only preview; preservation and expiry conditions remain open.**
This approval is limited to the regional, non-operational scope below. It is not
national authority, publication approval, stable-release approval or evidence of
external independent reproduction. The panel decision applies only to this
bounded preview and does not satisfy beta, RC or stable-v1 external gates.

## Recommended decision

Approve the bounded regional, non-operational pilot using the rights-cleared
Rangitīkei and OpenStreetMap reference assertions, with the Wellington source
excluded and Stats NZ/LINZ candidates deferred. Deposit the preservation packet
before any public pilot representation.

The deterministic packet digest is recorded in the preservation handoff and
must be regenerated whenever this decision packet changes.

## Proposed scope

The pilot is limited to the locally captured Rangitīkei council ambulance
assertions and the regional OpenStreetMap supermarket/ambulance reference
assertions described in the source receipt and sensitivity report. Outputs are
research-only, non-authoritative and non-operational.

The pilot must not claim national completeness, current dispatch suitability,
clinical fitness, causal validity, commercial completeness or legal compliance.
Raw geometries remain in the ignored local evidence directory and are not part
of the proposed public packet.

## Source disposition

| Source | Proposed disposition | Reason |
|---|---|---|
| Rangitīkei public facilities | Include as regional reference assertions | Receipt records CC-BY-4.0 metadata and source limitations; not national authority |
| OpenStreetMap regional POIs | Include as exploratory reference assertions | ODbL attribution/share-alike obligations; completeness and currency are unverified |
| Wellington supermarket catalogue record | Exclude | Catalogue declares no licence; acquisition and redistribution remain disabled |
| Stats NZ population grid | Defer | Metadata-only candidate; exact-version payload receipt is pending |
| LINZ NZ Facilities | Defer | Metadata-only candidate; it is not a current service or capacity register |

## Required conditions before pilot publication

- Rights and attribution records are attached to the exact output packet.
- The internal pilot review receives a report satisfying
  `docs/bounded-pilot-review-protocol.md`; the external reproduction issue
  remains required before beta, release candidate or stable-v1 promotion.
- The output manifest, source hashes and generated report are deposited in a
  persistent repository or the release remains internal-only.
- An accountable release authority records the decision, exclusions, expiry and
  correction/withdrawal route.

## Decision record

- Decision: **approved for bounded regional pilot**
- Decision-maker: **programme owner approval recorded in Codex task**
- Validation authority: **three-agent subagent panel; consolidated report recorded as bounded-pilot evidence**
- Decision date: **2026-08-01**
- Expiry/review date: **2026-08-31; earlier review on any scope, rights, source-status or safety change**
- Conditions accepted: **rights-cleared sources only; non-authoritative and non-operational claims; preservation deposit before public representation; external reproduction remains required for beta/stable**
- Persistent decision identifier: `urn:riopa:decision:wp010-bounded-pilot:2026-08-01`
- Preservation destination: **Zenodo** — [record 21735818](https://zenodo.org/records/21735818)
- Persistent identifier: [`10.5281/zenodo.21735818`](https://doi.org/10.5281/zenodo.21735818)
- Deposited packet SHA-256: `bf22b88342d577ca84ce554b77cba90cf38c6df3e617a125c1801eb5d7291d9b`
- Successor preservation destination: **Zenodo** — [record 21737563](https://zenodo.org/records/21737563)
- Successor persistent identifier: [`10.5281/zenodo.21737563`](https://doi.org/10.5281/zenodo.21737563)
- Successor deposited packet SHA-256: `e0dcf5eb08e9b4530929da92a439d2cb97ced51bfe34f4848d1a2ef94c15abe5`
