# OEIS A231201 v2.1 DEVELOPMENT: six assignments, invalid adversary termination

Date: 2026-08-14 UTC

Status: **INVALID ADVERSARY EXECUTION; SIX UNVERIFIED ASSIGNMENTS; NO MATHEMATICAL RESULT**

Campaign commit: `8c1046821df46d141c1c83f32cb6209262df4eb2`

GitHub Actions run:
[`31811239530`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31811239530)

The Python 3.9 constructor correction worked. All six round-0
`SMALL_BASIS_CEGAR` cells emitted complete, hash-bound 55-coordinate
assignments covering their frozen 192-row proposal bases. Those are target-format
proposals, not candidates or mathematical results.

Each of the six exact adversary processes subsequently hit the external
process cap with exit code `124`. Each preserved a valid seven-row prefix
through prime 17, but none wrote the required `adversary-terminal.json`.
Artifact verification therefore could not run and correctly recorded exit
code `1`; each bootstrap diagnostic says `STAGE_TERMINAL_UNAVAILABLE`.
Downstream construction and final stages rejected these unusable predecessors.

This is a harness/process-finalization failure, not an honest
`ADVERSARY_DEADLINE`, `UNCOVERED_CLASS`, complete cover, verification failure,
or exhaustion result. No candidate reached the independent final verifier.

## Independent evidence audit

Independent replay verified:

- the exact campaign head and all 164 expected static jobs: eight successful
  jobs and 156 failed jobs;
- all 163 complete, unique, non-expired artifacts and all 163
  `SHA256SUMS` manifests, covering 1,507 payload files (1,670 downloaded files
  including checksum manifests);
- all v1, v2, and v2.1 frozen registries and the corrected Python 3.9
  constructor smoke paths;
- the immutable source snapshots, all 10,000 parsed b-file rows, all 72 exact
  semantic gate rows, and all eight gate chains and terminals;
- the inherited exact 55-prime order table, combined period, and all 559,815
  least-positive-representative `C+` classes;
- all 162 stage ledgers containing 222 canonical hash-chain rows;
- all 156 available stage terminals and their successful frozen artifact
  verification receipts;
- all six absent-terminal adversary prefixes, execution receipts, checksum
  manifests, and bootstrap diagnostics;
- all six assignments, including exact matrix identity, frozen-prime
  coordinates, `(a_2,a_3)` cell, assignment hash, basis hash, 192-row basis
  coverage, zero uncovered proposal rows, and least-prime-prefix rank; and
- zero candidate files, independent target-verification executions,
  certificates, or counterexamples.

There were no checksum or hash-chain failures. The six missing adversary
terminals are the substantive invalid-run condition.

Principal evidence locks:

- gate-attestation file SHA-256:
  `a11b31bb7b5fa5eec8f0c874bd0e49d3a11383122a24aebf4b1bb58301d205b2`;
- inherited v2 manifest SHA-256:
  `064a07d90a497de08ea026171b6e1351975955ea5cc679d04a4093b50af31a7b`;
- v2.1 manifest SHA-256:
  `59a00f18471963e79936250b7409fe3b26234fd30625b1de36f58cacc5af38e5`;
- v2.1 source/status attestation SHA-256:
  `6436e9b3d9003438aaaab33c817c9616ec955dba4aaa3ab254a149e37d10a75e`;
- inherited `C+` arithmetic-stream SHA-256:
  `0f149875f16fb46003e3de185ed4a7ad487f513708ddb7a711b78905ecfea124`;
- combined period:
  `249728679334046128590697275594786190851950664265138725258656853072581268625525551538208526056090039506543200`.

## Assignment proposals

| Cell | Assignment SHA-256 | Assignment artifact SHA-256 | Least prime prefix |
|---|---|---|---:|
| `0_0` | `dc437cdec85bcd3469cfbbe46c3540765ba4887a9627b8656353ab8cdf9b794d` | `d0c85e6b67313f94a5f2cdcf5b29778b49c0fc77ad7a38d7c7c24c72864d4a62` | 181 |
| `0_1` | `267a91722999291aba9c22464c5b60e8e940bf11be2829dc31f30a652a42a569` | `66014ffe561cf7e7cebab3b718c9562893e581c9c1adec15c6754dec1c2cf2fd` | 179 |
| `0_2` | `ec269746aa44d3890ced4871e00e8390ae995511292353ace1249679a42be66f` | `a5c4a9ee77cc5152ef1b9adc532faf8a588dab8137bfe845612333f15fbc7ada` | 193 |
| `1_0` | `5dd3efe67b33ac4032312dd6f0c1789ff2276bcdcc3953fdcd6385a91b25e9d3` | `a98de34cbd26491685748ca683c92f66476cffec7ca66ddfa04b7a4ec1be4667` | 191 |
| `1_1` | `b6172fb28b99d49bc442f2fc2cc51fe81a0add3c6d61bfbe31079c2227397bed` | `4c17972a48a1a183d15603cc4d9b962da7f844b7c7d92e964c95781a1867c61a` | 193 |
| `1_2` | `b080f5b91b7ccc1ecb12b4713390f998e069a326a4e6a404e2750dd4d63421b8` | `82566f7a9389722916dc84592872b5f158a749682c9bde24d147168527676243` | 173 |

Each assignment covers only its frozen 192-row proposal basis. None has an
exact-adversary receipt, so none is a pending cover or candidate.

## Exact stage dispositions

| Stage group | Jobs | Terminal/evidence | Prerequisite | Stage | Artifact verifier | Job |
|---|---:|---|---:|---:|---:|---:|
| round-0 small-basis construction | 6 | `ASSIGNMENT_EMITTED` | 0 | 0 | 0 | 0 |
| all compressed/greedy construction rounds | 36 | `CAP_EXHAUSTED_NO_ASSIGNMENT` | 0 | 75 | 0 | 75 |
| round-1/2 small-basis construction | 12 | `PREREQUISITE_NOT_RUN` | 95 / 99 | 75 | 0 | 95 / 99 |
| round-0 small-basis adversary | 6 | terminal unavailable after seven rows | 0 | 124 | 1 | 1 |
| other adversaries | 48 | `NOT_RUN` | 0 or 94 | 78 | 0 | 78 or 94 |
| all independent-final jobs | 54 | `NOT_RUN` | 0 or 94 | 78 | 0 | 78 or 94 |

The six partial adversary ledgers each contain complete per-level rows for
primes `2,3,5,7,11,13,17`. Their final recorded level consumed all 11,520
input states and emitted 368,640 states. The row status `DOMAIN_EXHAUSTED`
means only that the input queue at that individual refinement level was fully
processed. Because no adversary terminal exists and 48 frozen primes remain,
these prefixes cannot be interpreted as an overall adversary outcome,
`NO_COMPLETE_COVER`, or domain exhaustion.

## Scope

The valid operational observation is limited to six successful proposal
constructions on 192-row bases. The exact adversaries have no terminal outcome,
and the independent final jobs performed no target verification. There are
zero honest adversary deadlines, uncovered classes, pending covers,
verification failures, verified counterexamples, and exhaustion conclusions.

No issue, pull request, Lean certificate, release, README claim, or other
upstream action follows from this invalid run.
