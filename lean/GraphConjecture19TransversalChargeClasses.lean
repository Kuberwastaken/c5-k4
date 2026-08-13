import GraphConjecture19OddCycleTransversal
import GraphConjecture19StarBound

/-!
# WOWII 19/13: graph classes satisfying the transversal charge
-/

namespace WrittenOnTheWallII.GraphConjecture19TransversalChargeClasses

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19EndpointMax
open WrittenOnTheWallII.GraphConjecture19OddCycleTransversal
open WrittenOnTheWallII.GraphConjecture19StarBound

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Bipartite graphs have odd-cycle-transversal number zero. -/
theorem oddCycleTransversalNumber_eq_zero_of_bipartite
    (G : SimpleGraph V) (hG : G.IsBipartite) :
    oddCycleTransversalNumber G = 0 := by
  apply Nat.eq_zero_of_le_zero
  apply Nat.sInf_le
  refine ⟨∅, ?_, rfl⟩
  have heq : (Finset.univ \ ∅ : Finset V) = Finset.univ := by ext x; simp
  rw [heq]
  rcases hG with ⟨c⟩
  exact ⟨Coloring.mk (fun x => c x.val) fun {_x _y} hxy => c.valid hxy⟩

/-- A one-vertex odd-cycle transversal bounds `tau_odd` by one. -/
theorem oddCycleTransversalNumber_le_one_of_delete_vertex
    (G : SimpleGraph V) (z : V)
    (hz : (G.induce (↑(Finset.univ.erase z) : Set V)).IsBipartite) :
    oddCycleTransversalNumber G ≤ 1 := by
  apply Nat.sInf_le
  refine ⟨{z}, ?_, by simp⟩
  have heq : (Finset.univ \ {z} : Finset V) = Finset.univ.erase z := by
    ext x
    simp
  rw [heq]
  exact hz

/-- A maximum induced star gives an explicit transversal whose deletion cost
plus `localMax+1` is exactly the graph order. -/
theorem exists_star_complement_transversal
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj] :
    ∃ T : Finset V,
      (G.induce (↑(Finset.univ \ T) : Set V)).IsBipartite ∧
      T.card + localMax G + 1 = Fintype.card V := by
  obtain ⟨v, hv⟩ := exists_indepNeighborsCard_eq_localMax G
  obtain ⟨A, hA, hAN, hAcard⟩ := exists_local_indep_witness G v
  let S : Finset V := insert v A
  let T : Finset V := Finset.univ \ S
  have hvA : v ∉ A := by
    intro hvA
    have : G.Adj v v := by simpa [mem_neighborFinset] using hAN hvA
    exact G.loopless v this
  have hScard : S.card = localMax G + 1 := by
    dsimp [S]
    rw [card_insert_of_notMem hvA, hAcard, hv]
  have hSbip : (G.induce (↑S : Set V)).IsBipartite := by
    have hI : G.IsIndepSet ((∅ : Finset V) : Set V) := by simp
    have hIout : ∀ x ∈ (∅ : Finset V), x ≠ v ∧ ¬G.Adj v x := by simp
    have hb := induce_insert_union_isBipartite_of_indep
      G v A (∅ : Finset V) hA
        (by intro x hx; simpa [mem_neighborFinset] using hAN hx) hI hIout
    have heq : insert v (A ∪ (∅ : Finset V)) = S := by
      ext x
      simp [S]
    rw [heq] at hb
    exact hb
  refine ⟨T, ?_, ?_⟩
  · have hcomp : Finset.univ \ T = S := by
      dsimp [T]
      ext x
      simp [S]
    rw [hcomp]
    exact hSbip
  · have hTcard : T.card = Fintype.card V - S.card := by
      dsimp [T]
      rw [Finset.card_sdiff, Finset.inter_eq_left.mpr (Finset.subset_univ S),
        Finset.card_univ]
    rw [hTcard, hScard]
    have hle : localMax G + 1 ≤ Fintype.card V := by
      rw [← hScard]
      exact S.card_le_univ
    omega

/-- Universal maximum-star charge: an odd-cycle transversal can always be
chosen so that its size plus `localMax+1` fits in the vertex set. -/
theorem transversalNumber_add_localMax_add_one_le_card
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj] :
    oddCycleTransversalNumber G + localMax G + 1 ≤ Fintype.card V := by
  obtain ⟨T, hT, hcard⟩ := exists_star_complement_transversal G
  have htau : oddCycleTransversalNumber G ≤ T.card := by
    apply Nat.sInf_le
    exact ⟨T, hT, rfl⟩
  omega

/-- Every graph of diameter at most two satisfies the full transversal charge,
via deletion of the complement of a maximum induced star. -/
theorem transversal_charge_of_diam_le_two
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hdiam : G.diam ≤ 2) :
    oddCycleTransversalNumber G + G.diam + localMax G ≤
      Fintype.card V + 1 := by
  obtain ⟨T, hT, hcard⟩ := exists_star_complement_transversal G
  have htau : oddCycleTransversalNumber G ≤ T.card := by
    apply Nat.sInf_le
    exact ⟨T, hT, rfl⟩
  omega

/-- Hence WOWII 13 holds on every graph of diameter at most two through the
general odd-cycle-transversal charge theorem. -/
theorem wowii13_of_diam_le_two_via_transversal
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hdiam : G.diam ≤ 2) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  exact wowii13_of_minimum_transversal_charge G
    (transversal_charge_of_diam_le_two G hdiam)

/-- Bipartite (hence tree) class reduction: only the classical order count
`diam+localMax <= n+1` remains. -/
theorem transversal_charge_of_bipartite_of_order_count
    (G : SimpleGraph V) [Nonempty V] (hG : G.IsBipartite)
    (hcount : G.diam + localMax G ≤ Fintype.card V + 1) :
    oddCycleTransversalNumber G + G.diam + localMax G ≤
      Fintype.card V + 1 := by
  rw [oddCycleTransversalNumber_eq_zero_of_bipartite G hG]
  omega

/-- One-deletion (including many unicyclic/cactus) class reduction. -/
theorem transversal_charge_of_delete_vertex_of_order_count
    (G : SimpleGraph V) [Nonempty V] (z : V)
    (hz : (G.induce (↑(Finset.univ.erase z) : Set V)).IsBipartite)
    (hcount : G.diam + localMax G ≤ Fintype.card V) :
    oddCycleTransversalNumber G + G.diam + localMax G ≤
      Fintype.card V + 1 := by
  have htau := oddCycleTransversalNumber_le_one_of_delete_vertex G z hz
  omega

end WrittenOnTheWallII.GraphConjecture19TransversalChargeClasses
