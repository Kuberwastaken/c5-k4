# Method v0.36: WOWII 61 realization-cliff surgery

## Outcome

The separately frozen degree-preserving 2-switch trial returns
**`HOLD_BOUNDED`**. Across every tight realization in the 36 exact order-eight
realization-cliff strata, no one-switch neighbor points in the predeclared
descent direction. Consequently, the depth-four directional beam terminates
at radius one for every seed.

This is a negative local-geometry result, not a proof of WOWII 61. It says
that the exact order-eight tight wall has no degree-preserving one-switch move
which increases diameter without increasing maximum induced-forest order, or
which otherwise decreases the conjecture residual.

The addendum was frozen before development evaluation:

- `results/expansion/prospective_wowii61_realization_surgery_addendum.md`;
- `results/expansion/prospective_wowii61_realization_surgery_ledger.jsonl`;
- `scripts/prospective_wowii61_realization_surgery.py`.

No commit, push, issue, PR, release, or other public action was taken.

## Exact gate replay

The surgery evaluator independently replayed the parent trial's 1,030 control
graphs before expanding any seed. It reproduced the residual histogram
exactly:

| residual | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|
| graphs | 159 | 574 | 281 | 10 | 5 | 1 |

The histogram sums to 1,030. There were no negative controls or timeouts.

## Frozen seed universe

The script mechanically reconstructed the 36 cliff strata from the parent's
complete 11,117-row order-eight record. It required a residual range of at
least two and a minimum residual of zero, then selected every tight
realization. The result was 87 fixed seeds:

| seed invariant | value | seeds |
|---|---:|---:|
| diameter | 4 | 87 |
| maximum induced forest | 5 | 74 |
| maximum induced forest | 6 | 13 |

Every seed was exactly recomputed before surgery. Its degree sequence,
Havel--Hakimi residue, diameter, forest order, and residual had to match the
already-written exhaustive record.

## Surgery result

The evaluator generated 2,664 raw legal connected 2-switches. Exact
isomorphism rejection within each seed neighborhood left 843 child classes.
Seventy-three were isomorphic to their seed and were rejected as revisits;
the remaining 770 received new child evaluations:

| child residual | 0 | 1 | 2 |
|---:|---:|---:|---:|
| children | 112 | 381 | 277 |

There were no negative residuals and no timeouts. More sharply, all 87 seeds
returned `NO_ELIGIBLE_MOVE`. Not one child satisfied

```text
forest(child) <= forest(seed)
```

together with either a larger diameter or a smaller residual. Therefore:

- directional residual drops: 0;
- diameter lifts without forest growth: 0;
- retained beam endpoints: 0; and
- maximum reached path depth: 0 (children were evaluated at radius one, but
  none qualified for retention at depth one).

The global 25,000-child budget was not approached; the frozen direction rule
itself exhausted the search after 770 exact children.

## Independent census reconciliation

A separate implementation enumerated the switches without importing the
surgery code, then matched every unique child by exact isomorphism against the
complete order-eight census. It independently recovered all 36 strata, 87
seeds, 2,664 raw switches, 843 unique child classes, and the 73 seed-isomorphic
revisits. Including those revisits, its residual histogram was
`0:185, 1:381, 2:277`; after removing them it exactly reproduced the trial's
`0:112, 1:381, 2:277`. Every child had one census match. It found no negative
or direction-eligible child, including among the seed-isomorphic revisits.

## Interpretation

The realization cliffs are genuine—the same residue can coexist with residual
zero and residual two—but their tight members are local minima under this
specific degree-preserving move geometry. A successful continuation should
not tune this closed family retrospectively. It must freeze a different move
class or apply the already-frozen rule prospectively to a new higher-order
tight stratum.
