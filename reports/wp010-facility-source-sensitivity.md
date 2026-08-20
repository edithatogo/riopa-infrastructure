# WP-010 bounded facility-source sensitivity

This report records a deterministic, explicitly non-authoritative comparison of the locally
captured Rangitīkei District Council ambulance layer and regional OpenStreetMap ambulance
points. Raw payloads and coordinates remain in the ignored `.riopa-local` workspace.

## Reproduction

```console
uv run python scripts/compare_wp010_facility_sources.py \
  .riopa-local/wp010/public-source-capture/rangitikei-ambulance.geojson \
  .riopa-local/wp010/public-source-capture/osm-regional-pois.json
```

The `riopa-name-distance-v1` method compares only assertions of the same facility type,
uses punctuation-normalised name-token Jaccard similarity of at least 0.5, and uses a
great-circle distance threshold of 250 metres. Candidate selection is deterministic and
one-to-one.

## Result

| Measure | Result |
|---|---:|
| Council ambulance assertions | 3 |
| OSM ambulance assertions | 2 |
| Candidate pairs | 1 |
| Candidate distance | 5.660 m |
| Source-only assertions | 3 |

Canonical source hashes:

- council: `ece91d56518e618670c7c9d04c13a43530eeb653ba25386ca0d25e737fdca277`
- OSM: `fd8b83551e7ab8d404b2c2d1d94f084f5611f1d0fb77d9ef341bc40f3b810aea`

This result identifies a candidate pair, not an adjudicated match. Neither the council layer
nor OSM is promoted to an authoritative national facility registry. The three source-only
assertions demonstrate disagreement or coverage differences but do not establish which source
is correct. This bounded slice cannot estimate national completeness, classification accuracy,
or temporal currency.

An accountable analyst (human or agent) may record a reviewed disposition and rationale using
the review contract. Independent reproduction and broader source authority remain external gates.
