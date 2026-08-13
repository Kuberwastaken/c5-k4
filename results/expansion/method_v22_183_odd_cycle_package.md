# Method v0.22: #183 explicit odd-cycle package

## Root-sensitive pair

For every cycle order `n>=5` and prescribed root, Lean chooses one of two
adjacent pairs, `{0,1}` or `{2,3}`, so that the pair avoids the root.  It proves
the pair is distinct and adjacent and constructs retained neighbors dominating
both deleted vertices.

These are the root-sensitive and domination parts of `IsGoodTwoDeletion`.

## Remaining standard cycle API fact

The only unproved family fact is packaged as
`CyclePairComplementPathProperty`: deleting either chosen adjacent pair from
`cycleGraph n` leaves a connected bipartite path.  Mathlib provides the cycle
adjacency API and path/cycle connectivity, but not this induced-complement
isomorphism directly.  Conditional on that one standard fact,
`rootSensitiveCyclePair_isGoodTwoDeletion` supplies the full v0.21 structural
predicate.

No conjectural graph inequality or cardinality budget is hidden in this
property; it is purely the concrete cycle-minus-two-adjacent-vertices path
identification.

## Triangle

`C3` is kept separate.  It cannot use the generic adjacent-pair construction:
the retained graph has only one vertex, and the mandatory external attachment
exposes the same local-budget obstruction found in v0.20.  It needs a bespoke
branch or a global cross-component payment argument.

## Verification

The first clean-source audit exposed nonportable arithmetic in the retained-
neighbor proof: wrapped `Fin` subtraction had been left to `simp`, and
`Fin.last (n - 1)` depended on a non-definitional equality.  The repaired proof
uses the correct oriented disjunct of `cycleGraph_adj'`, explicit hypotheses for
`Fin.sub_val_of_le`, the literal vertex `⟨n - 1, ...⟩`, and an explicit modular
calculation for the wrap edge `0 -- (n-1)`.  The unused triangle-bound parameter
is retained in the API under an underscore-prefixed name.

The entire recursive dependency chain was compiled from source into the fresh
directory `/tmp/c5k4_183_audit.Z2CinK`.  For each module, the command was:

```bash
LEAN_PATH=/tmp/c5k4_183_audit.Z2CinK timeout 60s lake env lean \
  -DwarningAsError=true \
  -o /tmp/c5k4_183_audit.Z2CinK/<MODULE>.olean \
  -R /Users/kuber.mehta/Projects/c5-k4/lean \
  /Users/kuber.mehta/Projects/c5-k4/lean/<MODULE>.lean
```

The source order and exact driver output were:

```text
BUILD GraphConjecture183OutsideBudget
PASS GraphConjecture183OutsideBudget
BUILD GraphConjecture183Attachment
PASS GraphConjecture183Attachment
BUILD GraphConjecture183ComponentAssembly
PASS GraphConjecture183ComponentAssembly
BUILD GraphConjecture183CorrectedAssembly
PASS GraphConjecture183CorrectedAssembly
BUILD GraphConjecture183ComponentFold
PASS GraphConjecture183ComponentFold
BUILD GraphConjecture183AttachmentSelection
PASS GraphConjecture183AttachmentSelection
BUILD GraphConjecture183SelectionExistence
PASS GraphConjecture183SelectionExistence
BUILD GraphConjecture183CorrectedFold
PASS GraphConjecture183CorrectedFold
BUILD GraphConjecture183LocalTrunks
PASS GraphConjecture183LocalTrunks
BUILD GraphConjecture183NontrivialTrunk
PASS GraphConjecture183NontrivialTrunk
BUILD GraphConjecture183TreeTrunkExistence
PASS GraphConjecture183TreeTrunkExistence
BUILD GraphConjecture183RootSensitiveLeaf
PASS GraphConjecture183RootSensitiveLeaf
BUILD GraphConjecture183TreeComponentFlattening
PASS GraphConjecture183TreeComponentFlattening
BUILD GraphConjecture183AmbientConnectivity
PASS GraphConjecture183AmbientConnectivity
BUILD GraphConjecture183UnicyclicTrunk
PASS GraphConjecture183UnicyclicTrunk
BUILD GraphConjecture183TwoDeletionTrunk
PASS GraphConjecture183TwoDeletionTrunk
BUILD GraphConjecture183OddCyclePackage
PASS GraphConjecture183OddCyclePackage
```

Every invocation exited `0`, emitted no Lean output, used
`-DwarningAsError=true`, and was individually capped at 60 seconds.  The module
contains no `native_decide`, `sorry`, `admit`, `#print`, or custom axiom
declaration.
