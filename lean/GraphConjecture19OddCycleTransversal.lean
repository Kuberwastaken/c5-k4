import GraphConjecture19MultiArm

/-!
# WOWII 19/13: odd-cycle-transversal charging
-/

namespace WrittenOnTheWallII.GraphConjecture19OddCycleTransversal

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19EndpointMax
open WrittenOnTheWallII.GraphConjecture19MultiArm

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Orders of vertex sets whose deletion leaves an induced bipartite graph. -/
def oddCycleTransversalOrders (G : SimpleGraph V) : Set ℕ :=
  {k | ∃ T : Finset V,
    (G.induce (↑(Finset.univ \ T) : Set V)).IsBipartite ∧ T.card = k}

/-- Minimum odd-cycle-transversal order. -/
noncomputable def oddCycleTransversalNumber (G : SimpleGraph V) : ℕ :=
  sInf (oddCycleTransversalOrders G)

/-- Deleting every vertex shows that the defining order set is nonempty. -/
lemma oddCycleTransversalOrders_nonempty (G : SimpleGraph V) :
    (oddCycleTransversalOrders G).Nonempty := by
  refine ⟨Fintype.card V, Finset.univ, ?_, Finset.card_univ⟩
  rw [induce_isBipartite_iff_exists_coloring]
  exact ⟨fun _ => 0, by simp⟩

/-- A minimum odd-cycle transversal is attained by a finite vertex set. -/
lemma exists_minimum_oddCycleTransversal (G : SimpleGraph V) :
    ∃ T : Finset V,
      (G.induce (↑(Finset.univ \ T) : Set V)).IsBipartite ∧
      T.card = oddCycleTransversalNumber G := by
  exact Nat.sInf_mem (oddCycleTransversalOrders_nonempty G)

/-- Exact certificate lower bound: deleting `T` costs precisely `|T|` vertices
and retains an induced bipartite graph on every other vertex. -/
theorem card_sub_card_le_b_of_transversal (G : SimpleGraph V) (T : Finset V)
    (hT : (G.induce (↑(Finset.univ \ T) : Set V)).IsBipartite) :
    ((Fintype.card V - T.card : ℕ) : ℝ) ≤ b G := by
  have hb := card_le_b_of_induced_bipartite G (Finset.univ \ T) hT
  rw [Finset.card_sdiff, Finset.inter_eq_left.mpr (Finset.subset_univ T),
    Finset.card_univ] at hb
  exact hb

/-- General induced-bipartite bound `b >= n - tau_odd`. -/
theorem card_sub_oddCycleTransversalNumber_le_b (G : SimpleGraph V) :
    ((Fintype.card V - oddCycleTransversalNumber G : ℕ) : ℝ) ≤ b G := by
  obtain ⟨T, hT, hcard⟩ := exists_minimum_oddCycleTransversal G
  rw [← hcard]
  exact card_sub_card_le_b_of_transversal G T hT

/-- The exact transversal charge sufficient for WOWII 13: the deletion cost,
diameter, and maximum local independence fit into `n+1`. -/
theorem wowii13_of_transversal_charge
    (G : SimpleGraph V) [Nonempty V] (T : Finset V)
    (hT : (G.induce (↑(Finset.univ \ T) : Set V)).IsBipartite)
    (hcharge : T.card + G.diam + localMax G ≤ Fintype.card V + 1) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  have hb := card_sub_card_le_b_of_transversal G T hT
  have hsub : ((Fintype.card V - T.card : ℕ) : ℝ) =
      (Fintype.card V : ℝ) - T.card := by
    rw [Nat.cast_sub (Finset.card_le_univ T)]
  rw [hsub] at hb
  have hcR : (T.card : ℝ) + G.diam + localMax G ≤
      (Fintype.card V : ℝ) + 1 := by exact_mod_cast hcharge
  linarith

/-- Minimum-transversal-number form of the same charge theorem. -/
theorem wowii13_of_minimum_transversal_charge
    (G : SimpleGraph V) [Nonempty V]
    (hcharge : oddCycleTransversalNumber G + G.diam + localMax G ≤
      Fintype.card V + 1) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  obtain ⟨T, hT, hcard⟩ := exists_minimum_oddCycleTransversal G
  apply wowii13_of_transversal_charge G T hT
  simpa [hcard] using hcharge

end WrittenOnTheWallII.GraphConjecture19OddCycleTransversal
