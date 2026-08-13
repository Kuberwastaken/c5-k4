# Method v0.31: WOWII #141 scalable radius-four exclusion

Date: 2026-08-13
Status: distance-five witness closed; girth-twelve/thirteen metric obstruction removed

## Result

[`lean/GraphConjecture141RadiusFour.lean`](../../lean/GraphConjecture141RadiusFour.lean)
generalizes the v0.29 maximum-cycle-peak argument through BFS rank four.  It
proves the stronger-than-requested theorem

```lean
theorem everyVertexHasDistanceAtLeastFive_of_connected_of_ten_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 10 ≤ G.girth) :
    EveryVertexHasDistanceAtLeastFive G
```

Thus every root in a finite connected graph of girth at least ten has a
vertex at distance at least five.  In particular, the metric witness needed
to extend WOWII #141 to girth twelve and thirteen is unconditional.

## Why the certificate scales

`RadiusThreeForestCertificate` is rank-generic despite its historical name:
acyclicity needs only unique preceding-layer parents and a maximum-rank peak
on every cycle.  The radius bound occurs solely in the estimates proving
those two fields.

For ranks at most four:

1. A horizontal edge joins equal-rank geodesic endpoints.  Their canonical
   splice closes to a cycle of length at most `2 * 4 + 1 = 9`, so girth ten
   makes every layer through rank four independent.
2. Two distinct parents of a rank-four vertex close to a cycle of length at
   most `2 * 3 + 2 = 8`, so girth ten gives unique parents.
3. On any simple cycle, select a support vertex of maximum distance from the
   root.  Layer independence rules out equal-rank neighbors, maximality rules
   out higher-rank neighbors, and adjacency-distance variation forces both
   cycle neighbors exactly one rank lower.

The resulting forest certificate makes any radius-four graph acyclic.  Its
girth would then be zero, contradicting the positive girth hypothesis.

## New reusable interfaces

The module adds:

- `RadiusFourCenter`;
- `EveryVertexHasDistanceAtLeastFive` and its exact negation equivalence;
- layer independence through rank four;
- unique preceding-layer parents through rank four;
- `cyclePeak_of_radiusFourCenter`;
- `radiusFourForestCertificate`;
- the unconditional distance-five theorem.

## Exact remaining girth-twelve/thirteen gap

For girth twelve or thirteen, the original arithmetic requires an induced
tree of size

```text
maximum local independence + 5.
```

The v0.31 theorem now supplies a shortest path with five edges from a maximum
local center.  The remaining gap is purely the next representation rung:

1. package its chordless five-edge prefix `v-u-x-y-z-t`;
2. reuse the certified three-tail on `x-y-z`;
3. show `t` has no additional edge into the retained star or earlier tail;
4. attach `t` as a fourth leaf and count the resulting induced tree.

The needed chord exclusion is bounded: any extra edge from `t` to `N(v)`
closes a cycle of length at most seven, while shortestness already excludes
edges to the earlier prefix vertices.  No further radius or distance theorem
is required for the 12/13 range.

## Verification

The complete recursive #141 chain, from `GraphConjecture141Extraction`
through `GraphConjecture141RadiusFour`, was compiled from source into a fresh
temporary directory.  Each invocation used:

```bash
LEAN_PATH=<fresh-audit-directory> timeout 60s lake env lean \
  -DwarningAsError=true \
  -o <fresh-audit-directory>/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

Every process was individually capped at 60 seconds.  The new module contains
no `sorry`, `admit`, `native_decide`, `#print`, or custom axiom declaration.
