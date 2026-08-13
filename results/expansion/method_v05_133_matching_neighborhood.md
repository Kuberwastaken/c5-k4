# Method v0.5: WOWII 133 matching-neighborhood formula

Date: 2026-08-13 UTC

Status: **MAX-DEGREE-ONE FORMULA PROVED / C4-FREE LOCAL-AVERAGE FORMULA PROVED**

Local artifact: `lean/GraphConjecture133MatchingNeighborhood.lean`

## Result

This pass closes the finite matching-neighborhood boundary isolated by
`method_v05_133_next.md`.  It proves, without `sorry`, that every finite graph
`H` satisfying `degree(H,v) <= 1` at every vertex obeys

```text
indepNum(H) + |E(H)| = |V(H)|.
```

Applying the formula to open neighborhoods in a C4-free graph gives the exact
pointwise correction

```text
indepNeighborsCard(G,v) + |E(G[N(v)])| = degree(G,v).
```

Consequently the source invariant has the fully formal identity

```text
l(G) = (2|E(G)| - sum_v |E(G[N(v)])|) / |V(G)|
```

for every finite C4-free graph.  The subtraction is natural-number
subtraction before casting; the proof establishes the needed inequality, so
no truncation information is lost.

## Exact maximum-degree-one proof

The equality is proved as two independently useful inequalities.

### General lower bound

`card_le_indepNum_add_card_edgeFinset` proves

```text
|V(H)| <= indepNum(H) + |E(H)|
```

for every finite simple graph.  It selects one endpoint from each edge using
the canonical `Sym2.out` representative.  The selected vertices form a
vertex cover of cardinality at most `|E(H)|`; its complement is independent.

### Matching upper bound

For the reverse inequality, choose a maximum independent set `S`.  Every edge
has an endpoint outside `S`.  Select such an endpoint for every edge.  In a
maximum-degree-one graph two distinct edges cannot share a vertex, so this
selection is injective into `V(H) \ S`.  Therefore

```text
|E(H)| <= |V(H) \ S|,
```

which gives `indepNum(H)+|E(H)| <= |V(H)|`.

The reusable lemmas

```text
adj_right_unique_of_degree_le_one
edge_eq_of_common_vertex_of_degree_le_one
```

formalize the uniqueness needed for that injection.  Combining the two
inequalities yields

```lean
indepNum_add_card_edgeFinset_eq_card_of_degree_le_one
```

with no graph-classification theorem and no ordering assumption on vertices.

## Application to C4-free neighborhoods

The file independently proves that every graph induced by an open
neighborhood in a C4-free graph has degree at most one.  Two distinct edges
sharing a neighborhood vertex would, together with the center, form a
not-necessarily-induced four-cycle.

The maximum-degree-one formula then supplies

```lean
indepNeighborsCard_add_neighborhoodEdgeCount_eq_degree_of_c4Free
```

and its subtractive form

```lean
indepNeighborsCard_eq_degree_sub_neighborhoodEdgeCount_of_c4Free.
```

This is the exact generalization of the earlier cubic split.  A triangle-free
neighborhood has zero correction; each edge inside a neighborhood subtracts
one from its local independence number.

## Averaged identity

Define

```text
neighborhoodEdgeCount(G,v) = |E(G[N(v)])|,
triangleIncidenceCount(G) = sum_v neighborhoodEdgeCount(G,v).
```

Summing the pointwise formula, using finite truncated-subtraction
distribution, and applying the degree-sum theorem gives the compiled theorem

```lean
l_eq_two_edges_sub_triangleIncidenceCount_of_c4Free
```

with conclusion

```text
l(G) = (2|E(G)| - triangleIncidenceCount(G)) / |V(G)|.
```

This is already an exact triangle-corrected local-average identity in the
source invariant's types.

## Relation to ordinary triangle count

Combinatorially, every edge of `G[N(v)]` is a triangle containing `v`, and
every triangle contributes one such edge at each of its three vertices.
Hence

```text
triangleIncidenceCount(G) = 3 * |cliqueFinset(G,3)|.
```

The source-notation consequence is packaged as

```lean
l_eq_two_edges_sub_three_triangles_of_c4Free
```

under exactly that explicit incidence equality:

```text
l(G) = (2|E(G)| - 3t(G)) / |V(G)|.
```

The equality between the two existing finite representations is not assumed
silently.  Mathlib exposes triangles as three-element clique finsets and
neighborhood edges as `Sym2` edge finsets, but no ready-made cardinality
bijection connects them.  Formalizing that generic representation bijection
is the sole remaining step before the final `3t(G)` spelling becomes
unconditional.  It is independent of C4-freeness and of the matching formula
proved here.

The preceding frozen exact check evaluated the unconditional numerical
identity on all 131 saved C4-free graph6 rows with zero failures.  No new graph
was generated in this pass.

## Verification

Every command was capped at 60 seconds.  The final warning-as-error build was

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture133MatchingNeighborhood.lean
```

and exited successfully in approximately seven seconds.

Temporary `#print axioms` audits of the finite matching formula, the pointwise
C4-free formula, and the averaged identity reported only `propext`,
`Classical.choice`, and `Quot.sound`.  They reported neither `sorryAx` nor a
custom axiom, and the temporary commands were removed.  A source scan finds
no `sorry`, `admit`, or custom `axiom` in the Lean artifact.

## Claim boundary

This result proves the exact local-invariant formula for every C4-free graph.
It does not prove the remaining induced-path inequality and therefore does not
claim full WOWII 133.  The ordinary triangle-count spelling remains
conditional only on the explicit, standard incidence double-count described
above; the neighborhood-edge spelling is unconditional and fully formal.
