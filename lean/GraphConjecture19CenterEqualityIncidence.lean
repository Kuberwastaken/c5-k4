import GraphConjecture19CenterCharge

/-!
# WOWII 19/13: incidence form of the center equality obstruction
-/

namespace WrittenOnTheWallII.GraphConjecture19CenterEqualityIncidence

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19EndpointMax
open WrittenOnTheWallII.GraphConjecture19StarBound
open WrittenOnTheWallII.GraphConjecture19CenterCharge

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [DecidableEq V] in
/-- If the local neighborhood independence number equals the degree, the
entire open neighborhood is independent. -/
theorem neighborSet_independent_of_indepNeighborsCard_eq_degree
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V)
    (hfull : indepNeighborsCard G v = G.degree v) :
    G.IsIndepSet (G.neighborSet v) := by
  obtain ⟨A, hAindep, hAN, hAcard⟩ := exists_local_indep_witness G v
  have hNcard : (G.neighborFinset v).card = G.degree v :=
    G.card_neighborFinset_eq_degree v
  have hEq : A = G.neighborFinset v := by
    apply Finset.eq_of_subset_of_card_le hAN
    rw [hNcard, hAcard, hfull]
  intro x hx y hy hxy hxyAdj
  apply hAindep
  · simpa [hEq, mem_neighborFinset] using hx
  · simpa [hEq, mem_neighborFinset] using hy
  · exact hxy
  · exact hxyAdj

/-- Under a saturated path/neighborhood cover, a fully independent center
neighborhood makes every vertex outside the path part of one independent
set. -/
theorem path_complement_independent_of_saturation
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (P : Finset V) (c : V)
    (hsat : P ∪ G.neighborFinset c = Finset.univ)
    (hcenter : G.IsIndepSet (G.neighborSet c)) :
    G.IsIndepSet (↑(Finset.univ \ P) : Set V) := by
  have hsub : (↑(Finset.univ \ P) : Set V) ⊆ G.neighborSet c := by
    intro x hx
    have hxDiff := Finset.mem_sdiff.mp hx
    have hxCover : x ∈ P ∪ G.neighborFinset c := by
      rw [hsat]
      simp
    rcases Finset.mem_union.mp hxCover with hxP | hxN
    · exact (hxDiff.2 hxP).elim
    · simpa [mem_neighborFinset] using hxN
  intro x hx y hy hxy hxyAdj
  exact hcenter (hsub hx) (hsub hy) hxy hxyAdj

/-- Exact incidence split for the center equality obstruction.  Either WOWII
13 already follows, or the saturated center neighborhood and every off-path
vertex form independent sets, or the full-independent maximum neighborhood
occurs at a distinct maximum-degree vertex. -/
theorem wowii13_or_center_independent_cover_or_distinct_full_maxNeighborhood
    {G : SimpleGraph V} [Nonempty V] [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (c : V) (P : Finset V)
    (hconn : G.Connected)
    (hc : D.extraLeft = c ∨ D.extraRight = c)
    (hsat : P ∪ G.neighborFinset c = Finset.univ) :
    ((G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G) ∨
      (G.IsIndepSet (G.neighborSet c) ∧
        G.IsIndepSet (↑(Finset.univ \ P) : Set V)) ∨
      ∃ v : V, v ≠ c ∧
        G.degree v = G.maxDegree ∧
        G.IsIndepSet (G.neighborSet v) := by
  rcases wowii13_or_exists_full_independent_maxNeighborhood_of_center_endpoint
      D c hconn hc with hwow | hobstruction
  · exact Or.inl hwow
  · obtain ⟨v, hvDegree, hvFull⟩ := hobstruction
    have hvIndep := neighborSet_independent_of_indepNeighborsCard_eq_degree
      G v hvFull
    by_cases hvc : v = c
    · subst v
      exact Or.inr (Or.inl ⟨hvIndep,
        path_complement_independent_of_saturation G P c hsat hvIndep⟩)
    · exact Or.inr (Or.inr ⟨v, hvc, hvDegree, hvIndep⟩)

end WrittenOnTheWallII.GraphConjecture19CenterEqualityIncidence
