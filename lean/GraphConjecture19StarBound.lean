import FormalConjecturesUtil

/-!
# WOWII 19: the induced-star lower bound

This file formalizes the first graph-specific rung isolated in
`results/expansion/method_v07_19_proof_ladder.md`.  An independent set in the
open neighborhood of a vertex, the vertex itself, and an independent set
outside its closed neighborhood form an explicitly colored induced bipartite
subgraph.
-/

namespace WrittenOnTheWallII.GraphConjecture19StarBound

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- The induced star and an independent set outside its closed neighborhood
have the explicit bipartition `A | ({v} ∪ I)`. -/
lemma induce_insert_union_isBipartite_of_indep
    (G : SimpleGraph V) (v : V) (A I : Finset V)
    (hA : G.IsIndepSet (A : Set V))
    (hAN : (A : Set V) ⊆ G.neighborSet v)
    (hI : G.IsIndepSet (I : Set V))
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    (G.induce (↑(insert v (A ∪ I)) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  refine ⟨fun x => if x ∈ A then (0 : Fin 2) else 1, ?_⟩
  intro x hx y hy hxy
  by_cases hxA : x ∈ A
  · by_cases hyA : y ∈ A
    · exact (hA hxA hyA hxy.ne hxy).elim
    · simp [hxA, hyA]
  · by_cases hyA : y ∈ A
    · simp [hxA, hyA]
    · exfalso
      have hxvI : x = v ∨ x ∈ I := by
        simp only [mem_insert, mem_union] at hx
        rcases hx with rfl | hxA' | hxI
        · exact Or.inl rfl
        · exact (hxA hxA').elim
        · exact Or.inr hxI
      have hyvI : y = v ∨ y ∈ I := by
        simp only [mem_insert, mem_union] at hy
        rcases hy with rfl | hyA' | hyI
        · exact Or.inl rfl
        · exact (hyA hyA').elim
        · exact Or.inr hyI
      rcases hxvI with rfl | hxI <;> rcases hyvI with rfl | hyI
      · exact G.loopless _ hxy
      · exact (hIout y hyI).2 hxy
      · exact (hIout x hxI).2 hxy.symm
      · exact hI hxI hyI hxy.ne hxy

omit [Fintype V] in
/-- The explicit induced bipartite witness retains the exact sum of the two
independent-set cardinalities and the center vertex. -/
lemma card_insert_union_eq
    (G : SimpleGraph V) (v : V) (A I : Finset V)
    (hAN : (A : Set V) ⊆ G.neighborSet v)
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    (insert v (A ∪ I)).card = A.card + I.card + 1 := by
  have hAI : Disjoint A I := by
    rw [Finset.disjoint_left]
    intro x hxA hxI
    exact (hIout x hxI).2 (hAN hxA)
  have hvA : v ∉ A := by
    intro hvA
    exact G.loopless v (hAN hvA)
  have hvI : v ∉ I := by
    intro hvI
    exact (hIout v hvI).1 rfl
  rw [card_insert_of_notMem]
  · rw [card_union_of_disjoint hAI]
  · simp [hvA, hvI]

omit [DecidableEq V] in
/-- Any explicit induced bipartite witness bounds the repository's `sSup`
definition of largest induced bipartite order. -/
lemma card_le_largestInducedBipartiteSubgraphSize
    (G : SimpleGraph V) (S : Finset V)
    (hS : (G.induce (↑S : Set V)).IsBipartite) :
    S.card ≤ G.largestInducedBipartiteSubgraphSize := by
  unfold largestInducedBipartiteSubgraphSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n ⟨T, _hT, hn⟩ ↦ hn ▸ T.card_le_univ⟩
  · exact ⟨S, hS, rfl⟩

/-- Natural-number form of the induced-star/outside-independent-set lower
bound, before maximizing either independent set. -/
theorem card_add_card_add_one_le_largestInducedBipartiteSubgraphSize
    (G : SimpleGraph V) (v : V) (A I : Finset V)
    (hA : G.IsIndepSet (A : Set V))
    (hAN : (A : Set V) ⊆ G.neighborSet v)
    (hI : G.IsIndepSet (I : Set V))
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    A.card + I.card + 1 ≤ G.largestInducedBipartiteSubgraphSize := by
  let S := insert v (A ∪ I)
  have hSbip : (G.induce (↑S : Set V)).IsBipartite := by
    exact induce_insert_union_isBipartite_of_indep G v A I hA hAN hI hIout
  have hScard : S.card = A.card + I.card + 1 := by
    exact card_insert_union_eq G v A I hAN hIout
  rw [← hScard]
  exact card_le_largestInducedBipartiteSubgraphSize G S hSbip

/-- Real-valued `b G` form of the explicit-cardinality lower bound. -/
theorem card_add_card_add_one_le_b
    (G : SimpleGraph V) (v : V) (A I : Finset V)
    (hA : G.IsIndepSet (A : Set V))
    (hAN : (A : Set V) ⊆ G.neighborSet v)
    (hI : G.IsIndepSet (I : Set V))
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    ((A.card + I.card + 1 : ℕ) : ℝ) ≤ b G := by
  unfold b
  exact_mod_cast
    card_add_card_add_one_le_largestInducedBipartiteSubgraphSize
      G v A I hA hAN hI hIout

omit [DecidableEq V] in
/-- A maximum independent set in the induced open neighborhood, mapped back
to ambient vertices.  The cardinality equality is retained for later use. -/
lemma exists_local_indep_witness (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    ∃ A : Finset V,
      G.IsIndepSet (A : Set V) ∧
      A ⊆ G.neighborFinset v ∧
      A.card = indepNeighborsCard G v := by
  classical
  let H := G.induce (G.neighborSet v)
  obtain ⟨S, hS⟩ := H.exists_isNIndepSet_indepNum
  let A : Finset V := S.map (Function.Embedding.subtype _)
  refine ⟨A, ?_, ?_, ?_⟩
  · intro x hx y hy hxy hxyAdj
    rw [Finset.mem_coe] at hx hy
    obtain ⟨x', hx'S, hx'eq⟩ := Finset.mem_map.mp hx
    obtain ⟨y', hy'S, hy'eq⟩ := Finset.mem_map.mp hy
    subst x
    subst y
    apply hS.isIndepSet hx'S hy'S
    · exact fun h => hxy (congrArg Subtype.val h)
    · exact hxyAdj
  · intro x hx
    obtain ⟨x', _hx'S, hx'eq⟩ := Finset.mem_map.mp hx
    rw [← hx'eq, mem_neighborFinset]
    exact x'.property
  · rw [Finset.card_map, hS.card_eq]
    rfl

/-- The requested invariant-native natural-number star bound: a maximum
independent set in `N(v)` can be combined with any independent set outside
`N[v]`. -/
theorem indepNeighborsCard_add_card_add_one_le_largestInducedBipartiteSubgraphSize
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) (I : Finset V)
    (hI : G.IsIndepSet (I : Set V))
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    indepNeighborsCard G v + I.card + 1 ≤
      G.largestInducedBipartiteSubgraphSize := by
  obtain ⟨A, hA, hAN, hAcard⟩ := exists_local_indep_witness G v
  rw [← hAcard]
  exact card_add_card_add_one_le_largestInducedBipartiteSubgraphSize
    G v A I hA (by
      intro x hx
      rw [← coe_neighborFinset]
      exact hAN hx) hI hIout

/-- The same maximum-local-star bound in the real-valued upstream notation
`b G`. -/
theorem indepNeighborsCard_add_card_add_one_le_b
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) (I : Finset V)
    (hI : G.IsIndepSet (I : Set V))
    (hIout : ∀ x ∈ I, x ≠ v ∧ ¬G.Adj v x) :
    ((indepNeighborsCard G v + I.card + 1 : ℕ) : ℝ) ≤ b G := by
  unfold b
  exact_mod_cast
    indepNeighborsCard_add_card_add_one_le_largestInducedBipartiteSubgraphSize
      G v I hI hIout

end WrittenOnTheWallII.GraphConjecture19StarBound
