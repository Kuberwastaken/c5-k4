# Method v33: WOWII #19/#13 center-endpoint charge

## Scope

This rung applies the endpoint-deletion bipartite charge to the center-only
off-geodesic residue from v32 and identifies the exact remaining local
obstruction.

Lean source:
`lean/GraphConjecture19CenterCharge.lean`

## Symmetric endpoint deletion

The original decomposition package certified that deleting `extraLeft` leaves
an induced graph contained in the spanning tree.  This file proves the missing
right-endpoint version:

- deleting `extraRight` removes every possible occurrence of the unique added
  edge;
- the remaining induced graph is contained in the spanning tree;
- it is therefore acyclic and bipartite.

Consequently, if the center `c` equals either added-edge endpoint, deleting
`c` leaves an induced bipartite graph.  This immediately certifies the exact
witness

`b(G) >= |V| - 1`.

## Charge dichotomy

The existing one-transversal charge theorem proves WOWII 13 whenever

`localMax(G) < maxDegree(G)`.

The new center theorem packages the endpoint deletion and proves the exact
alternative

```text
WOWII 13 holds
or
localMax(G) = maxDegree(G).
```

This uses no additional diameter-degree slack.  The center endpoint itself is
the one-vertex odd-cycle transversal, and the strict local-independence
discount supplies precisely the missing unit.

The equality alternative is further converted into a structural witness:
there exists a vertex `v` such that

- `degree(v) = maxDegree(G)`;
- `indepNeighborsCard(G,v) = degree(v)`.

Thus failure of the charge route requires a maximum-degree vertex whose local
neighborhood independence number consumes its entire degree.  Equivalently at
the invariant level, no local-independence discount exists anywhere that can
beat the maximum-degree equality.

## Exact residual

For the center-to-off-path added-edge geometry, WOWII is now proved except for
the full-independent-maximum-neighborhood obstruction above.  Closing that
obstruction requires one of:

- show that every maximum-degree neighborhood cannot be fully independent in
  the saturated nontriangle unicyclic geometry;
- use a maximum-degree witness distinct from `c` and the exact path/neighborhood
  cover to obtain another induced bipartite vertex beyond the `n-1` deletion
  witness;
- combine the obstruction with the other remaining geometry, where the
  geodesic traverses the added edge consecutively.

The current file deliberately does not assert that the center configuration
is impossible: its endpoint-deletion charge is sufficient in the strict case,
and equality is the honest remaining boundary.

## Verification

The local dependency chain and new target were compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
target check exited 0 in 7.7 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
