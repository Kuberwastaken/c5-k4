# Method v0.33: WOWII #141 scalable radius-five exclusion

Date: 2026-08-13
Status: distance-six witness closed; girth-fourteen/fifteen metric obstruction removed

## Result

[`lean/GraphConjecture141RadiusFive.lean`](../../lean/GraphConjecture141RadiusFive.lean)
extends the BFS forest argument through rank five and proves:

```lean
theorem everyVertexHasDistanceAtLeastSix_of_connected_of_twelve_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 12 ≤ G.girth) :
    EveryVertexHasDistanceAtLeastSix G
```

Thus every root in a connected graph of girth at least twelve reaches a
vertex at distance at least six.  This is the metric input required by the
next WOWII #141 tail extension for girth fourteen and fifteen.

## Scaled estimates

The proof reuses the generic canonical geodesic-splice lemmas rather than
constructing new cycle representations.

For BFS ranks at most five:

1. An edge within one layer joins endpoints of two equal-length root
   geodesics.  The canonical splice and closing edge produce a simple cycle
   of length at most `2 * 5 + 1 = 11`.  Girth at least twelve therefore makes
   every layer through rank five independent.
2. Two distinct preceding-layer parents of a vertex at rank at most five
   produce a cycle of length at most `2 * 4 + 2 = 10`.  Girth at least twelve
   therefore gives unique parents.
3. A maximum-distance vertex on any simple cycle cannot have an equal-rank
   cycle neighbor by layer independence, cannot have a higher-rank neighbor
   by maximality, and hence has two distinct neighbors exactly one rank
   lower.

These fields instantiate the existing rank-generic forest certificate.  A
radius-five center would make the graph acyclic and force girth zero,
contradicting girth at least twelve.

## Exact next representation rung

To close the original conjecture through girth fifteen, the remaining work is
now finite representation bookkeeping:

1. extract a chordless six-edge prefix from the distance-six witness;
2. reuse the four-tail certificate from v0.32;
3. exclude edges from the sixth endpoint into the retained center
   neighborhood and preceding tail vertices;
4. attach it as a fifth leaf and count `maximum local independence + 6`.

No further radius obstruction is needed for that range.

## Verification

The complete recursive #141 chain from `GraphConjecture141Extraction` through
`GraphConjecture141RadiusFive` was compiled from source into a fresh temporary
directory.  Every Lean invocation used `-DwarningAsError=true` and was
individually capped at 60 seconds.  The new module contains no `sorry`,
`admit`, `native_decide`, `#print`, or custom axiom declaration.
