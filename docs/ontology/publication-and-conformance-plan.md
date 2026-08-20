# Canonical ontology publication and conformance plan

This plan describes the evidence required before the canonical ontology can be
called a published normative release. The current release remains a
repository fixture (`canonical-ontology-release-1.0.0.json`) and the
conformance manifest remains `bounded-pending`.

## Publication decision

The release owner must record a target repository, licence, persistent
identifier and publication date in
`ontology-publication-decision-template.json`. A repository URL alone is not
evidence of publication. The target must provide immutable versioned content,
an accessible persistent identifier and terms covering reuse of the ontology
artifacts.

Recommended target: an institutional repository with DOI/versioning support.
Fallback: a project-controlled repository with immutable tagged releases and
an archival mirror. If neither is approved, retain `unpublished` status.

Do not publish the descriptor as normative until semantic review confirms the
namespace, vocabulary and licence. Publishing a fixture does not itself close
SHACL or cross-language gates.

## Conformance evidence

The release can move beyond `bounded-pending` only when all of the following
are attached to the same release digest:

1. JSON Schema and semantic validator output for the positive and negative
   corpus (currently evidenced by Python tests).
2. A SHACL report from a pinned validator, including validator version and
   shape-set digest. A structural validator is an interim safety gate, not a
   SHACL claim.
3. A non-Python implementation round-trip against the frozen corpus, with
   runtime/version, commands, output digest and any explicitly bounded loss.
4. Migration output for every supported version transition.
5. A persistent publication identifier and licence record.

Each report must identify the exact Git revision and the SHA-256 values in
`canonical-conformance-manifest-1.0.0.json`. A changed artifact requires a
new release or successor manifest; never mutate a deposited evidence claim.

## Fallback posture

Until the evidence above exists, advertise only the Python, repository-fixture
profile. Do not claim SHACL conformance, cross-language interoperability or
formal ontology authority, and keep the release posture regional and
technical-preview-only.
