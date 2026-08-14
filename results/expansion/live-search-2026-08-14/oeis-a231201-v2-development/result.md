# OEIS A231201 v2 DEVELOPMENT: invalid frozen runtime, no target evaluation

Date: 2026-08-14 UTC

Status: **INVALID FROZEN HARNESS — PYTHON 3.9 RUNTIME INCOMPATIBILITY; NO MATHEMATICAL RESULT**

Campaign commit: `83ef494622957db578079772b37f716f7060db89`

GitHub Actions run:
[`31809864013`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31809864013)

The immutable source/database gate passed, but every round-0 constructor
crashed before producing an assignment. The frozen workflow selected Python
`3.9.23`, while `construct_oeis_a231201_v2.py` called `int.bit_count()` during
its mandatory deterministic-greedy hint construction. That method is absent
from the selected runtime. Every one of the 18 arm/cell jobs therefore emitted
`WORKER_ERROR` with the exact exception

```text
AttributeError: 'int' object has no attribute 'bit_count'
```

The static downstream matrix failed closed exactly as designed: later
constructors emitted `PREREQUISITE_NOT_RUN`, and all exact-adversary and
independent-final jobs emitted `NOT_RUN`. No assignment was constructed or
evaluated. This run is an operational harness failure, not a bounded search
outcome, deadline, infeasibility observation, exhaustion result, verification
failure, counterexample, or evidence that the conjecture is true.

## Independent evidence audit

Independent replay verified:

- the exact campaign head and all 164 expected static jobs: two successful
  prerequisite jobs and 162 failed stage jobs;
- all 163 complete, unique, non-expired artifacts: one gate plus 18 artifacts
  in each of the nine construction/adversary/final round groups;
- all 163 `SHA256SUMS` manifests, covering all 1,447 payload files (1,610
  downloaded files including checksum manifests);
- the v1 and v2 frozen-file manifests and all frozen harness hashes at the
  campaign commit;
- the inherited immutable source snapshots and contamination controls, all
  10,000 parsed b-file rows, and all 72 exact semantic gate rows;
- the eight gate ledger chains and `GATE_CHUNK_EXHAUSTED` terminals;
- the exact 55-prime order table, combined period, and all 559,815 inherited
  least-positive-representative `C+` classes;
- all 162 stage ledger/terminal chains containing 180 canonical rows, all 162
  execution-status receipts, all 162 successful artifact-verifier receipts,
  and all 162 `STAGE_TERMINAL_PRESENT` bootstrap diagnostics; and
- zero assignment artifacts, target-adversary calls, pending candidates,
  target final-verifier calls, or certificates.

There were no artifact-integrity or structural-verifier failures. The evidence
faithfully records the runtime failure and its fail-closed cascade; that does
not make the construction protocol usable.

Principal evidence locks:

- gate-attestation file SHA-256:
  `ce923e17711f0098a19d3acaec10550a9bab4ddb0d288cb1db0c17dc36fa72ed`;
- inherited v1 manifest SHA-256:
  `bed3cb25993017d044ecb8559a7f84125479f171ad1e1ff4057c4026f3614f2b`;
- v2 manifest SHA-256:
  `064a07d90a497de08ea026171b6e1351975955ea5cc679d04a4093b50af31a7b`;
- v2 source/status attestation SHA-256:
  `510d645c4701ed9fe5b28c4aa8bbaa233d06054f82a262a9ee0c5e4afd96bc83`;
- inherited `C+` arithmetic-stream SHA-256:
  `0f149875f16fb46003e3de185ed4a7ad487f513708ddb7a711b78905ecfea124`;
- combined period:
  `249728679334046128590697275594786190851950664265138725258656853072581268625525551538208526056090039506543200`.

## Exact fail-closed cascade

| Stage | Round | Jobs | Terminal | Prerequisite code | Stage code | Artifact verifier | Job code |
|---|---:|---:|---|---:|---:|---:|---:|
| construction | 0 | 18 | `WORKER_ERROR` | 0 | 75 | 0 | 75 |
| adversary | 0 | 18 | `NOT_RUN` | 94 | 78 | 0 | 94 |
| construction | 1 | 18 | `PREREQUISITE_NOT_RUN` | 95 | 75 | 0 | 95 |
| adversary | 1 | 18 | `NOT_RUN` | 94 | 78 | 0 | 94 |
| construction | 2 | 18 | `PREREQUISITE_NOT_RUN` | 99 | 75 | 0 | 99 |
| adversary | 2 | 18 | `NOT_RUN` | 94 | 78 | 0 | 94 |
| independent final | 0–2 | 54 | `NOT_RUN` | 94 | 78 | 0 | 94 |

The six `SMALL_BASIS_CEGAR` round-0 constructors bound 192 rows each before
the shared greedy-hint crash. The other twelve round-0 constructors bound
their complete active seed rows: 1,366 rows in cells `0_0` and `1_2`, and
1,365 in each other cell. All reported `construction_rounds` are zero; no
CP-SAT slice or greedy repair round completed.

Round-1 constructors rejected the unusable round-0 adversary predecessor with
code 95. Round-2 constructors rejected the full unusable predecessor chain
with code 99. All adversary and final processes rejected their immediate
predecessor execution receipts with code 94. Their `NOT_RUN` ledgers are
control-flow evidence only; they contain no target evaluation.

## Scope

The gate result remains a valid source/database sanity receipt, but the v2
proposal experiment produced no search evidence. In particular, this run has
zero `ASSIGNMENT_EMITTED`, `BASIS_INFEASIBLE_UNVERIFIED`, deadline,
`UNCOVERED_CLASS`, `COVER_FOUND_PENDING_VERIFY`,
`VERIFICATION_FAILED_UNCOVERED_CLASS`, and `VERIFIED_COUNTEREXAMPLE` outcomes.
It cannot be promoted to `NO_COMPLETE_COVER` or any exhaustion claim.

No issue, pull request, Lean certificate, release, README claim, or other
upstream action follows from this invalid run.
