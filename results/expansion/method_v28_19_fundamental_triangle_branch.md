# Method v28: WOWII #19/#13 fundamental-triangle branch

## Scope

This is the first cycle-specific exclusion after the geodesic saturation
classification.  It handles the subcase in which both endpoints of the added
edge are assigned to the same maximum-degree open neighborhood.

Lean source:
`lean/GraphConjecture19FundamentalTriangleBranch.lean`

## Certified incidence result

Let `D : TreePlusOneEdge G`, with added edge endpoints `extraLeft` and
`extraRight`.  If a vertex `c` is adjacent in `G` to both endpoints, then:

1. neither adjacency can be the added edge itself without collapsing `c` to
   an endpoint and contradicting looplessness or endpoint distinctness;
2. both adjacencies therefore already belong to the spanning tree;
3. they give a two-edge tree walk from `extraRight` through `c` to
   `extraLeft`;
4. the endpoints are distinct and nonadjacent in the tree, so their tree
   distance is exactly two;
5. uniqueness of paths in the spanning tree forces the canonical fundamental
   tree path to have length exactly two.

Restoring the added edge therefore makes the fundamental cycle a triangle.

The file derives the usable exclusion:

```text
fundamental tree path length >= 4
  -> not (extraLeft in N(c) and extraRight in N(c)).
```

It then feeds this into the on-path saturation classification.  When
`P union N(c) = V` and the fundamental tree path has length at least four, at
least one endpoint of the added edge must lie on the diametral path `P`; the
possibility that saturation assigns both endpoints only to `N(c)` is ruled
out.

For an odd fundamental cycle, the length-at-least-four tree-path hypothesis is
exactly the nontriangle branch (cycle length at least five).

## Exact residual

This does not yet exclude every saturated configuration.  The remaining
branches are:

- the fundamental triangle case;
- in the nontriangle branch, configurations with one or both added-edge
  endpoints on the diametral path;
- the analogous off-path saturation assignments, where an endpoint may also
  equal the maximum-degree vertex `c`.

The next useful incidence rung should exploit the geodesic indices of an
added-edge endpoint on `P`.  The other endpoint is adjacent to it in `G`, so
geodesicity either places it at a consecutive path index or forces it outside
`P`; combining that split with membership in `N(c)` and the width-two/three
neighbor-index window should sharply restrict the residual configurations.

## Verification

The committed/local dependency chain through `GraphConjecture19GeodesicSaturation`
and this file was compiled using the pinned `formal-conjectures` environment
with `-DwarningAsError=true`.  The final target check exited 0 in 8.2 seconds,
under the 60-second cap, with no warnings.  No `sorry`, `admit`,
`native_decide`, or custom axioms are used.
