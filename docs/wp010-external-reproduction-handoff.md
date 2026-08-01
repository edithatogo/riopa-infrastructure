# WP-010 external reproduction handoff

This handoff is ready for an external person/operator. It does not claim that
the reproduction has been performed.

## Frozen references

- Published pilot packet: [Zenodo 10.5281/zenodo.21735818](https://doi.org/10.5281/zenodo.21735818)
- Deposited packet SHA-256: `bf22b88342d577ca84ce554b77cba90cf38c6df3e617a125c1801eb5d7291d9b`
- Repository: `https://github.com/edithatogo/riopa-infrastructure`
- Exact commit under test: `6b99b3ee42110733b36fd7777c960832719359b8`
- Expected benchmark: `urn:riopa:benchmark:wp010:synthetic-methods:1.0.0`
- Reviewer-bundle builder: `scripts/build_wp010_reviewer_bundle.py`
- Expected deterministic reviewer-bundle SHA-256: `26bf2281f67c35f3327ebadeda3c8d5e7c6460e5b447dfc8417c851bcb0b6813`
- Result issue: [#149](https://github.com/edithatogo/riopa-infrastructure/issues/149)

## Operator procedure

Use a clean checkout and a fresh temporary directory outside the implementer's
environment. Record the exact commit, operating system, architecture, Python
version, UTC start/end times, reviewer identity or stable pseudonym,
organisation, relationship/conflict disclosure and all commands run.

```sh
git clone https://github.com/edithatogo/riopa-infrastructure.git
cd riopa-infrastructure
git checkout 6b99b3ee42110733b36fd7777c960832719359b8
test -z "$(git status --porcelain)"
python scripts/build_wp010_reviewer_bundle.py --output /tmp/wp010-a.zip
python scripts/build_wp010_reviewer_bundle.py --output /tmp/wp010-b.zip
cmp /tmp/wp010-a.zip /tmp/wp010-b.zip
shasum -a 256 /tmp/wp010-a.zip
unzip -q /tmp/wp010-a.zip -d /tmp/wp010-review
python /tmp/wp010-review/verify.py
```

Return a content-bound report containing the exact commit and bundle digest,
environment, stdout/stderr digest, exit status, deviations, findings and one
decision: `pass`, `pass-with-limitations` or `fail`. Do not include secrets or
sensitive machine paths. Publish the report as an issue attachment or other
immutable/persistent artifact and link it from issue #149. This report is
required before beta, release-candidate or stable-v1 promotion; an agent or
subagent review does not substitute for it.
