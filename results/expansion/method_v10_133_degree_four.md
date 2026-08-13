# Method v0.10: WOWII 133 degree-four extension barrier

Date: 2026-08-13

Local certificate: `lean/GraphConjecture133DegreeFour.lean`

## Exact target

For a C4-free, triangle-free, 4-regular graph, the local invariant is exactly
`l(G)=4`.  The new theorem
`sourceConclusion_iff_radius_add_four_le_path` verifies that WOWII 133 is
equivalent on this stratum to

```text
radius(G) + 4 <= path(G).
```

The v0.10 work does not claim this remaining wall is proved or false.

## Why the naive multi-neighbor prepend fails

A radius geodesic begins `u,x1,...`.  Four-regularity leaves three neighbors
of `u` other than `x1`.  It is tempting to place all three before the geodesic
and count four additional vertices.

That cannot be a path.  Triangle-freeness makes every two distinct neighbors
`a,b` of `u` nonadjacent, whereas the proposed list prefix `[a,b,u]` requires
`a` and `b` to be adjacent because they are consecutive.  The theorem
`siblingPrepend_not_inducedPath` formalizes this contradiction directly in
the repository's exact list-based `isInducedPath` representation.

This is stronger than one failed ordering: **any** ordering of two distinct
off-direction siblings fails at its first sibling-sibling step.  The three
available neighbors form a star around `u`, not a path extension.

## Strongest unconditional surviving rung

The local hypotheses do guarantee one clean extra vertex.  The Lean proof
establishes:

1. a connected triangle-free 4-regular graph has radius at least two;
2. an off-direction neighbor exists at a radius-geodesic head;
3. triangle-freeness prevents its adjacency to the geodesic's second vertex;
4. C4-freeness plus shortestness prevents contact with the rest of the tail;
5. prepending it yields an induced path of size `radius+2`.

Thus

```text
radius(G) + 2 <= path(G)
```

is formally certified by
`radius_add_two_le_path_of_fourRegular_triangleFree_c4Free`.

This leaves an exact two-vertex deficit relative to the degree-four target.
Merely counting all off-neighbors cannot close it, because those vertices are
pairwise nonadjacent.  A successful proof needs depth rather than breadth:
for example, a clean length-three handle attached to one geodesic endpoint,
or compatible extensions at both endpoints plus one further clean vertex.
Those deeper contacts are not controlled by triangle- and C4-freeness alone
through the present local argument.

## Lean audit

The file contains no proof holes or custom axioms.  It was checked with its
local dependencies and warnings promoted to errors:

```text
LEAN_PATH=/tmp/c5k4-133-degree-four:/tmp/c5k4-133-regular:\
/tmp/c5k4-133-specialization:/tmp/c5k4-133-v07-check \
  timeout 60s lake env lean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133DegreeFour.lean
```

Result: exit code 0 in 7.0 seconds.

This is an obstruction and partial-theorem checkpoint, not a resolution of
WOWII 133 and not a counterexample release candidate.
