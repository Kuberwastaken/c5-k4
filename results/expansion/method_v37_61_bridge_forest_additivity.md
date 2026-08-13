# WOWII #61 bridge-block forest additivity Lean extraction

## Extracted certificate API

The clique-, cycle-, and theta-bead computations use the same exact invariant
step: an induced forest restricts to a forest in every vertex-disjoint block,
while compatible block-maximizing witnesses combine across the attachment
bridge.  Therefore the ambient maximum induced-forest order is the sum of the
block maxima.

`GraphConjecture61BridgeForestAdditivity.lean` packages this as
`ForestBlockCompositionCertificate`.  Its hypotheses record:

- two disjoint finite blocks covering the ambient vertex set;
- an upper bound for the intersection of every ambient induced forest with
  each block;
- exact witnesses attaining both block bounds;
- acyclicity of their combined ambient induced subgraph.

The module proves separately:

```text
every ambient forest has order <= leftMaximum + rightMaximum,
leftMaximum + rightMaximum <= largestInducedForestSize,
largestInducedForestSize = leftMaximum + rightMaximum.
```

It also defines `BridgeAttachedForestCertificate`, which adds roots, the
attachment adjacency, and the assertion that this is the only cross-block
edge.  Its exact-sum and subtraction corollaries are convenient for iterated
bead certificates.

## Necessary hypothesis boundary

The combined-witness acyclicity premise is deliberately explicit.  It is
automatic for a true bridge attachment, but the current graph library does
not provide a direct theorem that unions two induced forests across a unique
cross edge.  Omitting compatibility in a more general separator setting is
false: two individually acyclic restrictions can combine into a cycle when
there are multiple cross edges.  The certificate API therefore preserves the
countermodel boundary rather than silently asserting unconditional union
acyclicity.

This is theorem extraction supporting the exact forest certificates in the
#61 experiments.  It does not prove WOWII #61 itself.

## Verification

The existing warning-clean #40 baseline was supplied from a fresh temporary
module directory.  From the pinned `formal-conjectures` Lake environment:

```text
LEAN_PATH=/tmp/c5k4-40-star-check timeout 55s lake env lean \
  -DwarningAsError=true \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture61BridgeForestAdditivity.lean
```

The command exited zero in 6.6 seconds with no output.  The new module contains
no `sorry`, `admit`, custom `axiom`, or native decision procedure.
Fresh `.olean` compilation and `#print axioms` report only Lean's standard
`propext`, `Classical.choice`, and `Quot.sound` foundations for both exact-sum
theorems.

No commit, push, release, issue, PR, or other public action was performed.
