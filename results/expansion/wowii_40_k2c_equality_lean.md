# WOWII 40: `K_{2,c}` equality manifold in Lean

Date: 2026-08-13

Lean module: `lean/GraphConjecture40K2cEquality.lean`

The cut-pair-fusion equality family is formalized as
`K2c c = completeBipartiteGraph (Fin 2) (Fin c)`.  The module proves:

- `largestInducedForestSize (K2c c) = c + 1` for `c ≥ 2`;
- `largestInducedBipartiteSubgraphSize (K2c c) = c + 2` for every `c`;
- `b (K2c c) = c + 2`;
- `pathCoverNumber (K2c c) ≤ c - 2` for `c ≥ 3`, using the explicit
  alternating five-vertex path and singleton completion;
- exact equality in the original ceiling expression for `c ≥ 4`, assuming
  only the complementary lower certificate
  `c - 2 ≤ pathCoverNumber (K2c c)`.

The forest proof is structural.  The graph contains a four-cycle, so every
induced forest omits a vertex; deleting one of the two left vertices leaves
an induced star of order `c+1`.  The bipartite invariant is witnessed by the
standard two-coloring of the full graph.

The sole remaining premise is explicit rather than hidden: the repository's
`pathCoverNumber` is currently an `sInf` with no lower-bound API expressing
the standard bipartition-imbalance argument.  Mathematically, each path in a
`2 | c` bipartition contains at most one more right than left vertex, so a
cover needs at least `c-2` paths.  The module proves the matching upper bound
without assuming this argument.

Verification command (from the `formal-conjectures` checkout):

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture40K2cEquality.lean
```

Result: pass.  The axiom audit reports only `propext`, `Classical.choice`, and
`Quot.sound`; there is no `sorryAx`, `native_decide`, or custom axiom.
