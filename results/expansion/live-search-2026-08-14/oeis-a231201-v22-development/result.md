# OEIS A231201 v2.2 DEVELOPMENT: six honest bounded adversary deadlines

Date: 2026-08-14 UTC

Status: **VALID BOUNDED RUN; SIX UNVERIFIED ASSIGNMENTS; SIX HONEST ADVERSARY DEADLINES; NO MATHEMATICAL RESULT**

Campaign commit: `74f904b66edcb191f2172eaf04c303b438648b74`

GitHub Actions run:
[`31812806288`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31812806288)

The v2.2 finalization-reserve correction worked. All six round-0
`SMALL_BASIS_CEGAR` cells emitted complete, hash-bound 55-coordinate
assignments covering their frozen 192-row proposal bases. Each exact adversary
then searched for 48 seconds and wrote an honest `ADVERSARY_DEADLINE` terminal
within the six-second finalization reserve. Every terminal is bound to its
eight-row ledger, exact input assignment, cursor, partial-state count, and
incremental insertion-order frontier digest.

These assignments remain target-format proposals only. No adversary reported
`COMPLETE_COVER`, no pending candidate was created, and no independent final
target verifier ran. The workflow's `failure` conclusion is the intended
fail-closed aggregation of bounded nonzero stage outcomes, not a harness
failure or a mathematical counterexample.

## Independent evidence audit

Independent replay verified:

- the exact campaign head and all 164 expected static jobs: 14 successful jobs
  and 150 expected fail-closed failures;
- all 163 complete, unique, non-expired artifacts and all 163 `SHA256SUMS`
  manifests, covering 1,549 payload files (1,712 downloaded files including
  checksum manifests);
- all v1, v2, v2.1, and v2.2 frozen registries, the Python 3.9 constructor
  correction, and the v2.2 synthetic large-frontier finalization tests;
- the immutable source snapshots, all 10,000 parsed b-file rows, all 72 exact
  semantic gate rows, and all eight gate chains and terminals;
- the inherited exact 55-prime order table, combined period, and all 559,815
  least-positive-representative `C+` classes;
- all 162 stage ledgers containing 264 canonical hash-chain rows, all 162
  terminals, all 162 successful frozen artifact-verifier receipts, and all
  162 `STAGE_TERMINAL_PRESENT` diagnostics;
- all six assignments, including exact cell, assignment hash, artifact hash,
  basis hash, 192-row basis coverage, zero uncovered proposal rows, and
  least-prime-prefix rank;
- all six round-1 duplicate-suppression rows and their exact original
  assignment-artifact and adversary-terminal bindings;
- all six v2.2 deadline receipts with the frozen verifier, including the
  `ascii-r-comma-m-newline-insertion-order-v1` digest scheme, cursor, and
  48-second search / six-second reserve / exit-75 encoding; and
- zero candidate files, final target-verification executions, certificates,
  uncovered-class results, or verified counterexamples.

There were no checksum, hash-chain, terminal, receipt, or diagnostic failures.

Principal evidence locks:

- gate-attestation file SHA-256:
  `3afd22258c0127244558c41c67396d134aa32d50ecc88a66c6fcc6129afedc71`;
- inherited v2 manifest SHA-256:
  `064a07d90a497de08ea026171b6e1351975955ea5cc679d04a4093b50af31a7b`;
- v2.2 manifest SHA-256:
  `fe9341e7db1e10d5a25697e99ebe146e691d2bca2e2fcfd7e32185c3df5af30d`;
- v2.2 source/status attestation SHA-256:
  `40043eb6e5dead54c7dcd0fbc4184e4fd7fc27433038137e432edd41b5af26bb`;
- inherited `C+` arithmetic-stream SHA-256:
  `0f149875f16fb46003e3de185ed4a7ad487f513708ddb7a711b78905ecfea124`;
- combined period:
  `249728679334046128590697275594786190851950664265138725258656853072581268625525551538208526056090039506543200`.

## Assignment proposals

