import GraphConjecture40SharedCenterFlowers

/-!
# WOWII 40: one recursive leaf-block step

A cyclic leaf block can be allocated away from its parent cut vertex and
harvested as a path of order at least three.  If that path is disjoint from a
certificate for the remaining graph, inserting it raises path-family rank by
at least two, exactly paying the change `k ↦ k+1` in `2k+1`.
-/

namespace WrittenOnTheWallII.GraphConjecture40LeafBlockStep

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Data for one allocated cyclic leaf block relative to an existing path
family. -/
structure LeafBlockStep (G : SimpleGraph V)
    (P : Finset (Finset V)) where
  support : Finset V
  start : V
  finish : V
  path : G.Walk start finish
  path_isPath : path.IsPath
  support_eq : support = path.support.toFinset
  support_three : 3 ≤ support.card
  disjoint_remainder : Disjoint support
    (GraphConjecture40PathFamily.coveredVertices P)

namespace LeafBlockStep

variable {G : SimpleGraph V} {P : Finset (Finset V)}

omit [Fintype V] in
lemma support_not_mem (L : LeafBlockStep G P) : L.support ∉ P := by
  intro hs
  have hpos : 0 < L.support.card := lt_of_lt_of_le (by decide) L.support_three
  obtain ⟨x, hx⟩ := Finset.card_pos.mp hpos
  exact Finset.disjoint_left.mp L.disjoint_remainder hx
    (GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
      ⟨L.support, hs, hx⟩)

omit [Fintype V] in
/-- Inserting the allocated leaf path preserves the path-family predicate. -/
lemma insert_isPathSupportFamily
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (L : LeafBlockStep G P) :
    GraphConjecture40PathFamily.IsPathSupportFamily G
      (insert L.support P) := by
  refine ⟨?_, ?_⟩
  · intro s hs t ht hne
    simp only [mem_insert] at hs ht
    rcases hs with rfl | hsP
    · rcases ht with hsame | htP
      · exact (hne hsame.symm).elim
      · rw [Finset.disjoint_left]
        intro x hxL hxt
        exact Finset.disjoint_left.mp L.disjoint_remainder hxL
          (GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
            ⟨t, htP, hxt⟩)
    · rcases ht with rfl | htP
      · rw [Finset.disjoint_left]
        intro x hxs hxL
        exact Finset.disjoint_left.mp L.disjoint_remainder hxL
          (GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
            ⟨s, hsP, hxs⟩)
      · exact hP.1 s hsP t htP hne
  · intro s hs
    simp only [mem_insert] at hs
    rcases hs with rfl | hsP
    · exact ⟨L.start, L.finish, L.path, L.path_isPath, L.support_eq⟩
    · exact hP.2 s hsP

omit [Fintype V] in
/-- Exact covered-cardinality increment from one allocated leaf support. -/
lemma covered_insert_card
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (L : LeafBlockStep G P) :
    (GraphConjecture40PathFamily.coveredVertices
      (insert L.support P)).card =
      L.support.card +
        (GraphConjecture40PathFamily.coveredVertices P).card := by
  rw [GraphConjecture40FeedbackPathFamily.card_coveredVertices_eq_sum
    G (insert L.support P) (L.insert_isPathSupportFamily hP)]
  rw [sum_insert L.support_not_mem]
  rw [GraphConjecture40FeedbackPathFamily.card_coveredVertices_eq_sum G P hP]

omit [Fintype V] in
/-- Recursive rank step: a three-vertex leaf path pays the two additional
units required when the feedback coordinate increases from `k` to `k+1`. -/
theorem rank_step
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (L : LeafBlockStep G P) {k : ℕ}
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card) :
    (insert L.support P).card + (2 * (k + 1) + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices
        (insert L.support P)).card := by
  rw [card_insert_of_notMem L.support_not_mem]
  rw [L.covered_insert_card hP]
  have hthree := L.support_three
  omega

end LeafBlockStep

/-- One leaf-block extension closes WOWII 40 at feedback coordinate `k+1`
from a rank certificate at coordinate `k`. -/
theorem conjecture40_of_bipartite_of_leafBlockStep
    (G : SimpleGraph V) (hG : G.IsBipartite)
    {k : ℕ}
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = k + 1)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (L : LeafBlockStep G P) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  apply GraphConjecture40PathFamily.conjecture40_of_bipartite_of_pathFamily_rank
    G hG htau (insert L.support P) (L.insert_isPathSupportFamily hP)
  exact L.rank_step hP hrank

end WrittenOnTheWallII.GraphConjecture40LeafBlockStep
