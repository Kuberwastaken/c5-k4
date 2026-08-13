# Method v0.15: WOWII 141 second-leaf assembly

Date: 2026-08-13
Status: second-leaf construction fully verified; BFS radius-girth bridge
remains the sole global step for unconditional girth 8 and 9

## BFS route

The right global theorem is the standard radius-girth estimate for connected
cyclic graphs:

```text
girth(G) <= 2 * radius(G) + 1.
```

A breadth-first tree rooted at a center plus a non-tree edge produces the
short cycle.  In particular, `girth(G) >= 8` forces radius at least four,
which is stronger than the distance-three property needed in v0.14.

No theorem with this girth/radius interface was found in the current mathlib
checkout.  Formalizing the BFS parent map, locating a non-tree edge, and
turning the two root paths plus that edge into a simple `Walk.IsCycle` is the
remaining library-scale task.  This pass does not insert the radius-girth
estimate as an axiom or assumption.

## Assembly completed

[`lean/GraphConjecture141RadiusGirth.lean`](../../lean/GraphConjecture141RadiusGirth.lean)
closes the other half of the girth-eight/nine program.

`SecondLeafData G` starts with the already verified first-leaf
`DistanceTwoLeafData` and adds a second vertex whose unique neighbor in the
entire retained first-stage tree is the first leaf.  Lean proves that:

1. deleting the second vertex leaves exactly the first-stage induced tree;
2. the nested induced-subgraph representation is graph-isomorphic to that
   first-stage tree;
3. the generic leaf-extension theorem applies; and
4. the full maximum local star plus two-vertex tail is an induced tree.

This constructs `TwoVertexTailSplice` without assuming its final tree field.
Consequently the exact upstream WOWII 141 statement follows throughout
`8 <= girth(G) <= 9` from explicit second-leaf adjacency data.

## Exact remaining interface

After v0.14 and this pass, an unconditional proof needs only:

- obtain a vertex at distance at least three from the chosen maximum-local
  center, preferably via `girth <= 2*radius+1`;
- extract the chordless `v-u-x-y` prefix using the already verified shortest-
  path lemma; and
- use girth to show `y` has exactly one neighbor in the retained first-stage
  tree, namely `x`.

The induced-tree transport, the second leaf extension, the exact cardinality,
and the final integer inequality are all complete.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141RadiusGirth.lean
```

Result: exit 0 in 8.2 seconds.  The file contains no proof placeholders,
native evaluation shortcuts, or custom axioms.
