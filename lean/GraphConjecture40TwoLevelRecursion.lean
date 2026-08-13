import GraphConjecture40IncludeBranchRecurrence

/-!
# WOWII 40: two-level block-tree recursion

This file iterates the separator recurrence once on the cut-deleted remainder.
It also composes two allocated leaf paths, matching two feedback-successor
steps with two rank increments.
-/

namespace WrittenOnTheWallII.GraphConjecture40TwoLevelRecursion

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
open WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence
open WrittenOnTheWallII.GraphConjecture40IncludeBranchRecurrence

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V}

/-- Applying the separator recurrence twice: after an outer exclude step, the
remainder either takes a second exclude step (two total feedback units), or
splits additively through its include branch (plus the outer unit). -/
theorem feedbackDeletion_two_level_recursive_dichotomy
    (D : OneVertexSeparation G)
    (hdom : includeStateSum D ≤ excludeStateSum D)
    (D₂ : OneVertexSeparation
      (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut)) :
    (GraphConjecture40Deficiency.feedbackDeletion G =
      GraphConjecture40Deficiency.feedbackDeletion
        (GraphConjecture40FeedbackRecursion.deleteVertex
          (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut) D₂.cut) + 2) ∨
    (GraphConjecture40Deficiency.feedbackDeletion G =
      includeDeficiency
          ((GraphConjecture40FeedbackRecursion.deleteVertex G D.cut).induce
            (↑D₂.left : Set {x : V // x ≠ D.cut}))
          ⟨D₂.cut, D₂.cut_mem_left⟩ +
        includeDeficiency
          ((GraphConjecture40FeedbackRecursion.deleteVertex G D.cut).induce
            (↑D₂.right : Set {x : V // x ≠ D.cut}))
          ⟨D₂.cut, D₂.cut_mem_right⟩ + 1) := by
  have hout :=
    WrittenOnTheWallII.GraphConjecture40RecursiveLeafStep.feedbackDeletion_eq_succ_of_exclude_dominates
      D hdom
  rcases feedbackDeletion_recursive_dichotomy D₂ with hinner | hinner
  · left
    omega
  · right
    omega

/-- Two exclude-dominant separators give an exact two-unit feedback
recurrence. -/
theorem feedbackDeletion_eq_add_two_of_two_exclude_steps
    (D : OneVertexSeparation G)
    (hdom : includeStateSum D ≤ excludeStateSum D)
    (D₂ : OneVertexSeparation
      (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut))
    (hdom₂ : includeStateSum D₂ ≤ excludeStateSum D₂) :
    GraphConjecture40Deficiency.feedbackDeletion G =
      GraphConjecture40Deficiency.feedbackDeletion
        (GraphConjecture40FeedbackRecursion.deleteVertex
          (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut) D₂.cut) + 2 := by
  have hout :=
    WrittenOnTheWallII.GraphConjecture40RecursiveLeafStep.feedbackDeletion_eq_succ_of_exclude_dominates
      D hdom
  have hinner :=
    WrittenOnTheWallII.GraphConjecture40RecursiveLeafStep.feedbackDeletion_eq_succ_of_exclude_dominates
      D₂ hdom₂
  omega

/-- Two recursive leaf allocations match two feedback-successor steps. The
first path raises the target from `2*k+1` to `2*(k+1)+1`; the second raises it
to `2*(k+2)+1`. -/
theorem two_exclude_steps_feedback_and_rank
    (D : OneVertexSeparation G)
    (hdom : includeStateSum D ≤ excludeStateSum D)
    (D₂ : OneVertexSeparation
      (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut))
    (hdom₂ : includeStateSum D₂ ≤ excludeStateSum D₂)
    {k : ℕ}
    (hbase : GraphConjecture40Deficiency.feedbackDeletion
      (GraphConjecture40FeedbackRecursion.deleteVertex
        (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut) D₂.cut) = k)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (L₁ : GraphConjecture40LeafBlockStep.LeafBlockStep G P)
    (L₂ : GraphConjecture40LeafBlockStep.LeafBlockStep G
      (insert L₁.support P)) :
    GraphConjecture40Deficiency.feedbackDeletion G = k + 2 ∧
      (insert L₂.support (insert L₁.support P)).card +
          (2 * (k + 2) + 1) ≤
        (GraphConjecture40PathFamily.coveredVertices
          (insert L₂.support (insert L₁.support P))).card := by
  have htau := feedbackDeletion_eq_add_two_of_two_exclude_steps
    D hdom D₂ hdom₂
  have hP₁ := L₁.insert_isPathSupportFamily hP
  have hrank₁ := L₁.rank_step hP hrank
  have hrank₂ := L₂.rank_step hP₁ hrank₁
  constructor
  · omega
  · omega

/-- End-to-end depth-two recursive block-tree theorem for bipartite graphs. -/
theorem conjecture40_of_bipartite_of_two_exclude_leaf_steps
    (D : OneVertexSeparation G) (hG : G.IsBipartite)
    (hdom : includeStateSum D ≤ excludeStateSum D)
    (D₂ : OneVertexSeparation
      (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut))
    (hdom₂ : includeStateSum D₂ ≤ excludeStateSum D₂)
    {k : ℕ}
    (hbase : GraphConjecture40Deficiency.feedbackDeletion
      (GraphConjecture40FeedbackRecursion.deleteVertex
        (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut) D₂.cut) = k)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (L₁ : GraphConjecture40LeafBlockStep.LeafBlockStep G P)
    (L₂ : GraphConjecture40LeafBlockStep.LeafBlockStep G
      (insert L₁.support P)) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hpair := two_exclude_steps_feedback_and_rank
    D hdom D₂ hdom₂ hbase P hP hrank L₁ L₂
  have hP₁ := L₁.insert_isPathSupportFamily hP
  have hP₂ := L₂.insert_isPathSupportFamily hP₁
  exact GraphConjecture40PathFamily.conjecture40_of_bipartite_of_pathFamily_rank
    G hG hpair.1 _ hP₂ hpair.2

end WrittenOnTheWallII.GraphConjecture40TwoLevelRecursion
