# Method v0.7: Lean proof of the WOWII 19 induced-star bound

Date: **2026-08-13 UTC**

Status: **complete local no-`sorry` proof of the first graph-specific rung; not a proof of WOWII 19**

Local artifact:

```text
lean/GraphConjecture19StarBound.lean
```

No formal-conjectures source file was edited, and no theorem whose proof
contains `sorry` is invoked.

## Formalized result

The endpoint theorem is the requested invariant-native lower bound:

```lean
theorem indepNeighborsCard_add_card_add_one_le_b
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) (I : Finset V)
    (hI : G.IsIndepSet (I : Set V))
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    ((indepNeighborsCard G v + I.card + 1 : ℕ) : ℝ) ≤ b G
```

Thus any independent set outside the closed neighborhood of `v` combines with
a maximum independent set in `G[N(v)]` and the center `v` to give an induced
bipartite subgraph of the exact claimed order.  The file also retains the
natural-valued version:

```lean
theorem indepNeighborsCard_add_card_add_one_le_largestInducedBipartiteSubgraphSize
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) (I : Finset V)
    (hI : G.IsIndepSet (I : Set V))
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    indepNeighborsCard G v + I.card + 1 ≤
      G.largestInducedBipartiteSubgraphSize
```

## Explicit coloring and cardinality

The graph-specific rung from the proof-ladder report now compiles as:

```lean
lemma induce_insert_union_isBipartite_of_indep
    (G : SimpleGraph V) (v : V) (A I : Finset V)
    (hA : G.IsIndepSet (A : Set V))
    (hAN : (A : Set V) ⊆ G.neighborSet v)
    (hI : G.IsIndepSet (I : Set V))
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    (G.induce (↑(insert v (A ∪ I)) : Set V)).IsBipartite
```

It uses `induce_isBipartite_iff_exists_coloring` with the explicit coloring

```text
color 0: A
color 1: {v} union I.
```

Same-color adjacency is impossible because `A` and `I` are independent and
`v` has no neighbor in `I`.  Edges between `A` and `I` are unrestricted and
correctly cross the bipartition.

The separate cardinality lemma proves

```lean
(insert v (A union I)).card = A.card + I.card + 1.
```

Its hypotheses imply all required disjointness: membership in `A` gives
adjacency to `v`, membership in `I` forbids it, looplessness excludes `v` from
`A`, and the outside condition excludes `v` from `I`.  The artifact preserves
the explicit witness and cardinality before inserting it into the repository's
`sSup` definition.

## Maximum neighborhood witness

The file also closes the extremal-choice plumbing anticipated in the scout:

```lean
lemma exists_local_indep_witness (G : SimpleGraph V)
    [DecidableRel G.Adj] (v : V) :
    ∃ A : Finset V,
      G.IsIndepSet (A : Set V) ∧
      A ⊆ G.neighborFinset v ∧
      A.card = indepNeighborsCard G v
```

The proof applies `exists_isNIndepSet_indepNum` to
`G.induce (G.neighborSet v)` and maps its subtype vertices back into the
ambient vertex type with `Function.Embedding.subtype`.  This makes the final
bound use the actual upstream `indepNeighborsCard`, not an assumed cardinality
or an auxiliary maximum.

Finally,
`card_le_largestInducedBipartiteSubgraphSize` inserts the explicit witness into
the bounded `sSup` defining the maximum induced-bipartite order, and
`exact_mod_cast` transfers the result to the real-valued notation `b G`.

## Verification

Every subprocess was externally capped at 60 seconds.  The final
warning-as-error build was run from the formal-conjectures Lake project:

```text
timeout 60s lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/GraphConjecture19StarBound.lean
```

Result: **exit 0** in approximately 6.2 seconds with no output.

A temporary `#print axioms` audit of
`indepNeighborsCard_add_card_add_one_le_b` reported exactly

```text
[propext, Classical.choice, Quot.sound]
```

and was removed afterward.  `sorryAx` and project-specific axioms were absent.
The final source contains no `sorry`, `admit`, or custom `axiom`.

## Remaining boundary

This completes the full induced-star/outside-independent-set lower bound

```text
b(G) >= lambda(v) + 1 + |I|
```

for every independent `I` outside `N[v]`.  Maximizing `I` gives the paper
quantity `alpha(G-N[v])`, although this file deliberately avoids introducing a
second outside-graph invariant merely to rename an already explicit witness.

It does not prove WOWII 19.  The proof ladder still needs:

1. the finite-maximum normalization of
   `sSup (Set.range (indepNeighbors G))`;
2. a no-`sorry` proof of the solved WOWII 13 diameter baseline;
3. the non-self-centered average-eccentricity floor reduction; and
4. the self-centered outside-independent-set lemma identified in
   `method_v07_19_proof_ladder.md`.

No source status, novelty, or upstream claim follows from this local rung.
