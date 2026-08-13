# Method v0.6: WOWII 133 triangle incidence

## Closed rung

`lean/GraphConjecture133TriangleIncidence.lean` proves, without extra
hypotheses,

```text
sum_v numTrianglesAtVertex(G,v) = 3 * |cliqueFinset(G,3)|.
```

The proof is a direct double count of the finite incidence relation
`v ∈ triangle`.  Mathlib's
`Finset.sum_card_bipartiteAbove_eq_sum_card_bipartiteBelow` changes the order
of summation, and `SimpleGraph.IsNClique.card_eq` says that every member of
`cliqueFinset 3` has exactly three vertices.

This is in the source's own `numTrianglesAtVertex` notation and requires no
C4-free assumption.

## Exact remaining bridge

The existing #133 development defines

```text
neighborhoodEdgeCount(G,v)
  = |edgeFinset (G.induce (G.neighborSet v))|.
```

To turn the already proved identity

```text
l(G) = (2|E(G)| - sum_v neighborhoodEdgeCount(G,v)) / |V(G)|
```

into the unconditional source formula, the one missing lemma is the pointwise
cardinality equality

```text
neighborhoodEdgeCount(G,v) = numTrianglesAtVertex(G,v).
```

Mathematically, the bijection sends a neighborhood edge `{a,b}` to the
3-clique `{v,a,b}`, with inverse `triangle.erase v`.  There is no packaged
Mathlib lemma relating the subtype-valued `Sym2` elements of the induced
graph's `edgeFinset` to the ambient `Finset V` elements of `cliqueFinset 3`.
The remaining formal obligation is therefore representation plumbing:

1. transport both endpoints of `Sym2 (G.neighborSet v)` through subtype
   coercions;
2. prove the resulting ambient pair, after inserting `v`, is a 3-clique;
3. reconstruct a non-diagonal `Sym2` edge from `s.erase v` for an incident
   3-clique `s`;
4. prove the two constructions inverse despite the quotient representation of
   `Sym2`.

Useful APIs confirmed during this lane are
`Sym2.toFinset_mk_eq`, `Sym2.ext`, `Finset.card_eq_two`,
`Finset.insert_erase`, `SimpleGraph.is3Clique_triple_iff`, and
`Finset.card_bij'`.  No `sorry`, `admit`, or custom axiom was introduced.
