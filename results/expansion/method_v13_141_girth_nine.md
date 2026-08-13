# Method v0.13: WOWII 141 two-vertex-tail reduction

Date: 2026-08-13
Status: verified sufficient certificate for girth 8 and 9; unconditional
tail existence remains open

## Arithmetic target

For girth eight or nine, WOWII 141 requires exactly

```text
max_v indepNeighborsCard(G,v) + 3 <= largestInducedTreeSize(G).
```

The closed girth-six/seven construction retained a maximum local star plus
one extra vertex, giving the maximum local independence plus two.  The next
range therefore needs one further genuine tail vertex.

## Verified certificate

[`lean/GraphConjecture141GirthNine.lean`](../../lean/GraphConjecture141GirthNine.lean)
defines `TwoVertexTailSplice G`.  It records:

- a center attaining maximum local independence;
- a maximum independent set in its open neighborhood;
- two distinct new vertices outside the star; and
- a certificate that the entire induced star-plus-two-vertex-tail is a tree.

Lean proves the exact cardinal identity

```text
|{center} union localSet union {first,second}|
  = max_v indepNeighborsCard(G,v) + 3,
```

injects that explicit induced tree into `largestInducedTreeSize`, and derives
the exact upstream-shaped WOWII 141 inequality throughout
`8 <= girth(G) <= 9`.

## Precise obstruction

The new `ThirdVertexChordExclusion` definition isolates what the next
shortest-path proof must provide.  For a path prefix

```text
v -- u -- x -- y,
```

the third vertex `y` must be nonadjacent to the center and every retained
local neighbor, while retaining its prescribed edge to `x`.  Together with
the already proved uniqueness of `x`'s attachment into `N(v)`, these are
exactly the chord exclusions that make the retained graph a star with a
two-edge tail.

This pass does not claim that every maximum center in a connected girth-eight
graph admits such a three-edge shortest-path prefix.  Unlike the first
distance-two step, the previous universal-center contradiction only forces a
nonneighbor and hence distance at least two; it does not immediately force
eccentricity at least three at the selected maximizing center.  Coordinating
a shortest girth cycle with that specified center is the remaining global
existence problem.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141GirthNine.lean
```

Result: exit 0 in 7.6 seconds.  The file contains no proof placeholders,
native evaluation shortcuts, or custom axioms.

## Next exact rung

The next pass should prove one of the following:

1. every center of a connected graph with girth at least eight has a vertex
   at distance at least three; or
2. the weaker statement only for centers attaining maximum local
   independence.

Either statement lets the shortest-path construction supply `u,x,y`.
Girth then excludes every prohibited chord by producing cycles of length at
most five, after which the generic leaf-extension theorem can be applied a
second time to construct `TwoVertexTailSplice` without assuming its final
tree field.
