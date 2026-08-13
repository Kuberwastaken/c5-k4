import GraphConjecture40PositiveFeedback

/-!
# WOWII 40: witness-to-deficiency transfer

The path-support cover from v0.11 pays one unit of linear-forest rank for
each edge of its path.  This file packages the construction at arbitrary
feedback-deletion coordinate `tau`.
-/

namespace WrittenOnTheWallII.GraphConjecture40LinearForest

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- A path support of order `q` gives `pathCoverNumber + q - 1 <= n`.
This is the generic witness-to-linear-forest-rank bridge behind v0.11. -/
theorem pathCoverNumber_add_pred_card_le_card_of_path
    (G : SimpleGraph V) {a z : V} (p : G.Walk a z)
    (hp : p.IsPath) (hcard : 2 ≤ p.support.toFinset.card) :
    pathCoverNumber G + (p.support.toFinset.card - 1) ≤
      Fintype.card V := by
  have hcover :=
    GraphConjecture40PositiveFeedback.pathSupportCover_isPathCover
      G p hp hcard
  have hle :=
    GraphConjecture40PathCoverAPI.pathCoverNumber_le_card_of_isPathCover
      G _ hcover
  have hc :=
    GraphConjecture40PositiveFeedback.pathSupportCover_card
      (V := V) p.support.toFinset hcard
  omega

/-- In a bipartite graph, a single path of order at least `2*tau+2` pays the
entire deficiency bound `ell >= 2*tau+1`. -/
theorem conjecture40_of_bipartite_of_long_path_for_feedbackDeletion
    (G : SimpleGraph V)
    (hG : G.IsBipartite)
    {k : ℕ}
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = k)
    {a z : V} (p : G.Walk a z) (hp : p.IsPath)
    (hcard : 2 * k + 2 ≤ p.support.toFinset.card) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have htwo : 2 ≤ p.support.toFinset.card := by omega
  have hprank :=
    pathCoverNumber_add_pred_card_le_card_of_path G p hp htwo
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
  unfold GraphConjecture40Deficiency.feedbackDeletion at htau
  unfold GraphConjecture40Deficiency.feedbackDeletion
    GraphConjecture40Deficiency.oddDeletion
    GraphConjecture40Deficiency.linearForestRank
  rw [hB]
  omega

/-- Concrete `tau=2` endpoint: a bipartite graph with feedback-deletion two
and a path on at least six vertices satisfies WOWII 40. -/
theorem conjecture40_of_bipartite_of_feedbackDeletion_eq_two_of_six_vertex_path
    (G : SimpleGraph V)
    (hG : G.IsBipartite)
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = 2)
    {a z : V} (p : G.Walk a z) (hp : p.IsPath)
    (hcard : 6 ≤ p.support.toFinset.card) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  exact conjecture40_of_bipartite_of_long_path_for_feedbackDeletion
    G hG htau p hp (by omega)

end WrittenOnTheWallII.GraphConjecture40LinearForest