| Cell | Assignment SHA-256 | Assignment artifact SHA-256 | Least prime prefix |
|---|---|---|---:|
| `0_0` | `dc437cdec85bcd3469cfbbe46c3540765ba4887a9627b8656353ab8cdf9b794d` | `3927b0b6698a5b9cf5d0ae9d9d26f47bba5b3423502541078d39549f7858eba4` | 181 |
| `0_1` | `267a91722999291aba9c22464c5b60e8e940bf11be2829dc31f30a652a42a569` | `bf49bc114552cad114ff1d78c33d168d48d51a88628469d81203226c278ba2d4` | 179 |
| `0_2` | `ec269746aa44d3890ced4871e00e8390ae995511292353ace1249679a42be66f` | `df3ffb98fe5ffc39d07c7b0ddb45715d73688b652416b4f7402fe54ab655c756` | 193 |
| `1_0` | `5dd3efe67b33ac4032312dd6f0c1789ff2276bcdcc3953fdcd6385a91b25e9d3` | `520954f59efe6c86aafeb394df1217ca2dfb06511d944cf38591c818d02cd26d` | 191 |
| `1_1` | `b6172fb28b99d49bc442f2fc2cc51fe81a0add3c6d61bfbe31079c2227397bed` | `f1f56bfb8be84c927644670f0d3969ba9c64357c8e2cb71cfecd6fe8f2c10121` | 193 |
| `1_2` | `b080f5b91b7ccc1ecb12b4713390f998e069a326a4e6a404e2750dd4d63421b8` | `a384fde968a42c141b2c59dcaaffe101e3824245b25a90bb1d47b77b77f97d5c` | 173 |

Each assignment covers only its frozen 192-row proposal basis. None has a
complete-cover receipt, so none is a pending candidate or mathematical result.

## Arm and round comparison

| Arm | Round 0 construction | Round 1 construction | Round 2 construction | Adversary / final consequence |
|---|---|---|---|---|
| `COMPRESSED_SET_COVER_CP` | 6 `CAP_EXHAUSTED_NO_ASSIGNMENT` | 6 `CAP_EXHAUSTED_NO_ASSIGNMENT` | 6 `CAP_EXHAUSTED_NO_ASSIGNMENT` | 18 adversaries and 18 finals `NOT_RUN` |
| `DETERMINISTIC_GREEDY_REPAIR` | 6 `CAP_EXHAUSTED_NO_ASSIGNMENT` | 6 `CAP_EXHAUSTED_NO_ASSIGNMENT` | 6 `CAP_EXHAUSTED_NO_ASSIGNMENT` | 18 adversaries and 18 finals `NOT_RUN` |
| `SMALL_BASIS_CEGAR` | 6 `ASSIGNMENT_EMITTED` | 6 `CAP_EXHAUSTED_AFTER_ASSIGNMENTS` | 6 `CAP_EXHAUSTED_NO_ASSIGNMENT` | 6 round-0 deadlines; 12 later adversaries and all 18 finals `NOT_RUN` |

The round-1 small-basis constructors detected the six prior assignments and
preserved exact provenance instead of re-emitting them. Round 2 expanded each
small basis to 320 rows over three construction slices and emitted no further
assignment.

## Partial adversary frontiers

All six adversaries completed levels 0 through 6 (primes through 17), then
recorded their bounded deadline while processing level 7, prime 19, from an
input queue of 368,640 states.

| Cell | Input processed | Partial states | Cursor `(input index, residue, split index, value)` | Partial queue SHA-256 |
|---|---:|---:|---|---|
| `0_0` | 253,820 | 13,706,282 | `(253820, 1857333, 2, 5941413)` | `282ff9a0a0ec30455d7477ebc61d4564ac258668218f81fb63c855b21dce2362` |
| `0_1` | 249,455 | 13,470,619 | `(249455, 1002029, 52, 107188109)` | `2733af4b11cf96214eaa6579ca4ea73badf5eb9dea5bf00c47f5bcc6819cbb19` |
| `0_2` | 249,315 | 13,463,061 | `(249315, 203129, 54, 110473289)` | `48d0fdf08cac0ffdc1c64e5bc52f49543267d6ae009226264d58ab40f068afec` |
| `1_0` | 334,789 | 18,078,619 | `(334789, 351770, 14, 28940330)` | `5f4f3b6c77b90ecbce125349748457dc60d87eff84731d1bf62005d153b74c21` |
| `1_1` | 242,711 | 13,106,410 | `(242711, 1502602, 17, 36217282)` | `4b38445e8bfecfb4b1be17174f0690432a0230b8eafc63d600a7ed2daf213b18` |
| `1_2` | 253,901 | 13,710,669 | `(253901, 850528, 17, 35565208)` | `c4af6325f94ee8f769cb880f3a2476a6d1570007f41ec20426b604ad63b6e18d` |

Across cells, `input_processed` ranges from 242,711 to 334,789 and
`partial_states` from 13,106,410 to 18,078,619. The per-level
`DOMAIN_EXHAUSTED` rows through prime 17 mean only that those individual input
queues were fully processed. They are not an overall exhaustion conclusion;
48 frozen primes remain after the level-7 deadline, and v2.2 is neither
deduplicating nor resumable.

## Scope

The valid operational observation is limited to six proposal constructions
and six honest bounded adversary deadline receipts. There are zero complete
covers pending verification, final-verifier executions, verification failures,
verified counterexamples, and domain-exhaustion conclusions.

No issue, pull request, Lean certificate, release, README claim, or other
upstream action follows from this bounded DEVELOPMENT run.
