# WOWII 40 v0.24: shared-cut localization and include-state additivity

## Outcome

The include-cut half of the one-vertex-separation API is now exact.  The new
cycle-localization theorem proves that two induced forests glued at a common
cut vertex remain acyclic when every cross edge away from the cut is absent.

The proof treats the two possible cycle geometries directly.  A cycle meeting
the cut is rotated to begin there; deleting its first edge leaves a simple
path back to the cut, and path simplicity prevents that tail from visiting
the cut early or changing sides.  A cycle avoiding the cut is localized by
ordinary walk induction.  In either case the localized cycle embeds into one
of the assumed induced forests, a contradiction.

The side-constrained include state `forestOrderWithinIncluding` is attained
and bounds every feasible side forest.  Restriction and extension across a
`OneVertexSeparation` then give the exact natural-number identity

```text
forestOrderIncluding G c + 1
  = forestOrderWithinIncluding G L c
    + forestOrderWithinIncluding G R c.
```

The `+ 1` form is the canonical sum-minus-one formula without introducing
truncated natural subtraction.

## Verification

The complete 18-module dependency chain was rebuilt in topological order into
the fresh `mktemp` directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_include_final.XWXwC1`. Every Lean
process used an explicit olean output, `-DwarningAsError=true`, and a 60-second
cap; all 18 returned exit code zero. The source contains no `native_decide`,
`sorry`, `admit`, `#print`, or custom axiom.
