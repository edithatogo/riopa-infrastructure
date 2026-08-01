# Bounded pilot review protocol

This protocol applies only to an internal or bounded, non-operational pilot.
It does not replace the external-person/operator requirement for beta, release
candidate or stable-v1 reproduction.

## Eligible reviewer

A subagent or agent analyst may provide pilot review when it has a distinct
review identity, a separate execution process, disclosed relationship to the
implementation, and a recorded scope and method. The review must be adverse-
findings capable and must not be represented as external validation.

## Required evidence

The review record must include:

- exact repository revision and generated-artifact digest;
- reviewer identity and relationship disclosure;
- operating system, architecture and runtime;
- commands, exit statuses and output digest;
- findings, deviations and limitations;
- a decision of `pass`, `pass-with-limitations` or `fail`;
- the explicit statement that the review is internal pilot evidence.

## Promotion rule

Pilot review can support an internal or bounded regional release only when
rights, scope, safety and publication conditions are separately satisfied.
It cannot close the independent-reproduction gate for M5/M6, beta, release
candidate or stable-v1 promotion.
