# Method v0.18: WOWII 141 radius-two contradiction closed

Date: 2026-08-13
Status: unconditional distance-three theorem proved for connected graphs of
girth at least eight; final second-leaf chord packaging remains

## Second-layer independence

[`lean/GraphConjecture141RadiusTwoInstantiation.lean`](../../lean/GraphConjecture141RadiusTwoInstantiation.lean)
defines the exact BFS layers around a root `v`:

```text
L1   = neighborSet(v)
L2   = {w | dist(v,w)=2}
even = {v} union L2.
```

The new core lemma proves `L2` is independent at girth at least eight.  If
two second-layer vertices `x,y` were adjacent, choose shortest-path parents
`a,b` in `L1`.

- If `a=b`, the edges `a-x-y-a` form a triangle.
- If `a!=b`, the edges `v-a-x-y-b-v` form a 5-cycle.
- Apparent vertex collisions in the 5-cycle instead give a direct first-layer
edge to a distance-two vertex, or a triangle; each is discharged explicitly.

In every case `girth_le_length` contradicts `girth >= 8`.

## Full BFS certificate

The file then proves:

- `even` is independent: the root cannot meet `L2`, and `L2` is independent;
- `L1` is independent by the previously certified triangle exclusion;
- the layers cover all vertices under a radius-two-center hypothesis; and
- every non-root even vertex has a unique `L1` neighbor, using a shortest-
  path parent and the previously certified 4-cycle exclusion.

These fields instantiate the v0.17 `RadiusTwoForestCertificate`, hence the
whole graph is acyclic.  Positive girth contradicts that conclusion.

## Closed theorem

The radius-two obstruction is now eliminated without any BFS axiom:

```text
G.Connected and 8 <= girth(G)
  -> for every v, there exists w with 3 <= dist(v,w).
```

This is the exact eccentricity-three theorem sought since v0.14.  It is
slightly weaker than the general numerical bound `girth <= 2*radius+1`, but
it is precisely sufficient for the girth-eight/nine WOWII construction.

## Remaining step to girth nine

The existing shortest-path theorem now supplies a chordless prefix
`v-u-x-y` at every maximum-local center.  The remaining assembly is local:

1. form the first `DistanceTwoLeafData` from `v-u-x`;
2. use girth to prove `y` is adjacent to no retained star vertex other than
   `x`; and
3. feed that uniqueness into the already verified `SecondLeafData` assembly.

All global eccentricity, BFS layering, two leaf-extension representations,
cardinality, and final arithmetic are now complete.

## Verification

From the `formal-conjectures` checkout:

```bash
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture141RadiusTwoInstantiation.lean
```

Result: exit 0 in 6.6 seconds.  The file contains no proof placeholders,
native evaluation shortcuts, or custom axioms.
