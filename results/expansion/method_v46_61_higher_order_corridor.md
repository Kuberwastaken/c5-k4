# Method v0.46: WOWII 61 higher-order neutral corridor

## Outcome and protocol correction

The literal-contract replay of the separately frozen order-twelve trial
returns **`NEUTRAL_CORRIDOR` with zero crossings**. Starting from the new tight
realization at manifest index 623, degree-preserving 2-switches produce a
genuine neutral corridor of length two, but no endpoint raises the diameter
above four without increasing the maximum induced forest. The corridor closes
completely at the third layer.

The initial execution is retained but classified
**`INCONCLUSIVE_PROTOCOL_DEVIATION`**, not `HOLD_BOUNDED`. An independent audit
found that it rejected graphs isomorphic to *any previously evaluated* class,
whereas the frozen contract rejects only graphs isomorphic to a previously
*retained* class. It also selected the broad `HOLD_BOUNDED` label even though a
depth-two endpoint met the more specific frozen `NEUTRAL_CORRIDOR` definition.

The evaluator was corrected to the literal frozen semantics and replayed into
separate artifacts. No construction, ranking, depth, beam, switch cap, seed,
or invariant rule was retuned after observing the result. Both executions have
zero crossings; only the literal replay is protocol-exact.

This differs from the completed order-eight experiment: there, no tight seed
had even one direction-eligible switch. Here, two neutral first steps and one
neutral second step survive, but the extra freedom still does not reach the
next ceiling at diameter seven.

This is a bounded negative result, not a proof of WOWII 61 and not a novelty
claim. No issue, PR, release, commit, push, or other public action was taken by
the trial.

The frozen artifacts are:

- `results/expansion/prospective_wowii61_higher_order_corridor_contract.md`;
- `results/expansion/prospective_wowii61_higher_order_corridor_ledger.jsonl`;
- `results/expansion/prospective_wowii61_higher_order_corridor_records.jsonl`;
- `results/expansion/prospective_wowii61_higher_order_corridor_literal_ledger.jsonl`;
- `results/expansion/prospective_wowii61_higher_order_corridor_literal_records.jsonl`;
- `scripts/prospective_wowii61_higher_order_corridor.py`.

## Fixed source and seed

The target remained current DeepMind WOWII 61 at upstream commit
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`:

```text
largestInducedForestSize(G)
  >= residue(G) + ceil(diameter(G)/3).
```

The only seed was frozen before development evaluation:

| field | exact value |
|---|---|
| manifest index | 623 |
| graph6 | `K^qA@A?_A?G?` |
| degree sequence | `[6,6,4,3,2,1,1,1,1,1,1,1]` |
| residue | 8 |
| diameter | 4 |
| maximum induced forest | 10 |
| residual | `10 - 8 - ceil(4/3) = 0` |

The evaluator recomputed the complete Havel--Hakimi trajectory

```text
[6,6,4,3,2,1,1,1,1,1,1,1]
-> [5,3,2,1,1,1,1,1,1,0,0]
-> [2,1,1,1,1,0,0,0,0,0]
-> [1,1,0,0,0,0,0,0,0]
-> [0,0,0,0,0,0,0,0]
```

and reproduced the stored maximum-forest witness
`{0,1,2,5,6,7,8,9,10,11}`. Decreasing-cardinality exhaustive subset search
rejects all twelve order-eleven induced subgraphs and the full vertex set, so the
forest value is exact rather than merely a lower bound.

## Database sanity came first

Before any switch was evaluated, the new lane replayed the same 1,030 exact
controls and reproduced the established residual histogram:

| residual | 0 | 1 | 2 | 3 | 4 | 5 |
|---:|---:|---:|---:|---:|---:|---:|
| graphs | 159 | 574 | 281 | 10 | 5 | 1 |

There were no negative controls or timeouts.

## Frozen operation

The trial allowed neutral degree-preserving 2-switch paths rather than
demanding an immediate improvement. A child could continue exactly when its
maximum induced forest stayed at most ten and its diameter stayed at least
four. The prospective crossing target was diameter at least seven with forest
at most ten; since the degree sequence fixes residue at eight, that would give
residual at most `10 - 8 - 3 = -1`.

The frozen bounds were depth eight, beam width 32, 128 lexicographically
ordered legal connected switches per parent, and 8,000 exact child
evaluations. None of these resource bounds became active: every layer was
exhausted before its cap.

## Literal-contract path census

| depth | parents | raw switches | new exact children | eligible | retained |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 39 | 6 | 2 | 2 |
| 2 | 2 | 67 | 11 | 1 | 1 |
| 3 | 1 | 30 | 4 | 0 | 0 |

The difference between raw switches and exact children is caused by
isomorphic duplicates and revisits. In total the literal replay generated 136
legal connected switches, exactly evaluated 21 layer-local classes, and
retained three corridor endpoints. There were no timeouts. An unretained class
may be evaluated again at a later depth under the literal contract; only
retained classes enter the cross-depth global seen set.

All three retained endpoints have residue eight, diameter four, maximum
induced forest ten, and residual zero:

| depth | graph6 | path status |
|---:|---|---|
| 1 | `KniA@A?_A?G?` | neutral |
| 1 | `K~Q?PA?_A?G?` | neutral |
| 2 | `K~IA?Q?_A?G?` | neutral |

At the third layer, four layer-local classes were evaluated. Three have
residual one and one has residual two; none is corridor-eligible. The frontier
is therefore empty and depths four through eight are unreachable under the
frozen corridor rule.

Across all 21 exact child evaluations, the best residual remained zero and the largest
diameter remained four. There was no `CEILING_APPROACH`, since no child reached
diameter five or six, and no candidate crossing.

## Audit reconciliation

The independent implementation exactly reproduced the fixed seed, complete
Havel--Hakimi trajectory, residue, diameter, maximum induced forest, all three
retained graph6 endpoints, their paths and witnesses, and the 136 raw-switch
census. Under literal retained-only semantics it independently predicted the
corrected depth counts `6, 11, 4`, matching the replay. Under the initial
evaluated-global-seen implementation it predicted `6, 7, 1`, matching the
preserved original run. This isolates the discrepancy to seen-set semantics;
it does not affect either run's zero-crossing result.

## Interpretation

The new order-twelve cliff does supply more local freedom than the order-eight
cliffs: immediate improvement is absent, but a short plateau exists. The
plateau nevertheless forms a closed component under the no-forest-
compensation rule. This is useful falsification of a specific proposed move,
not a reason to tune the same operation after observing its failure.

A future prospective lane should freeze a structurally different operation—
for example, a paired switch treated as one atomic surgery, or a transfer to a
new degree-sequence stratum—before testing it. The completed neutral-corridor
family should remain closed.
