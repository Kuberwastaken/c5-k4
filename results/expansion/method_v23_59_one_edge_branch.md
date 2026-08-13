# Method v23: WOWII #59 one-edge branch boundary

Date: 2026-08-13

Local certificate: `lean/GraphConjecture59OneEdgeBranch.lean`

## Outcome

The one-edge outside-triple branch does not feed the v21 seven-vertex
bipartite builder. It has an exact local obstruction: the outside edge and
either aligned core form a triangle.

Lean now proves the sharp replacement under the v21 hypotheses:

```text
b(G) >= 6,
the full aligned seven-set is not bipartite.
```

The six-set is constructive. Delete one endpoint of the unique outside edge
and retain both aligned cores, the other two outside vertices, and both
extensions. The inherited coloring is

```text
color 0: a,b,q
color 1: retained outside pair,p.
```

All within-color pairs are nonedges. Hence the induced six-set is bipartite.

## Exact obstruction

The obstruction is only one outside edge. Regardless of its labeled position
among `xy`, `xz`, and `yz`, it makes a triangle with aligned core `a`, so no
proper two-coloring of the full seven-set exists. Deleting a suitable edge
endpoint restores a proper six-vertex coloring.

Thus the currently available local data do not yield `b>=7` in this branch;
they lose exactly one vertex from the fixed builder. No claim of `f>=5` is
made: a separate core exchange or forest construction needs additional
adjacency control.

## Formal contents

The module provides:

1. `PairwiseDistinctSix` and `SixSideCompatible`;
2. the explicit six-vertex coloring theorem;
3. the induced-bipartite invariant bound `b(G)>=6`;
4. the triangle obstruction for the full aligned seven-set;
5. `oneEdge_branch_exact_boundary` for all three labeled realizations.

## Scope

WOWII #59 is already externally disproved. This is theorem extraction, not a
new counterexample or release result.

## Lean audit

The complete local chain from `GraphConjecture40Baseline` through the v22
independent branch was rebuilt into a fresh temporary directory, with warnings
promoted to errors and every process capped at 60 seconds. The v19
synchronization branch was also rebuilt. Every module passed. The final target
check completed in 8.33 seconds with exit code zero and no warnings. The file
contains no proof holes, native computation, or custom axioms.

## Next bridge

The next useful datum must break the six-vertex plateau. Candidates are an
extra vertex compatible with the restored six coloring, or an adjacency
restriction allowing the isolated outside vertex to enter a five-vertex
induced forest after a core exchange.
