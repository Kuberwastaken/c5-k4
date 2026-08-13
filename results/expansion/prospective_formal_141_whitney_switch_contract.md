# Frozen prospective trial: WOWII #141 unique-triangle Whitney switch

Frozen: 2026-08-13 UTC, before exact candidate evaluation

Source commit: `2bbb48abecce1e67998ca390276b27c267b6a061`

Target: current
`FormalConjectures/WrittenOnTheWallII/GraphConjecture141.lean`

No commit, push, release, issue, PR, or other public action is authorized.

## Pre-existing selection universe

The only selection source is the already completed 1,057-control gate in
`prospective_formal_141_s4_cover_ledger.jsonl` (SHA-256
`b10753f8a3c48c5d4bcf5f0c74fed12c2b4c300f699824989d3e09beb4c27d0a`).
No graph produced by this trial may participate in seed selection.

Filter the distinct pre-existing rows in this order:

1. connected Atlas control, not `complement(C5[K3])`;
2. `R141 = tree - (girth // 2 - 1 + lambda_max) = 1`;
3. girth three, so eliminating all triangles raises the integer girth term;
4. exactly one triangle;
5. `lambda_max = Delta`, so a degree-preserving switch which eliminates all
   triangles is predicted to pin `lambda_max`;
6. minimum `(n,m,graph6)`.

The resulting selection table is:

| seed | graph6 | n | m | girth | lambda_max | Delta | tree | target | R141 | triangles |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| selected: `atlas:EhdW` | `EhdW` | 6 | 8 | 3 | 3 | 3 | 4 | 3 | 1 | 1 |
| excluded earlier order: `atlas:ERUO` | `ERUO` | 6 | 7 | 3 | 3 | 4 | 4 | 3 | 1 | 1 |
| excluded earlier order: `atlas:EhX_` | `EhX_` | 6 | 7 | 3 | 3 | 4 | 4 | 3 | 1 | 2 |

The last two rows document the nearest lower-edge controls; they fail the
pinning or unique-triangle filters.  All displayed invariants are copied or
derived only from the frozen gate row and the seed itself.

## Frozen local transformation

Decode `EhdW` with vertices `0,...,5`.  Its edge set is

```text
01 04 12 15 23 34 35 45.
```

Apply exactly one degree-preserving Whitney 2-switch:

```text
delete 01 and 45;
add    05 and 14.
```

No alternate orientation, second switch, relabelling-based search, seed
replacement, or post-result retuning is allowed.  This is not a graph cover.

The frozen prediction is that deleting `45` destroys the seed's unique
triangle `3-4-5-3`; the two added edges have disjoint endpoint neighborhoods
after deletion, so they create no triangle.  The degree sequence
`(2,2,3,3,3,3)` is unchanged.  Thus the output is predicted to have girth at
least four and, if triangle-free, `lambda_max = Delta = 3`.  The maximum
induced-tree order is predicted to remain four.  Therefore the intended move
is from residual one to the exact #141 wall:

```text
girth: 3 -> 4, lambda_max: 3 -> 3, tree: 4 -> 4,
target: 3 -> 4, R141: 1 -> 0.
```

Any other tuple is still recorded; it falsifies the prediction rather than
authorizing retuning.

## Gate and exact evaluation

Before evaluating the switch, replay all 1,057 controls with the same exact
definitions and witnesses used by the S4 lane.  A negative residual, witness
failure, mismatch against the frozen ledger, or timeout is `GATE_FAIL`.

For the transformed graph, verify simplicity, connectedness, exact edge delta,
degree multiset preservation, the absence/presence of every triangle, exact
girth with a cycle witness, every local-neighborhood independence number with
witnesses, and `lambda_max`.

Use the decision-first tree protocol.  Compute the target, search exactly for
an induced tree of that order, and stop at the first replayed witness.  Exact
maximum-tree optimization is forbidden after a target witness is found.  Only
if the target decision is exhaustively false may descending exact
maximization run.  A negative residual requires an independent replay before
any source/status/novelty work.

Every OS process and every exact phase is capped at 60 seconds, with internal
caps at most 55 seconds.  Ledger rows are append-only and flushed immediately.

Verdicts are `GATE_FAIL`, `HOLD_BOUNDED`, `HOLD_WITH_TIMEOUTS`, and
`CROSSING_VERIFIED`.
