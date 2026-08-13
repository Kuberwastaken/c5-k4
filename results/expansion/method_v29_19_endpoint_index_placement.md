# Method v29: WOWII #19 endpoint index placement

## Scope

This rung refines the nontriangle on-path saturation branch from v28.  It
assigns actual geodesic indices to the added-edge endpoints and turns the
remaining endpoint placement into an exhaustive indexed dichotomy.

Lean source:
`lean/GraphConjecture19EndpointIndexPlacement.lean`

## Certified metric lemma

For a shortest walk `p`, the exact subpath metric gives

`dist(p[i], p[j]) = Nat.dist i j`.

Consequently, if `p[i]` and `p[j]` are adjacent, then

`Nat.dist i j = 1`.

The file packages both the direct indexed statement and a support-level
version: any two adjacent vertices in the support of a geodesic admit path
indices at natural distance one.

## Certified nontriangle saturation dichotomy

Let `P` be the support of a shortest path `p`, let `N = N(c)`, and assume

- `P union N = V`;
- every fundamental tree path between the endpoints of the added edge has
  length at least four (the fundamental-cycle-length-at-least-five branch).

Then v28 first forces at least one added-edge endpoint onto `P`.  The new
theorem proves that, after choosing such an endpoint and its path index,
exactly the following exhaustive alternatives remain:

1. the other endpoint is also on `P`, and its index is consecutive to the
   first endpoint's index; or
2. the other endpoint is genuinely outside `P`, and saturation forces it into
   `N(c)`.

The theorem is symmetric in the two added-edge endpoints and returns either
orientation explicitly.

This is a real narrowing.  The earlier endpoint classification only said that
each endpoint belongs to `P` or `N`; it did not distinguish overlap, prove
off-path membership in the neighborhood, or constrain two on-path endpoints
to consecutive positions.

## Exact residual

The both-on-path consecutive case cannot be discarded generically: a
diametral geodesic may genuinely traverse the unique added edge.  The next
cycle-specific step must therefore analyze two residual geometries:

- **consecutive on-path:** cut the geodesic at the added edge and compare its
  two sides with the long fundamental tree detour;
- **one endpoint off-path in `N(c)`:** use that `c` is itself on the geodesic
  in the actual on-path branch, assign an index to `c`, and combine the
  endpoint--center adjacency with the at-most-two path-neighbor positions of
  `c`.

Any eventual exclusion needs the odd parity/length of the fundamental detour
or diametrality beyond the local adjacency fact; geodesicity alone correctly
permits the consecutive case.

## Verification

The local dependency and the new target were compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
target check exited 0 in 6.8 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
