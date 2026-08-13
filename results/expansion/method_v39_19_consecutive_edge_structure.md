# Method v39: WOWII #19/#13 consecutive added-edge structure

## Scope

This rung attacks the remaining nontriangle geometry in which both added-edge
endpoints occur consecutively on the diametral geodesic.  The branch is not
generically contradictory: a shortest path may genuinely use the unique added
edge.  The file therefore extracts its exact spanning-tree structure and
charge boundary.

Lean source:
`lean/GraphConjecture19ConsecutiveEdgeStructure.lean`

## Exact geodesic structure

Suppose at index `i` the geodesic has

```text
p[i]   = extraLeft
p[i+1] = extraRight.
```

The file proves:

1. the step `p[i]-p[i+1]` is the added edge and is not a tree edge;
2. every other consecutive geodesic step is a tree edge;
3. consequently the prefix ending at `extraLeft` and suffix starting at
   `extraRight` are spanning-tree arms.

For an alleged other non-tree step at index `j`, the decomposition says its
ordered endpoints must equal the added endpoints in one orientation.  Path
index injectivity then forces `j=i`; the reverse orientation would force both
`j=i+1` and `j+1=i`, an arithmetic contradiction.

The complete result is also proved for the reversed placement
`extraRight,extraLeft` by swapping the decomposition endpoints.  Thus in
either orientation the added edge is the geodesic's unique non-tree step.

The fundamental tree path is the unique detour reconnecting the boundary
vertices of these two tree arms.  Replacing the added step by that detour is
not itself a contradiction—it produces a longer walk, which geodesicity
allows.

## Exact charge boundary

Deleting either added-edge endpoint leaves an induced bipartite graph on
`|V|-1` vertices.  The file packages the resulting alternative for every
tree-plus-one-edge graph, and therefore for this consecutive geometry:

```text
WOWII 13 holds
or
localMax(G) = maxDegree(G).
```

If the inequality is strict, the one-unit local-independence discount combines
with endpoint deletion and closes the conjecture.  Hence the only remaining
numeric obstruction is full local independence at maximum degree.

## Exact residual

The nontriangle proof lane now has one geometric/numeric residue:

- a diametral geodesic made from two tree arms joined by the added edge;
- `localMax(G) = maxDegree(G)`, equivalently some maximum-degree vertex has a
  fully independent neighborhood.

The next split should locate that witness relative to the two arms and the
fundamental detour.  If it is an added-edge endpoint, its neighborhood includes
the opposite endpoint and its tree-side attachment; independence restricts
the detour's first edge.  If it lies internally on an arm, all of its geodesic
neighbors are tree neighbors and the full-independent condition constrains
additional branches.

The fundamental-triangle case remains separate, as requested.

## Verification

The local dependency chain and new target were compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
target check exited 0 in 7.2 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
