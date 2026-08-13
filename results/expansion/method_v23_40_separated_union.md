# WOWII 40 v0.23: separated-union cycle localization

## Outcome

The missing reverse union lemma is formalized.  If no graph edge crosses
between finite sets `A,B`, and both induced subgraphs are acyclic, then the
graph induced by `A union B` is acyclic.  (Disjointness is unnecessary for
cycle localization; the separator application uses it later to add the two
cardinalities.)

The proof first establishes that a walk beginning on one side cannot leave
that side.  It then localizes the entire support of a hypothetical cycle.
Rather than constructing an artificial total projection from the union, Lean
maps the cycle to its own walk subgraph, whose vertices are exactly supported
vertices, and embeds that subgraph into the appropriate side.  Injectivity of
both maps preserves the cycle, contradicting side acyclicity.

This is precisely the reverse separated-union acyclicity API obstruction left
by v0.22.  The file then unions the two attained side witnesses, proves their
disjointness and anticompleteness from the separator fields, and obtains the
reverse state inequality.  Combining it with v0.22's restriction inequality
closes the exact formula

```text
forestOrderExcluding G c
  = forestOrderWithin G (L.erase c)
    + forestOrderWithin G (R.erase c).
```

## Verification

The complete 17-module dependency chain, from
`GraphConjecture40Baseline.lean` through
`GraphConjecture40SeparatedUnion.lean`, was rebuilt in topological order into
the fresh isolated directory
`/Users/kuber.mehta/Projects/scratch/c5k4_40_strict_final.PXMSF0`.  Every Lean
invocation used an explicit output path, `-DwarningAsError=true`, and a
60-second process cap; all 17 returned exit code zero.  The final module
contains no `native_decide`, `sorry`, `admit`, `#print`, or custom axiom.
