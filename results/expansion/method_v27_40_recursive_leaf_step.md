# WOWII 40 v0.27: genuine recursive separator leaf step

## Outcome

The separator envelope now drives an actual recursion rather than only ambient
state arithmetic.

First, the exclude state is identified with the ordinary maximum induced-
forest invariant of the cut-deleted graph:

```text
forestOrderExcluding G c
  = largestInducedForestSize (deleteVertex G c).
```

Consequently, when the exclude branch dominates the block-tree envelope,

```text
includeStateSum <= excludeStateSum,
```

the global and cut-deleted maximum forest orders are equal. The existing exact
feedback recursion therefore yields

```text
feedbackDeletion G = feedbackDeletion (deleteVertex G c) + 1.
```

The complementary include-dominant branch is also extracted explicitly from
the same maximum envelope.

Finally, the exclude branch is paired with `LeafBlockStep.rank_step`. If the
recursive remainder has feedback coordinate `k` and path-family target
`2*k+1`, an allocated leaf path on at least three vertices simultaneously
proves that the full graph has feedback coordinate `k+1` and upgrades the
path-family target to `2*(k+1)+1`. An end-to-end bipartite theorem feeds these
facts into the existing deficiency proof of WOWII 40.

This is the first separator leaf theorem in the chain where the branch choice,
typed recursive remainder, feedback successor, and matching linear-forest
rank increment are all connected in one formal interface.

## Verification

The complete 21-module chain was built in topological order into the fresh
`mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_leaf_final.ubgDMr`. Every Lean
process used an explicit olean output, `-DwarningAsError=true`, and a 60-second
cap; the final corrected chain returned exit code zero throughout. The new
source contains no `native_decide`, `sorry`, `admit`, `#print`, or custom
axiom.
