# Method v37: WOWII #19/#13 reverse walk lift and attachment uniqueness

## Scope

This rung builds the missing local supergraph-to-subgraph walk lift and uses it
to finish the requested attachment-uniqueness consequences in the
center-attained orientation.

Lean source:
`lean/GraphConjecture19ReverseWalkLift.lean`

## Reverse walk lift

Mathlib's `Walk.mapLe` maps a walk from a subgraph into a supergraph.  Here the
needed direction is local and reversed: a walk lives in `G`, but every edge
appearing in that particular walk is certified to belong to the spanning tree
`T`.

The file defines `liftWalkEdges` recursively on the walk.  At each cons step,
the head edge's membership in `T.edgeSet` supplies the required tree
adjacency, and recursion lifts the tail.

The following facts are certified:

- lifted support equals the original support;
- lifted length equals the original length;
- pathhood transfers because the support list is unchanged.

For `TreePlusOneEdge`, every edge of a walk whose support avoids `extraRight`
is automatically a tree edge.  Otherwise the edge decomposition would put
`extraRight` back into the support.  Hence every such walk has a canonical
tree lift with the same support and length.

## Generic tree attachment lemma

The file proves that a vertex outside a simple path in an acyclic graph cannot
be adjacent to two distinct vertices of that path.

The proof constructs two paths from the original path's initial vertex to the
external vertex, using `takeUntil` at the two attachment points and then
concatenating the corresponding final edge.  Tree path uniqueness makes the
two paths equal.  Support comparison forces each attachment point to precede
the other on the original path, contradicting the `takeUntil` ordering lemma.

## Center-branch consequences

Apply the reverse lift to the diametral geodesic, whose support avoids
`extraRight`.

1. **Ordinary off-path vertices are leaves at the center.**  V35 already
   showed that every neighbor other than `c` would be a tree attachment to the
   geodesic.  The generic two-attachment lemma, using the tree edge `c-z`, now
   excludes every such attachment.  Thus for every ordinary off-path
   `z != extraRight`,

   `G.Adj z x -> x = c`.

2. **The fundamental endpoint has a unique tree neighbor.**  Any tree neighbor
   of `extraRight` is forced onto the lifted geodesic.  Two distinct tree
   neighbors would violate the same external two-attachment lemma.  Therefore
   all tree neighbors of `extraRight` coincide.

V36 already certified existence of a tree neighbor on `P`, so together the
results identify a unique noncenter geodesic attachment of `extraRight`.  The
fundamental cycle is therefore carried by the added edge `c-extraRight`, that
unique attachment, and the unique tree path back to `c`.

## Exact residual

The center-attained geometry is now a rigid unicyclic form:

- all off-path vertices other than `extraRight` are leaves at `c`;
- `extraRight` has the added edge to `c` and exactly one tree attachment to
  the geodesic;
- every geodesic edge lies in the spanning tree.

The next charge step can count these center leaves against `degree(c)` and
identify the fundamental-cycle attachment index.  Oddness constrains the
parity of the tree path from the attachment back to `c`; diametrality must then
be compared with the two directions through that cycle.  The separate branch
where the geodesic itself traverses the added edge remains untouched.

## Verification

The local dependency chain and new target were compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
target check exited 0 in 8.2 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
