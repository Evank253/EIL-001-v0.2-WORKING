# KCN → EIL Non-Promotion Verification Plan v1.0

## Status

- Constitutional requirement: FROZEN
- Implementation: TO_BE_VERIFIED
- Independent verification: NOT_ESTABLISHED
- Qualification: NOT_ESTABLISHED
- Human ratification: NOT_ESTABLISHED
- Authority: HUMAN_ONLY

## Governing invariant

Knowledge ingestion may create, classify, link, and preserve claims, but it may not promote their evidence, verification, qualification, or authority state.

## Direct promotion attack family

The harness must attempt, from an ingested E0 claim, unauthorized promotion to:

- E1
- E2
- E3
- E4
- E5
- VERIFIED
- QUALIFIED
- AUTHORIZED

Each attempt must be rejected unless the required intervening evidence/verification/qualification/authorization event exists.

## Indirect promotion attack family

The harness must test whether promotion can occur through:

1. duplicate ingestion
2. AI confidence
3. AI consensus
4. source reputation
5. semantic similarity
6. successful execution
7. prior qualification
8. imported verification labels
9. downstream reinterpretation

## Result semantics

- PASS: prohibited promotion was rejected.
- FAIL: prohibited promotion occurred.
- NOT_MEASURED: the required boundary could not actually be exercised.

A PASS establishes only the tested behavior. It does not establish EIL or KCN qualification.

## Evidence chain

TEST DEFINITION → EXECUTION → RAW RESULT → REPRODUCTION → INDEPENDENT VERIFICATION → QUALIFICATION → HUMAN RATIFICATION

Failures are preserved as findings and are not repaired in-place.

## Verification claims

- EIL-KCN-001 — Ingestion Non-Promotion
- EIL-KCN-002 — Source/Status Separation
- EIL-KCN-003 — Historical Claim Immutability
- EIL-KCN-004 — Evidence Linkage
- EIL-KCN-005 — Repetition Non-Promotion
- EIL-KCN-006 — AI Non-Authority
- EIL-KCN-007 — Domain Independence
- EIL-KCN-008 — Qualification Boundary
- EIL-KCN-009 — Human Authority Boundary

## Scope boundary

This plan does not assert that SCARS metrics, KCN economic controls, physical isolation, or any other KCN capability is qualified. Those remain separate verification targets with their own evidence requirements.
