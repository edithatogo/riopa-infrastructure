# Credential Compromise and Rollback Exercise

## Scenario
A mock release token was simulated to be compromised.

## Actions Taken
1. The compromised token was revoked immediately.
2. The affected release was marked as withdrawn in the release manifest.
3. The codebase was reverted to the previous known good state.
4. A new release was issued with a clean token and updated attestations.

## Outcome
The rollback scenario passed successfully. The incident response policy is effective.
