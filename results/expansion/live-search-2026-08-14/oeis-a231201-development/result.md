# OEIS A231201 DEVELOPMENT: bounded solver deadlines before target evaluation

Date: 2026-08-14 UTC

Status: **VALID BOUNDED DEVELOPMENT EXECUTION; NO TARGET ASSIGNMENT; NO MATHEMATICAL RESULT**

Campaign commit: `7669f2260b2dc1f05cf4aeb389f80d3c7c37b86a`

GitHub Actions run:
[`31805086511`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31805086511)

This contaminated, target-specific DEVELOPMENT run passed its frozen-harness
validation and exact database gate. All six CEGAR workers then reached the
frozen internal deadline while CP-SAT was still `UNKNOWN`. No worker produced
a feasible target assignment, so no exact adversary was invoked and no
candidate entered final verification.

The Actions conclusion is `failure` because each worker correctly propagated
the contract's fail-closed search exit code `75`. The preserved evidence is
complete and internally valid. This is a bounded deadline outcome, not a
harness defect, verification failure, solver-certified infeasibility, finite
domain exhaustion, counterexample, or evidence that the conjecture is true.

## Independent evidence audit

Independent replay verified:

- the exact campaign head, eight expected jobs, two successful prerequisite
  jobs, and six deadline-failed worker jobs;
- all seven complete and unique non-expired artifacts: one gate and exactly
  the six `(a_2,a_3)` shards `(0,0)` through `(1,2)`;
- all seven `SHA256SUMS` manifests, covering all 73 non-manifest files (80
  downloaded files including the manifests);
- the frozen-file manifest and every frozen harness hash at the campaign
  commit;
- all immutable source snapshots and contamination controls at their frozen
  hashes, including the Lean git-blob identity and all 10,000 parsed b-file
  rows;
- all 72 semantic gate rows by independent exact recomputation, their eight
  canonical SHA-256 chains, eight `GATE_CHUNK_EXHAUSTED` terminals, named
  controls, gate manifest, and diagnostic receipt;
- the exact 55-prime order table, combined period, and all 559,815 frozen
  positive-periodic `C+` residue classes using the least-positive
  representative correction, including the corrected prime-2 classes;
- all six master ledger chains, checkpoint hashes, terminal bindings, seed
  constraints `x=1..4096`, exact shard identities, and execution receipts;
  and
- zero assignments, adversary ledgers, adversary receipts, candidates, final
  ledgers, final-verification receipts, and certificates.

Principal evidence locks:

- gate-attestation file SHA-256:
  `9b532225177a9919cc809ebe28d296f4bf53fa573b500231966e0968c05810fe`;
- frozen manifest SHA-256:
  `bed3cb25993017d044ecb8559a7f84125479f171ad1e1ff4057c4026f3614f2b`;
- source/status attestation SHA-256:
  `a0714517770d138024a1aa3828e7620502699b777ef6f6124632f058529b3bf3`;
- Lean module SHA-256:
  `3cfc75e1613477cd4087e6fe9406658e27981abc2c0834958a311e9551bc8fa1`;
- OEIS source-record SHA-256:
  `f32bbcf524babe35878ac88d69bfb6a048eed0b7e461b2b5738d6bc3e93df129`;
- OEIS b-file SHA-256:
  `5e4e34c5132b40f4666ed04000615b4d652a6af46c9a2ad5022c725d293e5ace`;
- independent `C+` arithmetic-stream SHA-256:
  `0f149875f16fb46003e3de185ed4a7ad487f513708ddb7a711b78905ecfea124`;
- combined period:
  `249728679334046128590697275594786190851950664265138725258656853072581268625525551538208526056090039506543200`.

## Exact worker dispositions

| Fixed `(a_2,a_3)` | Solver status | Solver attempts | Assignment evaluations | Adversary calls | Terminal | Search exit |
|---|---|---:|---:|---:|---|---:|
| `(0,0)` | `UNKNOWN` | 1 | 0 | 0 | `DEADLINE_PREFIX` | 75 |
| `(0,1)` | `UNKNOWN` | 1 | 0 | 0 | `DEADLINE_PREFIX` | 75 |
| `(0,2)` | `UNKNOWN` | 1 | 0 | 0 | `DEADLINE_PREFIX` | 75 |
| `(1,0)` | `UNKNOWN` | 1 | 0 | 0 | `DEADLINE_PREFIX` | 75 |
| `(1,1)` | `UNKNOWN` | 1 | 0 | 0 | `DEADLINE_PREFIX` | 75 |
| `(1,2)` | `UNKNOWN` | 1 | 0 | 0 | `DEADLINE_PREFIX` | 75 |

Every worker bound the successful gate (`gate_exit_code=0`), successfully
replayed its master/checkpoint artifacts (`artifact_exit_code=0`), and had no
candidate requiring final replay (`final_verifier_exit_code=0`). Worker
elapsed times ranged from 54.609917136 to 54.801369092 seconds. Across the six
bounded CP-SAT attempts, the diagnostic counters total 12,124,806 branches
and 2,072,418 conflicts. These are effort counters only; they do not certify
infeasibility.

## Scope

`DEADLINE_PREFIX` records one non-resumable bounded attempt. The checkpoint is
diagnostic and cannot resume an omitted queue. Because no feasible assignment
was returned, this run evaluated zero target assignments and did not reach the
generalized-CRT adversary or independent final coverage verifier.

Accordingly, this execution supports only the operational conclusion that the
frozen 54-second, one-worker CP-SAT budget did not resolve any of the six seed
models. It does not support `SOLVER_INFEASIBLE_UNVERIFIED`, `NO_COMPLETE_COVER`,
`DOMAIN_EXHAUSTED`, `VERIFICATION_FAILED_UNCOVERED_CLASS`, or
`VERIFIED_COUNTEREXAMPLE`. No issue, pull request, Lean certificate, release,
README claim, or other upstream action follows.
