# Method v0.22: WOWII 141 radius-three rank certificate

Date: 2026-08-13
Status: four-layer cover, parent extraction, and generic rank-cycle
contradiction verified; the cycle-peak layer lemma remains

## Four BFS layers

[`lean/GraphConjecture141RadiusThreeAcyclic.lean`](../../lean/GraphConjecture141RadiusThreeAcyclic.lean)
defines exact BFS layers by `dist(root,v)=k` and proves that a radius-three
center covers the graph with layers zero through three.

It also proves a reusable parent lemma: every vertex at distance `k+1` has a
neighbor at distance exactly `k`.  The parent is extracted from a shortest
path; the exact layer equality follows from the path prefix upper bound and
the adjacency distance alternatives.

## Rank certificate

The file introduces `RadiusThreeForestCertificate`.  Its rank is intended to
be distance from the root.  It requires:

- every non-root vertex has at most one neighbor one rank lower; and
- every hypothetical cycle contains a non-root maximum-rank vertex whose two
  cycle neighbors are both one rank lower.

The acyclicity proof is then immediate and fully formal: the peak vertex has
two distinct parents, contradicting uniqueness.

This rank formulation scales beyond four layers and avoids the parity
problem that blocked a direct reuse of the radius-two bipartition theorem.

## Exact remaining girth lemma

`RadiusThreeBfsPeakProperty G` packages the sole residual:

```text
every radius-three center admits the rank certificate with rank=dist(root).
```

At girth at least ten, parent uniqueness follows because two distinct parents
of a layer-`k` vertex, together with shortest root paths, create a cycle of
length at most `2k`, hence at most six for `k<=3`.

For the cycle-peak field, choose a maximum-distance vertex on the cycle.
Adjacent cycle vertices cannot lie in the same layer: combining their root
paths with that edge produces a cycle of length at most seven.  Maximality
then forces both neighbors one layer lower.  The remaining formal work is to
turn the two possibly intersecting root paths plus the chord into a simple
`Walk.IsCycle`; this is exactly the same missing path-intersection primitive
behind the general theorem `girth <= 2*radius+1`.

Lean proves that the peak property, once established, yields the unconditional
distance-four theorem at girth at least ten.  No radius-girth result is
assumed as an axiom.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141RadiusThreeAcyclic.lean
```

Result: exit 0 in 8.3 seconds.  The file contains no proof placeholders,
native evaluation shortcuts, or custom axioms.
