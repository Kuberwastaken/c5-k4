import GraphConjecture40FiniteExcludeRecursion

/-!
# WOWII 40: include-branch path-rank composition

At an include-dominant separator, feedback deficiency is the sum of two side
include-deficiencies. This file gives the matching path-family composition:
after allocating the shared cut so the lifted side families are disjoint, the
two rank surpluses add and pay the parent target.
-/

namespace WrittenOnTheWallII.GraphConjecture40IncludeRankComposition

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
open WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence
open WrittenOnTheWallII.GraphConjecture40IncludeBranchRecurrence

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V}

/-- Compatibility data for joining two ambient-lifted path families. In a
block-tree application this is discharged by allocating the shared cut to at
most one side. -/
structure PathFamilyJoin (G : SimpleGraph V)
    (P Q : Finset (Finset V)) : Prop where
  family_disjoint : Disjoint P Q
  cross_disjoint : ∀ s ∈ P, ∀ t ∈ Q, Disjoint s t

namespace PathFamilyJoin

omit [Fintype V] in
/-- Compatible path families remain a path-support family after union. -/
theorem union_isPathSupportFamily
    {P Q : Finset (Finset V)}
    (J : PathFamilyJoin G P Q)
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hQ : GraphConjecture40PathFamily.IsPathSupportFamily G Q) :
    GraphConjecture40PathFamily.IsPathSupportFamily G (P ∪ Q) := by
  constructor
  · intro s hs t ht hne
    rcases mem_union.mp hs with hsP | hsQ
    · rcases mem_union.mp ht with htP | htQ
      · exact hP.1 s hsP t htP hne
      · exact J.cross_disjoint s hsP t htQ
    · rcases mem_union.mp ht with htP | htQ
      · exact (J.cross_disjoint t htP s hsQ).symm
      · exact hQ.1 s hsQ t htQ hne
  · intro s hs
    rcases mem_union.mp hs with hsP | hsQ
    · exact hP.2 s hsP
    · exact hQ.2 s hsQ

omit [Fintype V] in
/-- Covered vertices commute with union of support families. -/
lemma coveredVertices_union (P Q : Finset (Finset V)) :
    GraphConjecture40PathFamily.coveredVertices (P ∪ Q) =
      GraphConjecture40PathFamily.coveredVertices P ∪
        GraphConjecture40PathFamily.coveredVertices Q := by
  ext x
  constructor
  · intro hx
    obtain ⟨s, hs, hxs⟩ :=
      GraphConjecture40PathFamily.mem_coveredVertices_iff.mp hx
    rcases mem_union.mp hs with hsP | hsQ
    · exact mem_union_left _
        (GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
          ⟨s, hsP, hxs⟩)
    · exact mem_union_right _
        (GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
          ⟨s, hsQ, hxs⟩)
  · intro hx
    rcases mem_union.mp hx with hxP | hxQ
    · obtain ⟨s, hsP, hxs⟩ :=
        GraphConjecture40PathFamily.mem_coveredVertices_iff.mp hxP
      exact GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
        ⟨s, mem_union_left Q hsP, hxs⟩
    · obtain ⟨s, hsQ, hxs⟩ :=
        GraphConjecture40PathFamily.mem_coveredVertices_iff.mp hxQ
      exact GraphConjecture40PathFamily.mem_coveredVertices_iff.mpr
        ⟨s, mem_union_right P hsQ, hxs⟩

omit [Fintype V] in
/-- Cross-disjoint supports give disjoint covered-vertex sets. -/
lemma coveredVertices_disjoint
    {P Q : Finset (Finset V)} (J : PathFamilyJoin G P Q) :
    Disjoint (GraphConjecture40PathFamily.coveredVertices P)
      (GraphConjecture40PathFamily.coveredVertices Q) := by
  rw [Finset.disjoint_left]
  intro x hxP hxQ
  obtain ⟨s, hsP, hxs⟩ :=
    GraphConjecture40PathFamily.mem_coveredVertices_iff.mp hxP
  obtain ⟨t, htQ, hxt⟩ :=
    GraphConjecture40PathFamily.mem_coveredVertices_iff.mp hxQ
  exact Finset.disjoint_left.mp (J.cross_disjoint s hsP t htQ) hxs hxt

omit [Fintype V] in
/-- Exact cardinality addition for a compatible family join. -/
theorem union_card_and_covered_card
    {P Q : Finset (Finset V)} (J : PathFamilyJoin G P Q) :
    (P ∪ Q).card = P.card + Q.card ∧
      (GraphConjecture40PathFamily.coveredVertices (P ∪ Q)).card =
        (GraphConjecture40PathFamily.coveredVertices P).card +
          (GraphConjecture40PathFamily.coveredVertices Q).card := by
  constructor
  · exact card_union_of_disjoint J.family_disjoint
  · rw [coveredVertices_union]
    exact card_union_of_disjoint J.coveredVertices_disjoint

omit [Fintype V] in
/-- Exact include-branch rank composition. Two side certificates at targets
`2*kL+1` and `2*kR+1` give the parent target `2*(kL+kR)+1`; in fact their
disjoint union has one unit of spare surplus. -/
theorem union_rank
    {P Q : Finset (Finset V)} (J : PathFamilyJoin G P Q)
    {kL kR : ℕ}
    (hPL : P.card + (2 * kL + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (hQR : Q.card + (2 * kR + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices Q).card) :
    (P ∪ Q).card + (2 * (kL + kR) + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices (P ∪ Q)).card := by
  obtain ⟨hcard, hcovered⟩ := J.union_card_and_covered_card
  omega

end PathFamilyJoin

/-- End-to-end include-dominant composition theorem. Recursive side values
determine the parent feedback coordinate, while compatible lifted side path
families combine to meet its linear-forest rank target. -/
theorem conjecture40_of_bipartite_of_include_branch_join
    (D : OneVertexSeparation G) (hG : G.IsBipartite)
    (hdom : excludeStateSum D ≤ includeStateSum D)
    {kL kR : ℕ}
    (hL : includeDeficiency (G.induce (↑D.left : Set V))
      ⟨D.cut, D.cut_mem_left⟩ = kL)
    (hR : includeDeficiency (G.induce (↑D.right : Set V))
      ⟨D.cut, D.cut_mem_right⟩ = kR)
    (P Q : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hQ : GraphConjecture40PathFamily.IsPathSupportFamily G Q)
    (J : PathFamilyJoin G P Q)
    (hPL : P.card + (2 * kL + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (hQR : Q.card + (2 * kR + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices Q).card) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have htau := feedbackDeletion_eq_add_of_include_dominates
    D hdom hL hR
  exact GraphConjecture40PathFamily.conjecture40_of_bipartite_of_pathFamily_rank
    G hG htau (P ∪ Q) (J.union_isPathSupportFamily hP hQ)
      (J.union_rank hPL hQR)

end WrittenOnTheWallII.GraphConjecture40IncludeRankComposition
