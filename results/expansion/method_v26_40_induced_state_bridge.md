# WOWII 40 v0.26: ambient/subtype state bridge

## Outcome

The separator dynamic-programming states can now be used recursively on
induced subtype graphs.  For every finite side `A`, the formalization proves

```text
forestOrderWithin G A
  = largestInducedForestSize (G.induce A),
```

and, for every `c in A`,

```text
forestOrderWithinIncluding G A c
  = forestOrderIncluding (G.induce A) <c,hc>.
```

The proof transports attained witnesses through the canonical subtype map.
An explicit graph isomorphism identifies the graph obtained by first inducing
on `A` and then on a subtype finset with the ambient graph induced on that
finset's image.  This preserves acyclicity and cardinality in both directions.

As a recursive interface, `blockTreeForestRank` is rewritten completely as a
maximum of ordinary invariants of the induced left, right, left-minus-cut,
and right-minus-cut subtype graphs.  This closes the ambient/subtype typing
gap identified in v0.25; future block-tree induction can call graph invariants
on genuinely smaller vertex types rather than carrying ambient constrained
finsets.

## Verification

The complete 20-module dependency chain was rebuilt in topological order into
the fresh `mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_bridge_final.tJs81f`. Every Lean
invocation used an explicit olean output, `-DwarningAsError=true`, and a
60-second process cap; all 20 returned exit code zero. The new source contains
no `native_decide`, `sorry`, `admit`, `#print`, or custom axiom.
