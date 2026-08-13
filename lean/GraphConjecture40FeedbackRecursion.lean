import GraphConjecture40LeafBlockStep

/-!
# WOWII 40: exact feedback recursion under vertex deletion

Deleting one vertex changes the ambient order by one.  This file formalizes
the exact arithmetic relationship between feedback deletion before and after
that operation.  In particular, the feedback coordinate drops by one exactly
when the maximum induced-forest order does not grow after restoring the
deleted vertex.
-/

namespace WrittenOnTheWallII.GraphConjecture40FeedbackRecursion

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

def deleteVertex (G : SimpleGraph V) (v : V) : SimpleGraph {x : V // x ≠ v} :=
  G.induce {x | x ≠ v}

/-- The vertex-deleted graph has order one below the original graph. -/
lemma card_deleteVertex (v : V) :
    Fintype.card {x : V // x ≠ v} + 1 = Fintype.card V := by
  have hcomp := Fintype.card_subtype_compl (fun x : V ↦ x = v)
  have hone : Fintype.card {x : V // x = v} = 1 := by
    simp
  have hpos : 0 < Fintype.card V := Fintype.card_pos_iff.mpr ⟨v⟩
  rw [hone] at hcomp
  exact (Nat.sub_add_cancel (by omega : 1 ≤ Fintype.card V) |>.symm.trans
    (congrArg (fun n ↦ n + 1) hcomp).symm).symm

/-- Exact independent-leaf recursion: if restoring `v` does not increase the
maximum induced-forest order, then it raises feedback deletion by one. -/
theorem feedbackDeletion_eq_succ_of_forest_eq
    (G : SimpleGraph V) (v : V)
    (hforest : G.largestInducedForestSize =
      (deleteVertex G v).largestInducedForestSize) :
    GraphConjecture40Deficiency.feedbackDeletion G =
      GraphConjecture40Deficiency.feedbackDeletion (deleteVertex G v) + 1 := by
  have hG := GraphConjecture40Deficiency.largestInducedForestSize_le_card G
  have hH := GraphConjecture40Deficiency.largestInducedForestSize_le_card
    (deleteVertex G v)
  have hn := card_deleteVertex (V := V) v
  unfold GraphConjecture40Deficiency.feedbackDeletion
  omega

/-- Conversely, an exact one-unit feedback drop forces the maximum induced
forest to have the same order on both sides of the deletion. -/
theorem forest_eq_of_feedbackDeletion_eq_succ
    (G : SimpleGraph V) (v : V)
    (htau : GraphConjecture40Deficiency.feedbackDeletion G =
      GraphConjecture40Deficiency.feedbackDeletion (deleteVertex G v) + 1) :
    G.largestInducedForestSize =
      (deleteVertex G v).largestInducedForestSize := by
  have hG := GraphConjecture40Deficiency.largestInducedForestSize_le_card G
  have hH := GraphConjecture40Deficiency.largestInducedForestSize_le_card
    (deleteVertex G v)
  have hn := card_deleteVertex (V := V) v
  unfold GraphConjecture40Deficiency.feedbackDeletion at htau
  omega

/-- Exact characterization of a vertex that pays one feedback unit. -/
theorem feedbackDeletion_eq_succ_iff_forest_eq
    (G : SimpleGraph V) (v : V) :
    GraphConjecture40Deficiency.feedbackDeletion G =
        GraphConjecture40Deficiency.feedbackDeletion (deleteVertex G v) + 1 ↔
      G.largestInducedForestSize =
        (deleteVertex G v).largestInducedForestSize :=
  ⟨forest_eq_of_feedbackDeletion_eq_succ G v,
    feedbackDeletion_eq_succ_of_forest_eq G v⟩

/-- Corrected general recursion. Under the two standard induced-forest
comparison bounds, restoring one vertex either preserves the feedback
coordinate or raises it by exactly one. -/
theorem feedbackDeletion_eq_or_eq_succ
    (G : SimpleGraph V) (v : V)
    (hmono : (deleteVertex G v).largestInducedForestSize ≤
      G.largestInducedForestSize)
    (hgrowth : G.largestInducedForestSize ≤
      (deleteVertex G v).largestInducedForestSize + 1) :
    GraphConjecture40Deficiency.feedbackDeletion G =
        GraphConjecture40Deficiency.feedbackDeletion (deleteVertex G v) ∨
      GraphConjecture40Deficiency.feedbackDeletion G =
        GraphConjecture40Deficiency.feedbackDeletion (deleteVertex G v) + 1 := by
  have hG := GraphConjecture40Deficiency.largestInducedForestSize_le_card G
  have hH := GraphConjecture40Deficiency.largestInducedForestSize_le_card
    (deleteVertex G v)
  have hn := card_deleteVertex (V := V) v
  unfold GraphConjecture40Deficiency.feedbackDeletion
  omega

/-- An independent selected leaf/block step, expressed by forest equality,
supplies the exact feedback recurrence needed by `LeafBlockStep.rank_step`. -/
theorem conjecture40_of_independent_feedback_leaf
    (G : SimpleGraph V) (hG : G.IsBipartite)
    (v : V) {k : ℕ}
    (hrem : GraphConjecture40Deficiency.feedbackDeletion
      (deleteVertex G v) = k)
    (hforest : G.largestInducedForestSize =
      (deleteVertex G v).largestInducedForestSize)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (L : GraphConjecture40LeafBlockStep.LeafBlockStep G P) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have htau : GraphConjecture40Deficiency.feedbackDeletion G = k + 1 := by
    rw [feedbackDeletion_eq_succ_of_forest_eq G v hforest, hrem]
  exact GraphConjecture40LeafBlockStep.conjecture40_of_bipartite_of_leafBlockStep
    G hG htau P hP hrank L

end WrittenOnTheWallII.GraphConjecture40FeedbackRecursion
