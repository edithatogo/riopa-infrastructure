# Bounded pilot review protocol

This protocol applies only to an internal or bounded, non-operational pilot
using public datasets only. For this tier, the programme owner authorises a
three-agent panel as the pilot validation authority. It does not replace the
external-person/operator requirement for beta, release candidate or stable-v1.

## Eligible reviewer

A subagent or agent analyst may provide pilot review when it has a distinct
review identity, a separate execution process, disclosed relationship to the
implementation, and a recorded scope and method. The review must be adverse-
findings capable and must not be represented as external validation.

A qualifying panel consists of at least three isolated agents: a reproducer,
an adversarial analyst and an evidence/rights auditor. The orchestrator must
preserve separate reports, dissent, relationship disclosures and content
hashes.

## Required evidence

The review record must include:

- exact repository revision and generated-artifact digest;
- reviewer identity and relationship disclosure;
- operating system, architecture and runtime;
- commands, exit statuses and output digest;
- findings, deviations and limitations;
- a decision of `pass`, `pass-with-limitations` or `fail`;
- the explicit statement that the review is internal pilot evidence.
- at least two independent deterministic builds with matching digests;
- a consolidated, content-bound panel report recording concordance and dissent.

## Promotion rule

Pilot review can support an internal or bounded regional release only when
rights, scope, safety and publication conditions are separately satisfied.
It may close the bounded-pilot validation gate when the criteria above and all
rights, scope, safety and preservation conditions are met. It cannot close the
independent-reproduction gate for M5/M6, beta, release candidate or stable-v1.
