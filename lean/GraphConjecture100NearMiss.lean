import GraphConjecture100FiniteRange

/-!
# WOWII 100: the independence-three near miss

This continuation follows the exact upstream Lean expression containing
`degreeL2Norm Gᶜ`; it does not address the complement-diameter reading in the
upstream prose.

For independence number three, the crude complement-energy lower bound is
only `12`, just short of the residual target `16` after using `maxL ≥ 2`.
Connectedness forces the complement triangle supplied by a maximum independent
set to have a crossing edge.  That single attachment raises the squared-degree
energy to at least `18`, closing this near miss.
-/

namespace WrittenOnTheWallII.GraphConjecture100NearMiss

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction
open WrittenOnTheWallII.GraphConjecture100FiniteRange

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- An independent triple with one complement edge leaving it contributes at
least eighteen to the complement squared-degree sum. -/
theorem eighteen_le_compl_energy_of_indep_triple_crossing
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (hS : G.IsIndepSet (S : Set V)) (hcard : S.card = 3)
    (a y : V) (ha : a ∈ S) (hy : y ∉ S) (hay : Gᶜ.Adj a y) :
    (18 : ℝ) ≤ ∑ v, (Gᶜ.degree v : ℝ) ^ 2 := by
  have hbase : ∀ v ∈ S, 2 ≤ Gᶜ.degree v := by
    intro v hv
    have h := card_sub_one_le_compl_degree_of_indep G S hS v hv
    omega
  have hydeg : 1 ≤ Gᶜ.degree y := by
    have : 0 < Gᶜ.degree y := (Gᶜ.degree_pos_iff_exists_adj y).2 ⟨a, hay.symm⟩
    omega
  have hasub : insert y (S.erase a) ⊆ Gᶜ.neighborFinset a := by
    intro v hv
    simp only [mem_insert, mem_erase] at hv
    rcases hv with rfl | ⟨hva, hvS⟩
    · simpa only [mem_neighborFinset] using hay
    · rw [mem_neighborFinset, compl_adj]
      exact ⟨hva.symm, fun hav ↦ hS ha hvS hva.symm hav⟩
  have hacard : (insert y (S.erase a)).card = 3 := by
    rw [card_insert_of_notMem]
    · rw [card_erase_of_mem ha, hcard]
    · exact fun hyerase ↦ hy (mem_of_mem_erase hyerase)
  have hadeg : 3 ≤ Gᶜ.degree a := by
    rw [← hacard]
    exact card_le_card hasub
  have herasecard : (S.erase a).card = 2 := by
    rw [card_erase_of_mem ha, hcard]
  have herase : (8 : ℝ) ≤ ∑ v ∈ S.erase a, (Gᶜ.degree v : ℝ) ^ 2 := by
    calc
      (8 : ℝ) = ∑ _v ∈ S.erase a, (4 : ℝ) := by
        simp [herasecard]
        norm_num
      _ ≤ ∑ v ∈ S.erase a, (Gᶜ.degree v : ℝ) ^ 2 := by
        apply sum_le_sum
        intro v hv
        have hvS : v ∈ S := mem_of_mem_erase hv
        have hvdeg := hbase v hvS
        exact_mod_cast (sq_le_sq₀ (by omega : 0 ≤ (2 : ℕ))
          (Nat.zero_le (Gᶜ.degree v))).2 hvdeg
  have hasq : (9 : ℝ) ≤ (Gᶜ.degree a : ℝ) ^ 2 := by
    have hadegR : (3 : ℝ) ≤ Gᶜ.degree a := by exact_mod_cast hadeg
    nlinarith [sq_nonneg ((Gᶜ.degree a : ℝ) - 3)]
  have hysq : (1 : ℝ) ≤ (Gᶜ.degree y : ℝ) ^ 2 := by
    have hydegR : (1 : ℝ) ≤ Gᶜ.degree y := by exact_mod_cast hydeg
    nlinarith [sq_nonneg ((Gᶜ.degree y : ℝ) - 1)]
  have hSsum : (17 : ℝ) ≤ ∑ v ∈ S, (Gᶜ.degree v : ℝ) ^ 2 := by
    rw [← sum_erase_add _ _ ha]
    linarith
  have hins : (18 : ℝ) ≤ ∑ v ∈ insert y S, (Gᶜ.degree v : ℝ) ^ 2 := by
    rw [sum_insert hy]
    linarith
  exact hins.trans
    (sum_le_sum_of_subset_of_nonneg (subset_univ (insert y S))
      (fun _ _ _ ↦ sq_nonneg _))

/-- Under the two connectedness hypotheses, a maximum independent triple has
a complement edge crossing to the rest of the graph. -/
theorem eighteen_le_compl_energy_of_connected_indepNum_three
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (hGc : Gᶜ.Connected) (hthree : G.indepNum = 3) :
    (18 : ℝ) ≤ ∑ v, (Gᶜ.degree v : ℝ) ^ 2 := by
  obtain ⟨S, hS⟩ := G.exists_isNIndepSet_indepNum
  have hcard : S.card = 3 := hS.card_eq.trans hthree
  have hSne : S.Nonempty := card_pos.mp (by omega : 0 < S.card)
  let s : V := hSne.choose
  have hs : s ∈ S := hSne.choose_spec
  obtain ⟨z, hszG⟩ := hG.preconnected.exists_adj_of_nontrivial s
  have hzout : z ∉ S := by
    intro hz
    exact hS.isIndepSet hs hz hszG.ne hszG
  obtain ⟨p⟩ := hGc.preconnected s z
  obtain ⟨d, _hdp, hdfst, hdsnd⟩ :=
    p.exists_boundary_dart (S : Set V) hs hzout
  exact eighteen_le_compl_energy_of_indep_triple_crossing
    G S hS.isIndepSet hcard d.fst d.snd hdfst hdsnd d.adj

/-- The sharpened complement-energy norm at independence number three. -/
theorem four_lt_degreeL2Norm_compl_of_connected_indepNum_three
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (hGc : Gᶜ.Connected) (hthree : G.indepNum = 3) :
    (4 : ℝ) < degreeL2Norm Gᶜ := by
  have henergy :=
    eighteen_le_compl_energy_of_connected_indepNum_three G hG hGc hthree
  unfold degreeL2Norm
  apply (Real.lt_sqrt (by norm_num : (0 : ℝ) ≤ 4)).2
  nlinarith

/-- The exact formalized WOWII 100 conclusion at independence number three.
Together with v0.9, this leaves only `4 ≤ indepNum G ≤ 13` in the connected
finite residue. -/
theorem conjecture100_of_connected_of_indepNum_eq_three
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (hGc : Gᶜ.Connected) (hthree : G.indepNum = 3) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  apply conjecture100_of_residual G
  dsimp
  have hlocalN := two_le_max_indepNeighborsCard G hG hGc
  dsimp at hlocalN
  have hlocalR : (2 : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
    exact_mod_cast hlocalN
  have hnorm :=
    four_lt_degreeL2Norm_compl_of_connected_indepNum_three G hG hGc hthree
  rw [hthree]
  norm_num
  linarith

end WrittenOnTheWallII.GraphConjecture100NearMiss
