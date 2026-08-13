# WOWII 61 realization-cliff voltage-flip trial

Date: **2026-08-13 UTC**

Final status: **BOUNDED_HOLD at the tight-source gate**

## Independent 36-stratum analysis

Regrouping the complete 11,117-graph order-eight ledger reproduced exactly 36
degree-sequence strata with minimum `R61=0` and residual spread at least two.
Their tight realizations have a rigid common profile:

- all 36 have diameter 4 and `ceil(diameter/3)=2`;
- 31 have `residue=3`, forest 5, and feedback-vertex number 3;
- 5 have `residue=4`, forest 6, and feedback-vertex number 2.

Thus every cliff-tight realization satisfies `forest = residue + 2`. The
counterexample move would have to preserve that forest lock while pushing the
diameter to at least 7.

## Frozen transformation

The selected base was the exact tight graph `G?aN]w`:

`degree sequence = (5,5,4,4,4,2,1,1)`, `residue=3`, `diameter=4`, `forest=5`.

Its 13 edges give cycle rank 6. After fixing voltage zero on a deterministic
BFS spanning tree, all 64 canonical two-lift voltage classes were exhausted.
The zero assignment is disconnected; all 63 nonzero assignments are connected.
A one-cotree-edge voltage flip was the only allowed prospective move.

## Exact outcome

All connected lifts share the duplicated degree sequence

`(5,5,5,5,4,4,4,4,4,4,2,2,1,1,1,1)`

and Havel--Hakimi residue 5. Their exact profiles are:

| Quantity | Distribution |
|---|---|
| diameter | 5: 50 lifts; 6: 13 lifts |
| `ceil(diameter/3)` | 2: all 63 lifts |
| largest induced forest | 11: 25 lifts; 12: 38 lifts |
| residual `R61` | 4: 25 lifts; 5: 38 lifts |

No connected lift is tight. Therefore the frozen transformation has no
admissible tight source, no ceiling-raising edge from a tight source, and no
crossing pair.

## Independent verification

Assignment 1, the lexicographically first residual-four lift, has graph6
`O????A?OC@GAiITDQTBAg`. A separate minimum-feedback-vertex-set enumeration
checked 2,568 deletion sets and found the minimum set `{0,1,2,8,9}`. Hence its
maximum induced forest has order `16-5=11`. Independent Havel--Hakimi replay
gave residue 5, and an independent diameter computation gave diameter 6, so

`R61 = 11 - 5 - ceil(6/3) = 4`.

## Obstruction exposed

The lift preserves the degree sequence across voltage assignments, but it does
not preserve the base's extremal balance. Duplicating the base changes residue
from 3 to 5 and raises the induced forest from 5 to at least 11, while the
diameter reaches only 6 and never crosses the next ceiling at 7. The forest
gains six vertices against only two units of residue gain and zero ceiling
gain.

This rules out canonical two-lift voltage navigation for this representative
cliff. A future move needs a gadget whose new vertices are forced into the
feedback set nearly one-for-one; ordinary covers leave too many vertices
available to induced forests.

All 64 classes and Hamming-one relations were exhausted under the frozen
contract. Every subprocess was capped at 60 seconds. No commit, push, release,
issue, PR, or public action was made.
