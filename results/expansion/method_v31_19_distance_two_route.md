# Method v31: WOWII #19/#13 distance-two tree route

## Scope

This rung eliminates one orientation of the distance-two alternate-route
residue from v30 and thereby isolates the center case in that orientation.

Lean source:
`lean/GraphConjecture19DistanceTwoRoute.lean`

## Certified tree-edge transfer

In a `TreePlusOneEdge` decomposition, suppose both endpoints of a full-graph
edge occur on a walk whose support avoids `extraRight`.  The edge cannot be the
unique added edge, because either orientation of that alternative would put
`extraRight` on the walk.  Therefore the edge already belongs to the spanning
tree.

This small lemma is the bridge that turns a geodesic segment in `G` into a
tree route once the off-path endpoint is known.

## Certified distance-two exclusion

Consider the orientation where:

- `extraLeft = p[i]` lies on the geodesic;
- the center is `c = p[k]`;
- `extraRight` is outside the geodesic support;
- `c` is adjacent to `extraRight`;
- `Nat.dist i k = 2`.

Let `m` be the unique intermediate geodesic vertex, treating both possible
index orders separately.  The file proves:

1. the two geodesic edges between `extraLeft`, `m`, and `c` are tree edges,
   because all their endpoints lie on the geodesic avoiding `extraRight`;
2. `c-extraRight` is also a tree edge—the added-edge alternative either makes
   `c = extraLeft`, contradicting index distance two, or puts `extraRight` on
   the geodesic;
3. these three edges form a simple tree path from `extraRight` to
   `extraLeft`;
4. tree path uniqueness forces every fundamental tree path to equal this path
   and hence have length three.

Therefore `Nat.dist i k = 2` is impossible when all fundamental tree paths
have length at least four.

Combining this result with v30's exact zero-or-two split proves:

```text
right endpoint off-path + nontriangle fundamental cycle
  -> index(extraLeft) = index(c).
```

Thus the on-path endpoint is exactly the maximum-degree center in this
orientation.

## Exact residual

The right-off-path orientation is reduced completely to the center case.  The
remaining work is:

- prove or instantiate the symmetric left-off-path route theorem;
- analyze the center configuration, where the added edge itself joins `c` to
  the off-path endpoint in `N(c)`;
- retain the separate branch where both added-edge endpoints lie on the
  geodesic at consecutive indices.

The center configuration is not contradicted by tree path uniqueness alone.
It should next be combined with exact neighborhood saturation and the
endpoint-deleted bipartite witness/charge argument.

## Verification

The dependency chain through v30 and the new target was compiled using the
pinned `formal-conjectures` environment with `-DwarningAsError=true`.  The
fresh target check exited 0 in 7.0 seconds, under the 60-second cap, with no
warnings.  No `sorry`, `admit`, `native_decide`, or custom axioms are used.
