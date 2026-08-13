# Method v0.27: WOWII #141 radius-three layer independence

Date: 2026-08-13
Status: same-layer branch of the radius-three BFS certificate closed

## Result

[`lean/GraphConjecture141RadiusThreeLayers.lean`](../../lean/GraphConjecture141RadiusThreeLayers.lean)
connects the v0.26 equal-layer cycle constructor directly to the BFS ranks in
`GraphConjecture141RadiusThreeAcyclic`.

For every connected graph of girth at least eight, every exact-distance layer
of index at most three is independent:

```text
k <= 3  ->  G.IsIndepSet {v | dist r v = k}.
```

The four-layer specialization packages independence of ranks `0`, `1`, `2`,
and `3` around an arbitrary root.

## Proof

Assume distinct vertices `x,y` in layer `k <= 3` are adjacent.  Connectedness
supplies geodesics

```text
p : r -> x
q : r -> y
```

of lengths `dist r x = k` and `dist r y = k`.  The v0.26 constructor selects
their last common vertex, excludes the closing edge internally, and produces
a simple cycle of length at most seven.  Mathlib's `girth_le_length` then gives

```text
girth G <= 7,
```

contradicting `8 <= girth G`.

## Connection to the radius-three certificate

This closes the horizontal-edge part of
`RadiusThreeForestCertificate.cyclePeak`.  Along any cycle, two consecutive
vertices can no longer occupy the same BFS rank through radius three.  At a
maximum-rank cycle vertex, both incident cycle neighbors must therefore move
to the preceding layer once the standard distance-adjacency bound and finite
maximum selection are connected.

The substantive remaining girth branch is now **unique parent**: a vertex in
a positive layer cannot have two distinct neighbors in the preceding layer.
That requires the analogous two-edge closure

```text
parent x -- child v -- parent y
```

combined with equal-layer geodesics to `x` and `y`.  Its expected cycle bound
at radius three is at most eight, still contradictory to the active girth-ten
hypothesis.  After unique parent, the residual cycle-peak assembly is chiefly
finite maximum/rank bookkeeping.

## Verification

The entire recursive #141 chain was compiled from source into the fresh
directory `/tmp/c5k4_141_layers_audit.AlhY0P`.  Every module used:

```bash
LEAN_PATH=/tmp/c5k4_141_layers_audit.AlhY0P timeout 60s lake env lean \
  -DwarningAsError=true \
  -o /tmp/c5k4_141_layers_audit.AlhY0P/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

All dependencies from `GraphConjecture141Extraction` through
`GraphConjecture141EqualLayerClosure` passed, followed by the new
`GraphConjecture141RadiusThreeLayers`.  Every invocation exited `0`, emitted
no Lean diagnostics, used warnings-as-errors, and was individually capped at
60 seconds.  The new module contains no `sorry`, `admit`, `native_decide`,
`#print`, or custom axiom declaration.
