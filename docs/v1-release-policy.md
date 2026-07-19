# Stable-v1 release, compatibility and support policy

## Version axes

Software, schema/ontology profiles, datasets, analytical model specifications and research objects are independently versioned. A repository release must state exactly which versions it contains and which compatibility policy applies.

## Channels

- **Experimental:** interfaces may change without backward compatibility; migration notes are still required for published artifacts.
- **Candidate:** intended interface direction is stable, changes require compatibility analysis and explicit notice.
- **Release candidate:** normative inventory frozen; only release blockers, documentation and qualification changes are accepted.
- **Stable:** covered by the v1 compatibility, deprecation, support, security and preservation obligations.

## Compatibility

Within the supported 1.x series:

- patch releases do not intentionally break documented schemas, APIs, CLI, configuration or file formats;
- compatible additions require defaults or feature negotiation and cannot silently change scientific meaning;
- deprecations require an announced replacement, migration guide, warning period and tests;
- removals or incompatible semantic changes require a new major profile or software release;
- extensions use namespaced, versioned schemas and cannot redefine normative fields;
- persisted source evidence, event hashes and released research objects are immutable.

Scientific estimands, classifications, optimisation objectives, simulation assumptions and default parameters are versioned as model specifications even when software compatibility is unchanged.

## Release authority

The stable release requires approvals from release management, security, governance, scientific-method and independent-reproducibility roles. The decision and supporting evidence are signed or attested. Critical security, governance prohibition, integrity failure and unresolved P0/P1 categories cannot be waived.

## Support and maintenance

The v1 release publishes supported environments, support channels, response boundaries, security policy, maintainer roster and deprecation schedule. Annual revalidation includes conformance, preservation fixity, restore, dependency/security review, benchmark regression and maintainer succession.


## Post-GA status and end of support

Stable status is evidence backed and cannot be implied indefinitely by the existence of a `1.x` tag. A material lapse in security response, maintainer coverage, preservation, conformance or operational obligations triggers a published support-status review. The project then restores compliance, narrows the supported surface, announces a migration path, or archives the affected capability. End-of-support notices identify dates, affected contracts, replacement or export paths, preservation state and the security implications of continued use.
