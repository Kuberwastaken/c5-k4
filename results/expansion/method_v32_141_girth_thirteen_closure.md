# Method v0.32: unconditional WOWII #141 closure through girth thirteen

Date: 2026-08-13
Status: original conjecture closed for every connected graph of girth at most thirteen

## Result

[`lean/GraphConjecture141GirthThirteenClosure.lean`](../../lean/GraphConjecture141GirthThirteenClosure.lean)
turns the v0.31 distance-five theorem into the next induced-tree certificate.
It proves WOWII #141 unconditionally for girth twelve and thirteen and exports
`conjecture141_of_girth_le_thirteen` for the complete range through thirteen.

## Five-edge prefix

A shortest path of length at least five from a maximum local-independence
center supplies

```text
v -- u -- x -- y -- z -- t.
```

`FiveEdgePrefix` packages the existing chordless `FourEdgePrefix` on
`v-u-x-y-z`, the final edge `z-t`, distinctness of `t`, and all shortcuts from
`t` to `v,u,x,y` excluded by geodesic minimality.

## Explicit three-tail and fourth leaf

The representation layer rebuilds the earlier star and three-tail certificate
with explicit structure literals.  This avoids depending on reduction through
proof-recursive tactic definitions and makes the retained vertices
definitionally visible:

```text
N(v) together with v, x, y, z.
```

The last endpoint `t` is already nonadjacent to `v,x,y` by shortestness.  If
it had a neighbor `a` in `N(v)`, then

```text
v -- u -- x -- y -- z -- t -- a -- v
```

would be a simple seven-cycle.  Girth at least twelve excludes this, so `t`
is adjacent to exactly `z` in the retained induced graph.

`FourthLeafData` and `fourthLeaf_inducedTree` give a reusable one-leaf
extension of an arbitrary verified three-tail tree.  The resulting induced
tree has exactly

```text
maximum local independence + 5
```

vertices.  Since `girth / 2 ≤ 6` for girth twelve or thirteen, this discharges
the original integer inequality.

## Verification

The full recursive #141 chain from `GraphConjecture141Extraction` through
`GraphConjecture141GirthThirteenClosure` was compiled from source into a fresh
temporary directory.  Every module used `-DwarningAsError=true`; each Lean
process was individually capped at 60 seconds.  The new module contains no
`sorry`, `admit`, `native_decide`, `#print`, or custom axiom declaration.
