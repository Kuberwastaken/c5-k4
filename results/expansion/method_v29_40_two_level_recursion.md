# WOWII 40 v0.29: two-level recursive block-tree composition

## Outcome

The separator recurrence is now iterated on an explicit second decomposition
of the cut-deleted remainder.

After an outer exclude-dominant step, applying the complete dichotomy to the
remainder gives

```text
either tau(G) = tau((G-c)-d) + 2,
or     tau(G) = includeDeficiency(H[L],d)
                  + includeDeficiency(H[R],d) + 1,
```

where `H = G-c`. Thus the second node of the block tree is not represented by
an unused abstraction: its own branch choice is consumed in the parent's
exact feedback coordinate.

The two-exclude specialization proves the exact two-unit recurrence. It is
then paired with two explicit `LeafBlockStep` certificates. Starting from a
path-family rank target `2*k+1`, the first leaf allocation establishes
`2*(k+1)+1`, and the second establishes `2*(k+2)+1`, while the two separator
steps prove `tau(G)=k+2`. The final theorem feeds the resulting twice-extended
path family directly into the bipartite deficiency criterion for WOWII 40.

This is a concrete depth-two instance of the intended total block-tree
argument and verifies that the dependent subtype remainder, branch recurrence,
feedback arithmetic, and iterative rank certificates compose without a type
gap.

## Verification

The complete 23-module chain was rebuilt in topological order into the fresh
`mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_two_level_final.BQeqt7`. Every
Lean process used an explicit olean output, `-DwarningAsError=true`, and a
60-second cap; all 23 returned exit code zero. The new source contains no
`native_decide`, `sorry`, `admit`, `#print`, or custom axiom.
