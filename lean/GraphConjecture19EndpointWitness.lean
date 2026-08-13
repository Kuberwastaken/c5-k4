import GraphConjecture19StarBound
import GraphConjecture19DiameterBaseline

/-!
# WOWII 19/13: explicit endpoint witness assembly

This file closes the finite-union, coloring, cardinality, and `b`-insertion
plumbing for the diametral-endpoint construction.  The retained geodesic tail
is represented by a finite set `Q` carrying its alternating coloring.
-/

namespace WrittenOnTheWallII.GraphConjecture19EndpointWitness

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- An independent attachment layer and an explicitly colored retained tail
give a bipartite induced graph on their union. -/
lemma induce_union_isBipartite_of_colored_attachment
    (G : SimpleGraph V) (A Q : Finset V) (c : V → Fin 2)
    (hA : G.IsIndepSet (A : Set V))
    (hQ : ∀ x ∈ Q, ∀ y ∈ Q, G.Adj x y → c x ≠ c y)
    (hcross : ∀ a ∈ A, ∀ q ∈ Q, G.Adj a q → c q ≠ 0) :
    (G.induce (↑(A ∪ Q) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  refine ⟨fun x => if x ∈ A then 0 else c x, ?_⟩
  intro x hx y hy hxy
  simp only [mem_union] at hx hy
  by_cases hxA : x ∈ A
  · by_cases hyA : y ∈ A
    · exact (hA hxA hyA hxy.ne hxy).elim
    · have hyQ : y ∈ Q := hy.resolve_left hyA
      simp only [if_pos hxA, if_neg hyA]
      exact Ne.symm (hcross x hxA y hyQ hxy)
  · have hxQ : x ∈ Q := hx.resolve_left hxA
    by_cases hyA : y ∈ A
    · simp only [if_neg hxA, if_pos hyA]
      exact hcross y hyA x hxQ hxy.symm
    · have hyQ : y ∈ Q := hy.resolve_left hyA
      simp only [if_neg hxA, if_neg hyA]
      exact hQ x hxQ y hyQ hxy

omit [Fintype V] in
/-- Exact cardinality of the assembled endpoint witness. -/
lemma card_union_eq_add_of_disjoint
    (A Q : Finset V) (hdisj : Disjoint A Q) :
    (A ∪ Q).card = A.card + Q.card := by
  exact card_union_of_disjoint hdisj

omit [DecidableEq V] in
/-- Any finite induced bipartite witness inserts into the repository's `sSup`
definition of `b`. -/
lemma card_le_largestInducedBipartiteSubgraphSize
    (G : SimpleGraph V) (S : Finset V)
    (hS : (G.induce (↑S : Set V)).IsBipartite) :
    S.card ≤ G.largestInducedBipartiteSubgraphSize := by
  unfold largestInducedBipartiteSubgraphSize
  apply le_csSup
  · exact ⟨Fintype.card V, fun n ⟨T, _hT, hn⟩ ↦ hn ▸ T.card_le_univ⟩
  · exact ⟨S, hS, rfl⟩

/-- Complete representation theorem: the colored attachment certificate gives
the exact sum lower bound, with no loss at the union or `sSup` steps. -/
theorem card_add_card_le_b_of_colored_attachment
    (G : SimpleGraph V) (A Q : Finset V) (c : V → Fin 2)
    (hA : G.IsIndepSet (A : Set V)) (hdisj : Disjoint A Q)
    (hQ : ∀ x ∈ Q, ∀ y ∈ Q, G.Adj x y → c x ≠ c y)
    (hcross : ∀ a ∈ A, ∀ q ∈ Q, G.Adj a q → c q ≠ 0) :
    (((A.card + Q.card : ℕ) : ℝ)) ≤ b G := by
  have hbip := induce_union_isBipartite_of_colored_attachment
    G A Q c hA hQ hcross
  have hcard := card_le_largestInducedBipartiteSubgraphSize G (A ∪ Q) hbip
  rw [card_union_eq_add_of_disjoint A Q hdisj] at hcard
  unfold b
  exact_mod_cast hcard

/-- Endpoint form.  A maximum independent neighborhood witness and a retained
tail of cardinality `diam(G)` yield the stronger endpoint bound
`b(G) ≥ diam(G) + lambda(u)`. -/
theorem diam_add_indepNeighborsCard_le_b_of_endpoint_certificate
    (G : SimpleGraph V) [DecidableRel G.Adj] (u : V)
    (Q : Finset V) (c : V → Fin 2)
    (hQcard : Q.card = G.diam)
    (hQoutside : ∀ q ∈ Q, q = u ∨ ¬G.Adj u q)
    (hQ : ∀ x ∈ Q, ∀ y ∈ Q, G.Adj x y → c x ≠ c y)
    (hcross : ∀ a ∈ G.neighborFinset u, ∀ q ∈ Q,
      G.Adj a q → c q ≠ 0) :
    (((G.diam + indepNeighborsCard G u : ℕ) : ℝ)) ≤ b G := by
  obtain ⟨A, hA, hAN, hAcard⟩ :=
    _root_.WrittenOnTheWallII.GraphConjecture19StarBound.exists_local_indep_witness G u
  have hdisj : Disjoint A Q := by
    rw [Finset.disjoint_left]
    intro x hxA hxQ
    have hxN : G.Adj u x := by simpa [mem_neighborFinset] using hAN hxA
    rcases hQoutside x hxQ with hxEq | hxnot
    · subst x
      exact G.loopless _ hxN
    · exact hxnot hxN
  have hcrossA : ∀ a ∈ A, ∀ q ∈ Q, G.Adj a q → c q ≠ 0 := by
    intro a ha q hq haq
    exact hcross a (hAN ha) q hq haq
  have hb := card_add_card_le_b_of_colored_attachment
    G A Q c hA hdisj hQ hcrossA
  rw [hAcard, hQcard] at hb
  norm_num at hb ⊢
  linarith

/-- The endpoint certificate also immediately supplies the weaker WOWII 13
shape, losing the harmless final unit. -/
theorem diam_add_indepNeighborsCard_sub_one_le_b_of_endpoint_certificate
    (G : SimpleGraph V) [DecidableRel G.Adj] (u : V)
    (Q : Finset V) (c : V → Fin 2)
    (hQcard : Q.card = G.diam)
    (hQoutside : ∀ q ∈ Q, q = u ∨ ¬G.Adj u q)
    (hQ : ∀ x ∈ Q, ∀ y ∈ Q, G.Adj x y → c x ≠ c y)
    (hcross : ∀ a ∈ G.neighborFinset u, ∀ q ∈ Q,
      G.Adj a q → c q ≠ 0) :
    (((G.diam + indepNeighborsCard G u - 1 : ℕ) : ℝ)) ≤ b G := by
  have hstrong := diam_add_indepNeighborsCard_le_b_of_endpoint_certificate
    G u Q c hQcard hQoutside hQ hcross
  exact le_trans (by exact_mod_cast Nat.sub_le (G.diam + indepNeighborsCard G u) 1) hstrong

end WrittenOnTheWallII.GraphConjecture19EndpointWitness
