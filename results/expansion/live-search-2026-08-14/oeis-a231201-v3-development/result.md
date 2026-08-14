# OEIS A231201 v3 DEVELOPMENT: 57 least-escape steps, no full-seed proposal

Date: 2026-08-14 UTC

Status: **VALID CONSTRUCTOR DIAGNOSTIC; ALL 54 CELLS CAPPED; ZERO FULL-SEED PROPOSALS; NO MATHEMATICAL RESULT**

Campaign commit: `c2777e4b39288f4f372f2625eb37524d322581f1`

GitHub Actions run:
[`31815834051`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31815834051)

The immutable source/database gate passed, and the exact 3-arm × 6-cell ×
3-round matrix ran to completion. Every constructor wrote
`CONSTRUCTION_CAP_NO_PROPOSAL` with prerequisite exit `0`, bounded stage exit
`75`, artifact-verifier exit `0`, and a present diagnostic terminal. The
workflow's `failure` conclusion is therefore the intended fail-closed
aggregation of 54 bounded diagnostic outcomes, not an installation, gate,
runner, checksum, or verifier failure.

No cell covered its complete active seed in `1..4096`. There are zero
`FULL_SEED_PROPOSAL_EMITTED_DIAGNOSTIC` terminals, proposal files, seed-closure
receipts, candidates, target-verification jobs, certificates, or mathematical
results.

## Independent evidence audit

Independent replay verified:

- the exact run head, 56 expected jobs, two successful setup jobs, and 54
  expected diagnostic failures;
- all 55 complete, unique, non-expired artifacts and all 55 `SHA256SUMS`
  manifests, covering 514 payload files (569 files including manifests);
- the exact gate, all 10,000 b-file rows, all 72 semantic gate rows, and all
  eight gate chains and terminals;
- all 54 construction ledgers containing 241 canonical hash-chain rows, all
  54 terminals, execution receipts, successful artifact-verifier receipts,
  and `STAGE_TERMINAL_PRESENT` diagnostics;
- all 54 construction artifacts with the frozen v3 artifact verifier;
- all 57 least-escape delta documents directly from
  `(x - 2^x) mod q`, including proposal hash, current-basis coverage, exact
  lexicographically least active-seed miss, one-row basis growth, and final
  basis order; and
- zero proposal or promotion artifacts and no target-stage execution surface.

There were no checksum, chain, terminal, semantic replay, or infrastructure
failures.

Principal evidence locks:

- gate-attestation file SHA-256:
  `ac646395b5d86a08e07aae7a227515402692386f18f46d187a1dc7d11781bac2`;
- v3 manifest SHA-256:
  `70460946849ad53e76e6932ce829056fa1cdafbcaa03289dc7ad59a340a82472`;
- v3 source/status attestation SHA-256:
  `a46f67445da6f974dc97176cd0c9d50fc9a8f5bd964645212ab33ba815d7af07`.

## Arm outcomes

| Arm | Jobs | Work performed | Outcome |
|---|---:|---|---|
| `COMPRESSED_SET_COVER_CP` | 18 | full active seed (1,365 or 1,366 rows); zero CP slices after the preliminary greedy hint consumed the search budget | 18 caps, no proposal |
| `DETERMINISTIC_GREEDY_REPAIR` | 18 | full active seed; one recorded repair round per job, but the second pass had zero moves after the preliminary hint consumed the budget | 18 caps, no proposal |
| `SMALL_BASIS_CEGAR` | 18 | 112 CP slices: 57 `OPTIMAL`, 55 `UNKNOWN`; every optimal assignment exposed and recorded a least seed escape | 18 caps, 57 deltas, no closure or proposal |

The first two arms' caps are low-information operational observations. Their
unconditional preliminary greedy pass used the 48-second search budget before
the compressed CP or recorded repair pass could do substantive work. They do
not establish infeasibility or full-seed exhaustion.

## Small-basis cross-round comparison

| Round | Initial rows per cell | CP slices | Least-escape deltas | Final basis rows by cell `0_0..1_2` | Full-seed closures |
|---:|---:|---:|---:|---|---:|
| 0 | 192 | 57 (31 optimal, 26 unknown) | 31 | 197, 198, 197, 197, 197, 197 | 0 |
| 1 | 256 | 50 (25 optimal, 25 unknown) | 25 | 259, 261, 261, 261, 258, 261 | 0 |
| 2 | 320 | 5 (1 optimal, 4 unknown) | 1 | 320, 321, 320, 320, 320, 320 | 0 |

Exact least-escape sequences:

| Cell | Round 0 | Round 1 | Round 2 |
|---|---|---|---|
| `0_0` | 3, 27, 31, 57, 61 | 3, 7, 13 | none |
| `0_1` | 5, 13, 25, 29, 35, 41 | 23, 25, 31, 35, 47 | 29 |
| `0_2` | 29, 47, 71, 75, 87 | 3, 11, 15, 23, 29 | none |
| `1_0` | 6, 32, 38, 48, 54 | 6, 24, 26, 32, 44 | none |
| `1_1` | 6, 22, 28, 46, 48 | 6, 16 | none |
| `1_2` | 22, 44, 46, 56, 62 | 8, 20, 22, 40, 44 | none |

Round 0 exactly recovered the six v2.2 first misses
`3,5,29,6,6,22`, confirming the correction's intended first feedback step.
Across all rounds, the 57 records contain 36 distinct escapes ranging only
from 3 to 87. Round 1 did not uniformly advance the first or final escape, and
round 2 produced only one feasible assignment before its caps. Because rounds
are independent and no proposal closed the full active seed, these sequences
are CEGAR diagnostics—not monotone lower bounds, witnesses, or evidence for a
bounded `x<n` claim.

## Scope

This run establishes that the durable least-escape feedback mechanism works
and replays exactly. It also shows that the frozen construction schedule did
not move beyond small cheap-seed escapes or emit a full-seed proposal. It says
nothing about periodic exhaustion, a candidate integer, or A231201 itself.

No issue, pull request, Lean certificate, release, README claim, or other
upstream action follows from this constructor-only DEVELOPMENT run.
