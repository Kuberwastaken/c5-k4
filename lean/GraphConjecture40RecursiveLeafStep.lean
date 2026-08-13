import GraphConjecture40InducedStateBridge

/-!
# WOWII 40: recursive block-tree leaf step

The subtype bridges turn the separator max-envelope into an actual recursion.
This file identifies the exclude state with the cut-deleted graph and proves
that an exclude-dominant separator raises feedback deletion by one, while an
allocated three-vertex leaf path raises linear-forest rank by two.
-/

namespace WrittenOnTheWallII.GraphConjecture40RecursiveLeafStep

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
open WrittenOnTheWallII.GraphConjecture40SharedCutUnion
open WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V}

/-- Excluding `c` in the ambient graph is the same optimization problem as an
unconstrained induced forest in the vertex-deleted graph. -/
theorem forestOrderExcluding_eq_deleteVertex_largestInducedForestSize
    (G : SimpleGraph V) (c : V) :
    GraphConjecture40CutVertexSum.forestOrderExcluding G c =
      (GraphConjecture40FeedbackRecursion.deleteVertex G c).largestInducedForestSize := by
  have hexWithin :
      GraphConjecture40CutVertexSum.forestOrderExcluding G c =
        forestOrderWithin G (Finset.univ.erase c) := by
    apply le_antisymm
    · obtain ⟨S, hS, hcS, hcard⟩ :=
        GraphConjecture40CutVertexSum.exists_forestOrderExcluding_witness G c
      have hsub : S ⊆ Finset.univ.erase c := by
        intro x hx
        exact mem_erase.mpr ⟨fun hxc => hcS (hxc ▸ hx), mem_univ x⟩
      have hbound := card_le_forestOrderWithin G (Finset.univ.erase c) S
        hsub hS
      omega
    · obtain ⟨S, hsub, hS, hcard⟩ :=
        exists_forestOrderWithin_witness G (Finset.univ.erase c)
      have hcS : c ∉ S := by
        intro hc
        exact (mem_erase.mp (hsub hc)).1 rfl
      have hbound := GraphConjecture40CutVertexSum.card_le_forestOrderExcluding
        G c S hS hcS
      omega
  rw [hexWithin]
  rw [WrittenOnTheWallII.GraphConjecture40InducedStateBridge.forestOrderWithin_eq_induce_largestInducedForestSize]
  have hset : (↑(Finset.univ.erase c) : Set V) = {x | x ≠ c} := by
    ext x
    simp
  rw [hset]
  rfl

/-- If the exclude branch wins the state envelope, the global forest optimum
equals the optimum after deleting the cut. -/
theorem largestInducedForestSize_eq_deleteVertex_of_exclude_dominates
    (D : OneVertexSeparation G)
    (hdom : includeStateSum D ≤ excludeStateSum D) :
    G.largestInducedForestSize =
      (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut).largestInducedForestSize := by
  have henv := largestInducedForestSize_add_one_eq_blockTreeForestRank D
  have hbranch : blockTreeForestRank D = excludeStateSum D := by
    exact max_eq_right hdom
  have hexc :=
    WrittenOnTheWallII.GraphConjecture40SeparatedUnion.OneVertexSeparation.forestOrderExcluding_eq_sum_within_erase D
  have hdelete := forestOrderExcluding_eq_deleteVertex_largestInducedForestSize
    G D.cut
  unfold excludeStateSum at hbranch
  rw [hbranch] at henv
  omega

/-- The complementary include-dominant branch evaluates the global optimum
directly from the two recursively typed include states. -/
theorem largestInducedForestSize_add_one_eq_includeStateSum_of_include_dominates
    (D : OneVertexSeparation G)
    (hdom : excludeStateSum D ≤ includeStateSum D) :
    G.largestInducedForestSize + 1 = includeStateSum D := by
  rw [largestInducedForestSize_add_one_eq_blockTreeForestRank D]
  exact max_eq_left hdom

/-- Exclude-branch dominance is exactly the feedback-deletion successor step
at the separator cut. -/
theorem feedbackDeletion_eq_succ_of_exclude_dominates
    (D : OneVertexSeparation G)
    (hdom : includeStateSum D ≤ excludeStateSum D) :
    GraphConjecture40Deficiency.feedbackDeletion G =
      GraphConjecture40Deficiency.feedbackDeletion
        (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut) + 1 := by
  exact GraphConjecture40FeedbackRecursion.feedbackDeletion_eq_succ_of_forest_eq
    G D.cut (largestInducedForestSize_eq_deleteVertex_of_exclude_dominates D hdom)

/-- Genuine recursive leaf step. If the exclude branch controls the separator,
then feedback deletion changes `k` to `k+1`; simultaneously, inserting an
allocated three-vertex leaf path changes the path-family rank target from
`2*k+1` to `2*(k+1)+1`. -/
theorem exclude_branch_feedback_succ_and_rank_step
    (D : OneVertexSeparation G)
    (hdom : includeStateSum D ≤ excludeStateSum D)
    {k : ℕ}
    (hrem : GraphConjecture40Deficiency.feedbackDeletion
      (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut) = k)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (L : GraphConjecture40LeafBlockStep.LeafBlockStep G P) :
    GraphConjecture40Deficiency.feedbackDeletion G = k + 1 ∧
      (insert L.support P).card + (2 * (k + 1) + 1) ≤
        (GraphConjecture40PathFamily.coveredVertices
          (insert L.support P)).card := by
  constructor
  · rw [feedbackDeletion_eq_succ_of_exclude_dominates D hdom, hrem]
  · exact L.rank_step hP hrank

/-- End-to-end recursive leaf theorem for bipartite graphs. The separator
branch condition discharges the forest-equality premise, and the allocated
leaf path supplies the matching linear-forest rank increment. -/
theorem conjecture40_of_bipartite_of_exclude_dominant_leaf
    (D : OneVertexSeparation G) (hG : G.IsBipartite)
    (hdom : includeStateSum D ≤ excludeStateSum D)
    {k : ℕ}
    (hrem : GraphConjecture40Deficiency.feedbackDeletion
      (GraphConjecture40FeedbackRecursion.deleteVertex G D.cut) = k)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (L : GraphConjecture40LeafBlockStep.LeafBlockStep G P) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hforest :=
    largestInducedForestSize_eq_deleteVertex_of_exclude_dominates D hdom
  exact GraphConjecture40FeedbackRecursion.conjecture40_of_independent_feedback_leaf
    G hG D.cut hrem hforest P hP hrank L

end WrittenOnTheWallII.GraphConjecture40RecursiveLeafStep
