# WOWII 40 v0.30: arbitrary finite exclude recursion

## Outcome

The concrete depth-two construction now iterates to arbitrary finite depth.

`ExcludeTrace` is a dependent recursive certificate. Each node contains an
exclude-dominant `OneVertexSeparation`; its tail is indexed by the genuinely
new subtype graph obtained after deleting that node's cut. For a trace of
depth `n`, Lean proves the exact recurrence

```text
feedbackDeletion(initial)
  = feedbackDeletion(terminal) + n.
```

`LeafStepChain` independently records `n` successive allocated leaf paths in
the original ambient graph, with each constructor indexed by the path family
produced by the preceding insertion. Iterating `LeafBlockStep.rank_step`
proves

```text
initial target:  2*k + 1
terminal target: 2*(k+n) + 1.
```

The coupled theorem requires the exclude trace and leaf-step chain to have the
same depth. If the terminal feedback coordinate is `k`, it simultaneously
derives `tau(G)=k+n` and the matching terminal path-family rank. For bipartite
graphs, the arbitrary-depth terminal family feeds directly into the existing
deficiency theorem and proves WOWII 40.

This is the finite recursive induction wrapper suggested by the depth-two
experiment: graph types change correctly along the deletion trace, path-family
types change correctly along the allocation trace, and their shared natural
depth synchronizes the `+1` feedback and `+2` rank recurrences.

Include-dominant nodes remain represented by the additive alternative proved
in v0.28; this file isolates and closes the full finite all-exclude branch.

## Verification

The complete 24-module dependency chain was rebuilt in topological order into
the fresh `mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_finite_final.ONNM5U`. Every Lean
process used an explicit olean output, `-DwarningAsError=true`, and a 60-second
cap; all 24 returned exit code zero. The new source contains no
`native_decide`, `sorry`, `admit`, `#print`, or custom axiom.
