import GraphConjecture40SharedCutUnion

/-!
# WOWII 40: one block-tree composition recurrence

The exact include/exclude separator states are combined into a single local
rank.  Its complement in the sum of the two side orders is exactly feedback
deletion.  This identifies the remaining linear-forest obligation at a
one-vertex block-tree composition.
-/

namespace WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
open WrittenOnTheWallII.GraphConjecture40SharedCutUnion

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V}

/-- The include branch counts both side forests, each containing the shared
cut. -/
noncomputable def includeStateSum (D : OneVertexSeparation G) : ℕ :=
  forestOrderWithinIncluding G D.left D.cut +
    forestOrderWithinIncluding G D.right D.cut

/-- The exclude branch receives one bookkeeping unit so that both branches
equal the corresponding global forest order plus one. -/
noncomputable def excludeStateSum (D : OneVertexSeparation G) : ℕ :=
  forestOrderWithin G (D.left.erase D.cut) +
    forestOrderWithin G (D.right.erase D.cut) + 1

/-- Local block-tree forest rank at a one-vertex separator. -/
noncomputable def blockTreeForestRank (D : OneVertexSeparation G) : ℕ :=
  max (includeStateSum D) (excludeStateSum D)

/-- The state-composition rank is exactly the global maximum induced-forest
order, shifted by one for the shared-cut bookkeeping convention. -/
theorem largestInducedForestSize_add_one_eq_blockTreeForestRank
    (D : OneVertexSeparation G) :
    G.largestInducedForestSize + 1 = blockTreeForestRank D := by
  rw [GraphConjecture40CutVertexSum.largestInducedForestSize_eq_max_states
    G D.cut]
  unfold blockTreeForestRank includeStateSum excludeStateSum
  rw [← max_add_add_right]
  have hinc :=
    WrittenOnTheWallII.GraphConjecture40SharedCutUnion.OneVertexSeparation.forestOrderIncluding_add_one_eq_sum_withinIncluding D
  have hexc :=
    WrittenOnTheWallII.GraphConjecture40SeparatedUnion.OneVertexSeparation.forestOrderExcluding_eq_sum_within_erase D
  rw [hinc, hexc]

/-- Inclusion-exclusion for the two vertex sides of a one-vertex
separation. -/
theorem card_left_add_card_right_eq_card_add_one
    (D : OneVertexSeparation G) :
    D.left.card + D.right.card = Fintype.card V + 1 := by
  have hcard := card_union_add_card_inter D.left D.right
  rw [D.cover, D.inter, card_univ, card_singleton] at hcard
  omega

/-- Exact one-node block-tree recurrence: feedback deletion plus the local
forest rank equals the sum of the two side orders. -/
theorem feedbackDeletion_add_blockTreeForestRank_eq_side_orders
    (D : OneVertexSeparation G) :
    GraphConjecture40Deficiency.feedbackDeletion G + blockTreeForestRank D =
      D.left.card + D.right.card := by
  have hrank := largestInducedForestSize_add_one_eq_blockTreeForestRank D
  have hforest := GraphConjecture40Deficiency.largestInducedForestSize_le_card G
  have hcard := card_left_add_card_right_eq_card_add_one D
  unfold GraphConjecture40Deficiency.feedbackDeletion
  omega

/-- The feedback coordinate is the side-order complement of the composed
state rank. -/
theorem feedbackDeletion_eq_side_orders_sub_blockTreeForestRank
    (D : OneVertexSeparation G) :
    GraphConjecture40Deficiency.feedbackDeletion G =
      D.left.card + D.right.card - blockTreeForestRank D := by
  have hrec := feedbackDeletion_add_blockTreeForestRank_eq_side_orders D
  omega

/-- Exact reduction of the `2*tau+1` linear-forest target at one block-tree
composition.  The right side is the smallest remaining state inequality. -/
theorem linearForestRank_target_iff_blockTree_state_bound
    (D : OneVertexSeparation G) :
    2 * GraphConjecture40Deficiency.feedbackDeletion G + 1 ≤
        GraphConjecture40Deficiency.linearForestRank G ↔
      2 * (D.left.card + D.right.card - blockTreeForestRank D) + 1 ≤
        GraphConjecture40Deficiency.linearForestRank G := by
  rw [feedbackDeletion_eq_side_orders_sub_blockTreeForestRank D]

/-- For bipartite graphs, the block-tree state inequality is sufficient for
WOWII 40.  Thus all forest-side composition has been discharged; only the
displayed linear-forest rank bound remains. -/
theorem conjecture40_of_bipartite_of_blockTree_state_bound
    (D : OneVertexSeparation G) (hG : G.IsBipartite)
    (hrank :
      2 * (D.left.card + D.right.card - blockTreeForestRank D) + 1 ≤
        GraphConjecture40Deficiency.linearForestRank G) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hB : G.largestInducedBipartiteSubgraphSize = Fintype.card V := by
    apply le_antisymm
      (GraphConjecture40Deficiency.largestInducedBipartiteSubgraphSize_le_card G)
    simpa using
      GraphConjecture40Baseline.card_le_largestInducedBipartiteSubgraphSize
        G (Finset.univ : Finset V) (by
          rw [induce_isBipartite_iff_exists_coloring]
          obtain ⟨c⟩ := hG
          exact ⟨fun x ↦ c x, by
            intro u _ v _ huv
            exact c.valid huv⟩)
  apply GraphConjecture40Deficiency.conjecture40_of_deficiency_bound G
    (GraphConjecture40PathCoverAPI.pathCoverNumber_le_card G)
  have htau :=
    (linearForestRank_target_iff_blockTree_state_bound D).mpr hrank
  unfold GraphConjecture40Deficiency.oddDeletion
  rw [hB]
  simpa using htau

end WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence
