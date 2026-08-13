# Method v36: WOWII #19/#13 center tree attachment

## Scope

This bounded rung identifies the spanning-tree attachment of the off-path
added-edge endpoint in the center-attained branch.  It does not yet claim
uniqueness of that attachment.

Lean source:
`lean/GraphConjecture19CenterTreeAttachment.lean`

## Certified fundamental attachment

Retain the v35 hypotheses in the orientation `extraLeft = c`:

- `extraRight` is outside the geodesic vertex set `P`;
- `P union N(c) = V`;
- `N(c)` is independent.

Take any spanning-tree path from `extraRight` to `extraLeft`.  The file proves
that its first vertex after `extraRight`, namely `q.snd`, satisfies:

- `q.snd` lies in `P`;
- `q.snd != c`;
- `extraRight-q.snd` is a tree edge.

The proof is exact:

1. the tree path is nonempty because the added-edge endpoints are distinct;
2. its first edge supplies the tree adjacency;
3. the first vertex cannot be `c`, since `c-extraRight` is precisely absent
   from the spanning tree;
4. saturation places the first vertex in `P` or `N(c)`;
5. the `N(c)` alternative contradicts independence, because `extraRight` is
   itself in `N(c)` and is adjacent to that first vertex.

Therefore `extraRight` has a genuine tree attachment to a noncenter geodesic
vertex.  This is also packaged in existential form.

## Carrier split

Combining with v35 gives:

- every ordinary off-path vertex `z != extraRight` has the tree edge `c-z`;
- `extraRight` instead has the added edge `c-extraRight` and a certified tree
  edge to a noncenter vertex of `P`.

This separates the unique-cycle carrier from the other independent off-path
vertices at the level of actual tree edges.

## Exact residual

Two requested uniqueness consequences remain:

1. an ordinary off-path vertex cannot also attach to a noncenter geodesic
   vertex;
2. `extraRight` has only one tree attachment to `P`.

Both reduce to the same missing representation bridge: reinterpret the
geodesic subpath from `c` to a proposed attachment vertex as a spanning-tree
path.  All of its edges are tree edges because its support avoids
`extraRight`.  Tree path uniqueness can then compare it with the route through
the off-path vertex and force that vertex onto the geodesic, a contradiction.

The current mathlib `Walk.mapLe` only maps from a subgraph to a supergraph, so
the reverse reinterpretation needs a small recursive walk constructor or a
subgraph walk-lifting lemma.  This rung supplies the endpoint and membership
facts that constructor will consume.  No degree/charge conclusion is claimed
before uniqueness is certified.

## Verification

The local dependency chain and new target were compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
target check exited 0 in 6.6 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
