# EIL-001 Independent Verification

This directory defines the independent-verification boundary for **EIL-001 Constitutional Baseline v1.0**.

Frozen implementation candidate SHA-256:

`f4f1e93db44fd1cb9c4834ba4973f7834e3972f832c547437627db7ab176f62b`

## Registered verification claims

EIL-C-001 through EIL-C-008 are separate verification propositions. Their initial status is **NOT_ESTABLISHED**.

The harness does not modify the candidate, does not promote qualification, and does not grant authority.

## Execution

```
python3 verification/independent_harness.py path/to/EIL-001-v0.2-implementation-candidate.zip
```

The source hash must match the frozen candidate exactly. A mismatch aborts the run.

## Evidence discipline

- Local test results remain historical evidence.
- Independent probes are separate evidence.
- Failures are findings, not repairs.
- Qualification remains separate.
- Human ratification remains external.
- The harness must not be treated as the source of truth for its own success.
