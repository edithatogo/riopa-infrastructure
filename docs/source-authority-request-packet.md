# Source custodian and national-authority request packet

**Status:** prepared; not sent

This packet requests metadata and terms only. It does not acquire data, create
credentials, or imply authority, completeness or permission to redistribute.

## Requested source metadata

For each candidate national or regional source, request:

- custodian/owner and authoritative contact;
- dataset and layer identifiers, version, publication/update timestamps;
- geographic coverage, exclusions, resolution and known gaps;
- access mechanism and stability/SLO expectations;
- licence, attribution, redistribution, derivative-use and retention terms;
- privacy, sensitive-location, safety and disclosure restrictions;
- correction, withdrawal, takedown and successor-notification process;
- whether the custodian endorses national-coverage claims or only source-level
  authority statements.

## Questions requiring written answers

1. What population, geography and time period does the source cover, and what
   is explicitly out of scope?
2. What is the freshness/update cadence and how are late or corrected records
   identified?
3. May RIOPA capture metadata, preserve source responses, transform data and
   publish derived aggregates? Under which licence and attribution wording?
4. Which fields, geometries or linkages require controlled access or must not
   be retained?
5. Who may approve a release, and how should withdrawal or correction requests
   be authenticated and propagated?

## Evidence expected in response

An authoritative URL or signed statement, terms/licence reference, coverage
and freshness description, named contact/role, and a date-bound decision. A
non-response is recorded as `review-required`; it is not permission.

## Handling boundary

Until written authority and rights evidence are received, retain only public
metadata already available under its stated terms. Do not scrape, download,
link, or provision credentials based on this packet. National completeness and
operational use remain unclaimed.
