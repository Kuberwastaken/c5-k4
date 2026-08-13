# Method v0.28: WOWII #141 unique preceding-layer parent

Date: 2026-08-13
Status: `RadiusThreeForestCertificate.uniqueParent` closed

## Result

[`lean/GraphConjecture141UniqueParent.lean`](../../lean/GraphConjecture141UniqueParent.lean)
proves the unique-parent field required by the radius-three BFS forest
certificate.

In a connected graph of girth at least nine, if a vertex `v` has distance at
most three from a root `r`, then it has at most one neighbor in the preceding
distance layer.

## Two-parent cycle

Assume distinct parents `x,y` satisfy

```text
dist r x + 1 = dist r v
dist r y + 1 = dist r v
v -- x
v -- y.
```

Choose equal-length geodesics from `r` to `x` and `y`.  Their canonical
last-common splice gives a simple connector `x -> y` of length at most the sum
of the two geodesic lengths.

The child `v` is absent from either parent geodesic: if it occurred on a
shortest path to a vertex one layer closer to the root, the shortest prefix to
`v` would be no longer than the entire parent path, contradicting
`dist r v = dist r x + 1`.

Support containment for the two canonical splice pieces therefore keeps `v`
off the connector.  Appending `y-v` and closing with `v-x` gives a simple
cycle of length at most

```text
p.length + q.length + 2.
```

For `dist r v <= 3`, both parent paths have length at most two, so the cycle
has length at most six.  This is stronger than the anticipated bound eight
and contradicts girth at least nine.

## Certificate integration

The module proves `radiusThree_uniqueParent` in the exact dependent function
shape of `RadiusThreeForestCertificate.uniqueParent`.

It also defines `radiusThreeForestCertificate_of_cyclePeak`.  Connectedness,
girth at least nine, and a radius-three center now construct every certificate
field except `cyclePeak`.  Thus the exact remaining radius-three obstruction
is finite maximum selection on an arbitrary simple cycle:

1. select a non-root cycle vertex of maximum distance rank;
2. use v0.27 layer independence to rule out equal-rank cycle neighbors;
3. use adjacency-distance variation to force both neighbors one layer lower.

Once this bookkeeping lemma is supplied, `RadiusThreeForestCertificate.isAcyclic`
and the existing `everyVertexHasDistanceAtLeastFour` bridge apply directly.

## Verification

The full recursive #141 chain was compiled from source into the fresh
directory `/tmp/c5k4_141_parent_audit.3jzeEK`.  Every module used:

```bash
LEAN_PATH=/tmp/c5k4_141_parent_audit.3jzeEK timeout 60s lake env lean \
  -DwarningAsError=true \
  -o /tmp/c5k4_141_parent_audit.3jzeEK/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

All dependencies from `GraphConjecture141Extraction` through
`GraphConjecture141RadiusThreeLayers` passed, followed by the new
`GraphConjecture141UniqueParent`.  Every process exited `0`, emitted no Lean
diagnostics, used warnings-as-errors, and was individually capped at 60
seconds.  The new module contains no `sorry`, `admit`, `native_decide`,
`#print`, or custom axiom declaration.
