# WP-010 external operator handoff

**DRAFT — NOT SENT**  
**Prepared:** 2026-08-01  
**Purpose:** unsent handoff for an independent person/operator who can perform and report the bounded-pilot reproduction.

## Frozen references

- Repository: https://github.com/edithatogo/riopa-infrastructure
- Frozen revision: `8cac8b019cd20f7ba276147567442003489ac5b5`
- Internal preflight (non-qualifying): [wp010-internal-reproduction-preflight-20260801.md](wp010-internal-reproduction-preflight-20260801.md)
- Preserved successor packet: [Zenodo 10.5281/zenodo.21737563](https://doi.org/10.5281/zenodo.21737563)
- Submitted packet SHA-256: `e0dcf5eb08e9b4530929da92a439d2cb97ced51bfe34f4848d1a2ef94c15abe5`
- Expected reviewer-bundle SHA-256: `26bf2281f67c35f3327ebadeda3c8d5e7c6460e5b447dfc8417c851bcb0b6813`
- Reproduction issue: [#149](https://github.com/edithatogo/riopa-infrastructure/issues/149)

## Requested independent work

Please use a fresh checkout and temporary directory outside the implementation environment:

```sh
git clone https://github.com/edithatogo/riopa-infrastructure.git
cd riopa-infrastructure
git checkout 8cac8b019cd20f7ba276147567442003489ac5b5
test -z "$(git status --porcelain)"
python scripts/build_wp010_reviewer_bundle.py --output /tmp/wp010-a.zip
python scripts/build_wp010_reviewer_bundle.py --output /tmp/wp010-b.zip
cmp /tmp/wp010-a.zip /tmp/wp010-b.zip
shasum -a 256 /tmp/wp010-a.zip
unzip -q /tmp/wp010-a.zip -d /tmp/wp010-review
python /tmp/wp010-review/verify.py
```

## Required report

Return an immutable or content-bound report linked to issue #149 containing:

- exact commit, operating system, architecture and Python version;
- UTC start/end times, operator identity or stable pseudonym, organisation and relationship/conflict disclosure;
- every command, exit status, complete stdout/stderr digest and generated bundle digest;
- dependency observations, deviations, adverse findings and safety limitations;
- exactly one disposition: `pass`, `pass-with-limitations` or `fail`.

Do not include credentials, secrets or sensitive machine paths. This request is for independent evidence only; it does not authorise beta, release-candidate or stable-v1 promotion. The repository remains a regional, non-authoritative technical preview until the applicable custodian and release-authority gates are separately satisfied.

**Status:** draft handoff; not sent and not evidence of external reproduction.
