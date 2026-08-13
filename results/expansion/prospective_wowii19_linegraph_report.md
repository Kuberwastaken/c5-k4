# Prospective WOWII 19 line-graph trial

Date: **2026-08-13 UTC**

Verdict: **INCONCLUSIVE**.

## Frozen question

This trial selected one current DeepMind finite-graph equality wall outside
the exhausted #40, Reed, #61, and #141 lanes.  It tests the exact current
WOWII 19 reading

```text
b(G) >= floor(averageEccentricity(G) + localMax(G))
```

and applies exactly one preregistered operation: take the line graph of each
of the 56 previously serialized #19 equality seeds.  The contract was written
before any line graph was evaluated.  No WoW I statement is involved.

The clean local `google-deepmind/formal-conjectures` checkout used for the
source check was at `9a1636c4030039f70cf78b866c216d8b6c5f35b0`.

## Residual separation

The operation has a clean coordinate interpretation.  The neighborhood of a
vertex of `L(G)` is the union of the two cliques arising from the endpoints of
the represented edge, so

```text
localMax(L(G)) <= 2.
```

Moreover, an induced subgraph of `L(G)` is bipartite exactly when the
corresponding selected-edge subgraph of `G` has maximum degree at most two and
contains no odd cycle.  Thus `b(L(G))` becomes a maximum even-linear edge rank,
while average eccentricity remains the independently moving edge-incidence
metric.  This was the frozen prospective reason for the transformation.

## Database gate

The source-faithful gate completed before development evaluation:

| set | rows | crossings | timeouts |
|---|---:|---:|---:|
| connected Graph Atlas, orders 2--7 | 995 | 0 | 0 |
| frozen named controls | 28 | 0 | 0 |
| **total** | **1,023** | **0** | **0** |

There were 612 equality controls.  The gate status is `PASS`.

## Frozen-scope result

The 56 seed rows yield 49 distinct transformed isomorphism classes of order at
most 60.  One transformed graph has order 75 and receives the contract's
predeclared `OUT_OF_SCOPE` classification.

Of the 49 in-scope classes:

- 39 were solved exactly;
- 10 retained unresolved exact `b(L(G))` optimizations under the unchanged
  cap;
- none of the 39 completed rows crossed;
- five completed rows remained tight.

The completed residual histogram is

```text
R19: 0  1  2  3  4  5
rows: 5  8 11  5  8  2
```

The five exact wall outputs are recorded with graph6 strings and witnesses in
the ledger.  Four have coordinates `(average eccentricity, localMax, b) =
(2,2,4)`; the fifth has `(25/8,2,5)`.

The initial deterministic process reached its global cap after serializing a
prefix.  The remainder was processed in deterministic index checkpoints under
fresh 60-second process caps.  `skip` in those checkpoint summaries means
"already serialized in an earlier prefix," not exclusion from the frozen
scope.  All 49 in-scope names are accounted for exactly once.  Solver
semantics, bounds, ordering, and the transformation were unchanged.

## Independent audit

Every one of the 39 completed rows passed a second exact audit with zero
mismatches and zero audit timeouts.  The audit did not reuse the primary
retained-vertex formulation.  It reconstructed the original seed and solved
directly over its edges:

- selected degree at every seed vertex is at most two;
- selected endpoints receive opposite binary colors;
- the number of selected seed edges is maximized.

This independently recomputes `b(L(G))`.  Separate all-pairs distances and
neighborhood-independent-set calculations reproduced the metric, local, RHS,
and residual coordinates.  Explicit selected-edge witnesses are appended for
all completed rows.

## Strict interpretation

The frozen line-graph move produced substantial exact safe-side and equality
evidence, but ten in-scope rows are unresolved.  A timeout is an unknown
bracket, not a hold.  Therefore the only protocol-valid outcome is
`INCONCLUSIVE`, not `HOLD_BOUNDED`.

No adaptive family expansion, cap extension, commit, push, release, issue,
PR, novelty claim, or public action was made.
