# Method v32: WOWII #19/#13 symmetric center-only residue

## Scope

This rung proves the left-off-path counterpart of v31 and combines both
orientations into one center-only conclusion.

Lean source:
`lean/GraphConjecture19CenterOnlyResidue.lean`

## Symmetric route theorem

The file first proves the edge-transfer lemma with `extraLeft` avoided: any
full-graph edge whose endpoints occur on a walk avoiding `extraLeft` must be a
tree edge.  Otherwise the edge would be the unique added edge and would put
`extraLeft` back on the walk.

For the left-off-path orientation, assume:

- `extraRight = p[j]` is on the geodesic;
- `c = p[k]` is the on-geodesic center;
- `extraLeft` is outside the geodesic;
- `c` is adjacent to `extraLeft`;
- `Nat.dist j k = 2`.

Both index orders are handled explicitly.  The two geodesic edges through the
intermediate vertex and the edge `c-extraLeft` are transferred to the spanning
tree.  They form a simple three-edge tree path between the added-edge
endpoints.  Tree path uniqueness therefore forces the fundamental tree path
to have length three, contradicting the nontriangle lower bound four.

Combining this with v30's symmetric zero-or-two split proves:

```text
left endpoint off-path + fundamental path length >= 4
  -> index(extraRight) = index(c).
```

## Unified center-only conclusion

The final theorem accepts either off-path orientation and proves the graph
level statement

`extraLeft = c or extraRight = c`.

More precisely, when exactly one endpoint is off the geodesic and adjacent to
the on-geodesic center, the other endpoint—the one on the geodesic—is exactly
that center.  All distance-two alternatives have now been eliminated in both
orientations.

## Exact residual

In the nontriangle on-path saturated branch, only two types remain:

1. both endpoints lie on the diametral geodesic at consecutive indices;
2. exactly one endpoint is off the geodesic, and the other endpoint is `c`.

The second is the genuine center case: the unique added edge joins `c` to the
off-path endpoint, which necessarily belongs to `N(c)`.  Path uniqueness does
not contradict this configuration.  Closing it requires the exact
neighborhood saturation or the endpoint-deletion bipartite/charge witness.
That global step is deliberately left separate from this route theorem.

## Verification

The dependency chain through v31 and this file was compiled using the pinned
`formal-conjectures` environment with `-DwarningAsError=true`.  The fresh
target check exited 0 in 7.3 seconds, under the 60-second cap, with no warnings.
No `sorry`, `admit`, `native_decide`, or custom axioms are used.
