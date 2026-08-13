import GraphConjecture40RecursiveLeafStep

/-!
# WOWII 40: include-dominant block-tree recurrence

The exclude-dominant branch pays one feedback unit at the cut.  This file
handles the complementary branch: when the optimum contains the cut, feedback
deletion is additive across the two recursively typed induced sides, using an
include-constrained deficiency on each side.
-/

namespace WrittenOnTheWallII.GraphConjecture40IncludeBranchRecurrence

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
open WrittenOnTheWallII.GraphConjecture40SharedCutUnion
open WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V}

/-- Feedback deficiency of a finite graph when an induced forest is required
to contain a designated vertex. -/
noncomputable def includeDeficiency
    {W : Type*} [Fintype W] (H : SimpleGraph W) (c : W) : ℕ :=
  Fintype.card W -
    GraphConjecture40CutVertexSum.forestOrderIncluding H c

omit [Fintype V] [DecidableEq V] in
/-- The induced graph on a finset has that finset's cardinality. -/
lemma card_induce_finset (A : Finset V) :
    Fintype.card ↥(↑A : Set V) = A.card := by
  simp

/-- In the include-dominant branch, feedback deletion is exactly additive
across the two recursively typed side graphs. -/
theorem feedbackDeletion_eq_add_includeDeficiencies_of_include_dominates
    (D : OneVertexSeparation G)
    (hdom : excludeStateSum D ≤ includeStateSum D) :
    GraphConjecture40Deficiency.feedbackDeletion G =
      includeDeficiency (G.induce (↑D.left : Set V))
          ⟨D.cut, D.cut_mem_left⟩ +
        includeDeficiency (G.induce (↑D.right : Set V))
          ⟨D.cut, D.cut_mem_right⟩ := by
  have hinc :=
    WrittenOnTheWallII.GraphConjecture40RecursiveLeafStep.largestInducedForestSize_add_one_eq_includeStateSum_of_include_dominates D hdom
  have hcard := card_left_add_card_right_eq_card_add_one D
  have hleft :=
    WrittenOnTheWallII.GraphConjecture40InducedStateBridge.forestOrderWithinIncluding_eq_induce_forestOrderIncluding
      G D.left D.cut D.cut_mem_left
  have hright :=
    WrittenOnTheWallII.GraphConjecture40InducedStateBridge.forestOrderWithinIncluding_eq_induce_forestOrderIncluding
      G D.right D.cut D.cut_mem_right
  have hforest := GraphConjecture40Deficiency.largestInducedForestSize_le_card G
  have hincLeft :
      GraphConjecture40CutVertexSum.forestOrderIncluding
          (G.induce (↑D.left : Set V)) ⟨D.cut, D.cut_mem_left⟩ ≤
        D.left.card := by
    obtain ⟨S, -, -, hSCard⟩ :=
      GraphConjecture40CutVertexSum.exists_forestOrderIncluding_witness
        (G.induce (↑D.left : Set V)) ⟨D.cut, D.cut_mem_left⟩
    rw [← hSCard, ← card_induce_finset D.left]
    exact S.card_le_univ
  have hincRight :
      GraphConjecture40CutVertexSum.forestOrderIncluding
          (G.induce (↑D.right : Set V)) ⟨D.cut, D.cut_mem_right⟩ ≤
        D.right.card := by
    obtain ⟨S, -, -, hSCard⟩ :=
      GraphConjecture40CutVertexSum.exists_forestOrderIncluding_witness
        (G.induce (↑D.right : Set V)) ⟨D.cut, D.cut_mem_right⟩
    rw [← hSCard, ← card_induce_finset D.right]
    exact S.card_le_univ
  unfold includeStateSum at hinc
  unfold includeDeficiency GraphConjecture40Deficiency.feedbackDeletion
  rw [card_induce_finset D.left, card_induce_finset D.right]
  omega

/-- The max envelope yields a complete recursive dichotomy. Either deleting
the cut lowers the feedback coordinate by exactly one, or the coordinate is
the sum of the two side include-deficiencies. Ties legitimately satisfy both
descriptions; the disjunction records the branch available for induction. -/
theorem feedbackDeletion_recursive_dichotomy
    (D : OneVertexSeparation G) :
    (GraphConjecture40Deficiency.feedbackDeletion G =
      GraphConjecture40Deficiency.feedbackDeletion
        (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut) + 1) ∨
    (GraphConjecture40Deficiency.feedbackDeletion G =
      includeDeficiency (G.induce (↑D.left : Set V))
          ⟨D.cut, D.cut_mem_left⟩ +
        includeDeficiency (G.induce (↑D.right : Set V))
          ⟨D.cut, D.cut_mem_right⟩) := by
  by_cases hbranch : includeStateSum D ≤ excludeStateSum D
  · exact Or.inl
      (WrittenOnTheWallII.GraphConjecture40RecursiveLeafStep.feedbackDeletion_eq_succ_of_exclude_dominates D hbranch)
  · have hrev : excludeStateSum D ≤ includeStateSum D :=
      Nat.le_of_lt (Nat.lt_of_not_ge hbranch)
    exact Or.inr
      (feedbackDeletion_eq_add_includeDeficiencies_of_include_dominates D hrev)

/-- If one has recursive upper bounds for the two side include-deficiencies,
they add directly to an upper bound for the parent feedback coordinate. -/
theorem feedbackDeletion_le_add_of_include_dominates
    (D : OneVertexSeparation G)
    (hdom : excludeStateSum D ≤ includeStateSum D)
    {kL kR : ℕ}
    (hL : includeDeficiency (G.induce (↑D.left : Set V))
      ⟨D.cut, D.cut_mem_left⟩ ≤ kL)
    (hR : includeDeficiency (G.induce (↑D.right : Set V))
      ⟨D.cut, D.cut_mem_right⟩ ≤ kR) :
    GraphConjecture40Deficiency.feedbackDeletion G ≤ kL + kR := by
  rw [feedbackDeletion_eq_add_includeDeficiencies_of_include_dominates D hdom]
  omega

/-- Exact-coordinate wrapper useful for recursive block-tree induction. -/
theorem feedbackDeletion_eq_add_of_include_dominates
    (D : OneVertexSeparation G)
    (hdom : excludeStateSum D ≤ includeStateSum D)
    {kL kR : ℕ}
    (hL : includeDeficiency (G.induce (↑D.left : Set V))
      ⟨D.cut, D.cut_mem_left⟩ = kL)
    (hR : includeDeficiency (G.induce (↑D.right : Set V))
      ⟨D.cut, D.cut_mem_right⟩ = kR) :
    GraphConjecture40Deficiency.feedbackDeletion G = kL + kR := by
  rw [feedbackDeletion_eq_add_includeDeficiencies_of_include_dominates D hdom,
    hL, hR]

end WrittenOnTheWallII.GraphConjecture40IncludeBranchRecurrence
