# Method v27: WOWII #19/#13 geodesic saturation bridge

## Scope

This rung connects the abstract equality-case saturation lemmas to the actual
objects used in the diameter--degree argument: a diametral shortest path and
the open neighborhood of a maximum-degree vertex.  It then feeds the resulting
saturation directly into the canonical tree-plus-one-edge endpoint
classification.

Lean source:
`lean/GraphConjecture19GeodesicSaturation.lean`

## Certified theorem

For a finite nonempty connected graph `G`, a `TreePlusOneEdge G`
decomposition `D`, and the extremal equality

`G.diam + G.maxDegree = |V| + 1`,

the theorem `extremal_diametral_geodesic_classification` selects:

- a maximum-degree vertex `c`;
- diametral endpoints `u,v`;
- a shortest path `p : G.Walk u v` of length `G.diam`.

Writing `P = p.support.toFinset` and `N = G.neighborFinset c`, it proves the
following exhaustive alternative.

1. If `c` is on `P`, then

   - `|P intersect N| = 2`;
   - `P union N = V`;
   - each endpoint of the added edge lies in `P` or `N`.

2. If `c` is off `P`, then

   - `|P intersect N| = 3`;
   - `{c} union P union N = V`;
   - each endpoint of the added edge equals `c` or lies in `P` or `N`.

The path-neighborhood bounds are not new assumptions.  They are instantiated
from the already certified `diametralNeighborhoodIntersectionBound`: a vertex
on a shortest path has at most two path neighbors, while an off-path vertex
has at most three.  Path support cardinality comes from path nodupness and
`length_support`; neighborhood cardinality comes from the selected
maximum-degree vertex.

## Exact residual

All generic metric selection, intersection counting, finite-set saturation,
and added-edge endpoint classification are now composed in one theorem.  The
remaining step is specifically unicyclic incidence geometry:

- use the fundamental tree path between `D.extraRight` and `D.extraLeft`;
- combine its unique-cycle role with the classified placements of both added
  edge endpoints;
- rule out the saturated on-path and off-path alternatives for the required
  odd-unicyclic class, or explicitly extract a vertex outside the saturated
  cover.

Thus no abstract `P,N`, maximum-degree selection, diametral-path selection, or
`<=2`/`<=3` intersection bridge remains downstream.

## Verification

Using the pinned `formal-conjectures` Lean environment and adding the carrier
Lean directory to the module path, the full local dependency chain and the new
file were compiled with `-DwarningAsError=true`.  The final fresh chain exited
0 with no warnings; every subprocess was capped at 60 seconds.  No `sorry`,
`admit`, `native_decide`, or custom axioms are used.
