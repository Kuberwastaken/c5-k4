# Method v30: WOWII #19/#13 off-path endpoint obstruction

## Scope

This rung attacks the one-added-edge-endpoint-off-geodesic alternative from
the v29 nontriangle on-path saturation dichotomy.

Lean source:
`lean/GraphConjecture19OffPathEndpointObstruction.lean`

## Certified local obstruction

Suppose `x` and `c` occur on a shortest path at indices `i` and `k`, while a
vertex `y` is adjacent to both.  Exact subpath distances and the two-edge walk
`x-y-c` prove

`Nat.dist i k <= 2`.

Apply this with `x` the on-path endpoint of the added edge and `y` the other,
off-path endpoint.  Saturation forces `y` into `N(c)`, while the added edge
gives `x-y`.  There are initially three possible index distances:

- zero;
- one;
- two.

Distance one is impossible in the nontriangle branch.  If `x` and `c` were
consecutive, then `c` would be a common neighbor of both added-edge endpoints.
The v28 fundamental-triangle theorem would force the fundamental tree path to
have length two, contradicting the assumed length at least four.

Therefore the exact surviving split is

`i = k` or `Nat.dist i k = 2`.

In graph language, the on-path endpoint is either the maximum-degree center
itself or lies exactly two positions from it along the diametral geodesic.
The file proves both orientations of the added edge.

## Composed saturation theorem

`refined_fundamental_endpoint_dichotomy_of_on_path_saturation` combines:

- the center's actual geodesic index;
- v29's consecutive-on-path versus off-path-neighborhood dichotomy;
- the new zero-or-two obstruction.

Its exhaustive output is symmetric:

1. both endpoints are on the geodesic at consecutive indices; or
2. one endpoint is off-path and in `N(c)`, while the on-path endpoint equals
   `c` or is exactly two geodesic positions from `c`.

No abstract membership implication remains in the off-path branch.

## Exact residual

The nontriangle on-path saturated case is now reduced to three concrete local
geometries:

- the geodesic traverses the added edge between consecutive indices;
- the on-path endpoint is exactly `c`, and the other endpoint is off-path in
  `N(c)`;
- the on-path endpoint is two geodesic steps from `c`, and the other endpoint
  is their common off-path neighbor.

The last configuration gives a four-cycle-shaped pair of length-two routes
between `c` and the on-path endpoint unless their intervening geodesic vertex
coincides with a fundamental-cycle attachment.  The next tree-plus-one-edge
step should split that coincidence and use tree path uniqueness; the
`x = c` configuration instead needs degree/neighborhood saturation or the
endpoint-deletion bipartite witness.  Bipartiteness alone has not been claimed
to exclude either configuration here.

## Verification

The dependency chain through v29 and the new file was compiled with the pinned
`formal-conjectures` Lean environment and `-DwarningAsError=true`.  The fresh
target check exited 0 in 6.5 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
