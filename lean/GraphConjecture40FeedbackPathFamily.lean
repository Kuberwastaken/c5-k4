import GraphConjecture40PathFamily

/-!
# WOWII 40: feedback-sized path families

The one-long-path condition is not universal: cycle petals joined through a
cut vertex can force large feedback deletion while every simple path meets at
most two petals.  This file gives a multi-component replacement.  At
feedback coordinate `k`, `k+1` disjoint paths of order at least three already
have rank at least `2k+2`, one more than WOWII 40 requires.
-/

namespace WrittenOnTheWallII.GraphConjecture40FeedbackPathFamily

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- Pairwise-disjoint path supports have union cardinality equal to the sum
of their cardinalities. -/
lemma card_coveredVertices_eq_sum
    (G : SimpleGraph V) (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P) :
    (GraphConjecture40PathFamily.coveredVertices P).card =
      ∑ s ∈ P, s.card := by
  unfold GraphConjecture40PathFamily.coveredVertices
  apply Finset.card_biUnion
  intro s hs t ht hne
  exact hP.1 s hs t ht hne

omit [Fintype V] in
/-- If every path component has at least three vertices, the total path
family rank is at least twice the number of components. -/
lemma two_mul_card_le_pathFamily_rank
    (G : SimpleGraph V) (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hthree : ∀ s ∈ P, 3 ≤ s.card) :
    P.card + 2 * P.card ≤
      (GraphConjecture40PathFamily.coveredVertices P).card := by
  rw [card_coveredVertices_eq_sum G P hP]
  have hsum : ∑ s ∈ P, 3 ≤ ∑ s ∈ P, s.card := by
    exact Finset.sum_le_sum fun s hs ↦ hthree s hs
  have : P.card * 3 ≤ ∑ s ∈ P, s.card := by simpa using hsum
  omega

/-- A feedback-sized family of three-vertex paths is a sufficient structural
class for the bipartite base. -/
theorem conjecture40_of_bipartite_of_feedback_sized_three_vertex_paths
    (G : SimpleGraph V) (hG : G.IsBipartite)
    {k : ℕ}
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = k)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hsize : P.card = k + 1)
    (hthree : ∀ s ∈ P, 3 ≤ s.card) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  apply GraphConjecture40PathFamily.conjecture40_of_bipartite_of_pathFamily_rank
    G hG htau P hP
  have hrank := two_mul_card_le_pathFamily_rank G P hP hthree
  omega

/-- A slightly sharper variant: `k` three-vertex paths plus one disjoint edge
pay exactly the required rank `2k+1`. -/
theorem conjecture40_of_bipartite_of_k_short_paths_and_one_edge
    (G : SimpleGraph V) (hG : G.IsBipartite)
    {k : ℕ}
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = k)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hcomponents : P.card = k + 1)
    (hsmall : ∀ s ∈ P, 2 ≤ s.card)
    (hbonus : ∃ Q ⊆ P, Q.card = k ∧ ∀ s ∈ Q, 3 ≤ s.card) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  obtain ⟨Q, hQP, hQcard, hQthree⟩ := hbonus
  apply GraphConjecture40PathFamily.conjecture40_of_bipartite_of_pathFamily_rank
    G hG htau P hP
  rw [card_coveredVertices_eq_sum G P hP]
  have hbase : ∑ s ∈ P, 2 ≤ ∑ s ∈ P, s.card :=
    Finset.sum_le_sum fun s hs ↦ hsmall s hs
  have hbonusSum : Q.card ≤ ∑ s ∈ Q, (s.card - 2) := by
    have : ∑ s ∈ Q, 1 ≤ ∑ s ∈ Q, (s.card - 2) :=
      Finset.sum_le_sum fun s hs ↦ by
        have := hQthree s hs
        omega
    simpa using this
  have hsurplus : ∑ s ∈ Q, (s.card - 2) ≤
      ∑ s ∈ P, (s.card - 2) := by
    exact Finset.sum_le_sum_of_subset_of_nonneg hQP fun _ _ _ ↦ Nat.zero_le _
  have htotal : 2 * P.card + Q.card ≤ ∑ s ∈ P, s.card := by
    have hdecomp : ∑ s ∈ P, s.card =
        2 * P.card + ∑ s ∈ P, (s.card - 2) := by
      calc
        _ = ∑ s ∈ P, (2 + (s.card - 2)) := by
          apply Finset.sum_congr rfl
          intro s hs
          have := hsmall s hs
          omega
        _ = _ := by simp [Finset.sum_add_distrib, Nat.mul_comm]
    rw [hdecomp]
    omega
  omega

end WrittenOnTheWallII.GraphConjecture40FeedbackPathFamily
