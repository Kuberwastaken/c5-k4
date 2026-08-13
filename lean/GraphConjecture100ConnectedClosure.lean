import GraphConjecture100WitnessClassification

/-!
# WOWII 100: consolidated connected-graph closure

This file follows the exact upstream Lean expression `degreeL2Norm Gᶜ`, not
the complement-diameter reading in the historical prose.
-/

namespace WrittenOnTheWallII.GraphConjecture100ConnectedClosure

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction
open WrittenOnTheWallII.GraphConjecture100MiddleRange
open WrittenOnTheWallII.GraphConjecture100AlphaThirteen
open WrittenOnTheWallII.GraphConjecture100IncidenceEnergy
open WrittenOnTheWallII.GraphConjecture100ThreeWitness
open WrittenOnTheWallII.GraphConjecture100WitnessClassification

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

set_option maxHeartbeats 1000000 in
lemma two_attachment_margin_two_to_three_of_sum_le
    (a t u : ℕ) (ha : 2 ≤ a ∧ a ≤ 11)
    (ht : t + 1 ≤ a) (hu : u + 1 ≤ a) (hsum : t + u ≤ a) :
    (2 * (a : ℝ) - 4 + 2 * min t u) ^ 2 <
      ((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u) + t ^ 2 + u ^ 2 : ℕ) : ℝ) := by
  have ha0 := ha.1
  have ha1 := ha.2
  have ht3 : t ≤ 10 := by omega
  have hu3 : u ≤ 10 := by omega
  interval_cases a <;> interval_cases t <;> interval_cases u <;> norm_num at *

set_option maxHeartbeats 1000000 in
lemma three_attachment_margin_two_to_three
    (a t u v : ℕ) (ha : 2 ≤ a ∧ a ≤ 11)
    (ht : t + 1 ≤ a) (hu : u + 1 ≤ a) (hv : v + 1 ≤ a) :
    (2 * (a : ℝ) - 4 + 2 * min t (min u v)) ^ 2 <
      ((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u + v) +
        t ^ 2 + u ^ 2 + v ^ 2 : ℕ) : ℝ) := by
  have ha0 := ha.1
  have ha1 := ha.2
  let m := min t (min u v)
  have hmt : m ≤ t := min_le_left _ _
  have hmu : m ≤ u := (min_le_right t (min u v)).trans (min_le_left u v)
  have hmv : m ≤ v := (min_le_right t (min u v)).trans (min_le_right u v)
  have hmtR : (m : ℝ) ≤ t := by exact_mod_cast hmt
  have hmuR : (m : ℝ) ≤ u := by exact_mod_cast hmu
  have hmvR : (m : ℝ) ≤ v := by exact_mod_cast hmv
  have htSq : (m : ℝ) ^ 2 ≤ (t : ℝ) ^ 2 :=
    (sq_le_sq₀ (Nat.cast_nonneg _) (Nat.cast_nonneg _)).2 hmtR
  have huSq : (m : ℝ) ^ 2 ≤ (u : ℝ) ^ 2 :=
    (sq_le_sq₀ (Nat.cast_nonneg _) (Nat.cast_nonneg _)).2 hmuR
  have hvSq : (m : ℝ) ^ 2 ≤ (v : ℝ) ^ 2 :=
    (sq_le_sq₀ (Nat.cast_nonneg _) (Nat.cast_nonneg _)).2 hmvR
  have hmBound : m ≤ 10 := by omega
  have hreduced :
      (2 * (a : ℝ) - 4 + 2 * m) ^ 2 <
        ((a * (a - 1) ^ 2 + (2 * a - 1) * (3 * m) + 3 * m ^ 2 : ℕ) : ℝ) := by
    interval_cases a <;> interval_cases m <;> norm_num at *
    all_goals omega
  have hsum : (3 : ℝ) * m ≤ t + u + v := by linarith
  have hmono :
      ((a * (a - 1) ^ 2 + (2 * a - 1) * (3 * m) + 3 * m ^ 2 : ℕ) : ℝ) ≤
        ((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u + v) +
          t ^ 2 + u ^ 2 + v ^ 2 : ℕ) : ℝ) := by
    interval_cases a <;> norm_num at htSq huSq hvSq hsum ⊢ <;> nlinarith
  exact hreduced.trans_le hmono

lemma conjecture100_of_zero_attachment_two_to_three
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (S : Finset V) (hS : G.IsNIndepSet G.indepNum S)
    (ha : 2 ≤ G.indepNum ∧ G.indepNum ≤ 11)
    (y : V) (hy : y ∉ S)
    (hzero : (S.filter (fun s ↦ Gᶜ.Adj y s)).card = 0) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  let T := S.filter (fun s ↦ Gᶜ.Adj y s)
  have hcard := hS.card_eq
  have htrade := attachment_tradeoff G S hS.isIndepSet (by omega) y hy
  dsimp only at htrade
  have hmargin : (2 * (S.card : ℝ) - 4 + 2 * T.card) ^ 2 <
      (((S.card - 1) ^ 2 * (S.card - T.card) + S.card ^ 2 * T.card +
        T.card ^ 2 : ℕ) : ℝ) := by
    have hz : T.card = 0 := hzero
    have ha' : 2 ≤ S.card ∧ S.card ≤ 11 := hcard ▸ ha
    have hlo := ha'.1
    have hhi := ha'.2
    rw [hz]
    interval_cases hSc : S.card <;> norm_num at *
  have hleft : (0 : ℝ) ≤ 2 * (S.card : ℝ) - 4 + 2 * T.card := by
    have h2 : (2 : ℝ) ≤ S.card := by exact_mod_cast (hcard ▸ ha.1)
    have ht0 : (0 : ℝ) ≤ T.card := Nat.cast_nonneg _
    linarith
  have hroot : 2 * (S.card : ℝ) - 4 + 2 * T.card < degreeL2Norm Gᶜ := by
    have hsqrt := (Real.lt_sqrt hleft).2 hmargin
    unfold degreeL2Norm
    exact hsqrt.trans_le (Real.sqrt_le_sqrt htrade.2)
  apply conjecture100_of_residual G
  dsimp
  have hlocalN : S.card - T.card ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp) :=
    htrade.1.trans ((Finset.univ.image (indepNeighborsCard G)).le_max'
      _ (mem_image_of_mem _ (mem_univ y)))
  have hlocalR : ((S.card - T.card : ℕ) : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
    exact_mod_cast hlocalN
  have ht : T.card ≤ S.card := card_le_card (filter_subset _ _)
  rw [Nat.cast_sub ht] at hlocalR
  rw [← hcard]
  linarith

lemma conjecture100_of_two_outside_energy_two_to_three
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (a t u : ℕ) (haG : G.indepNum = a) (ha : 2 ≤ a ∧ a ≤ 11)
    (ht : t + 1 ≤ a) (hu : u + 1 ≤ a) (hsum : t + u ≤ a)
    (hlocalT : a - t ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp))
    (hlocalU : a - u ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp))
    (henergy : TwoOutsideEnergyCertificate G a t u) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  have hmargin := two_attachment_margin_two_to_three_of_sum_le a t u ha ht hu hsum
  have hleft : (0 : ℝ) ≤ 2 * (a : ℝ) - 4 + 2 * min t u := by
    have haR : (2 : ℝ) ≤ a := by exact_mod_cast ha.1
    have hmR : (0 : ℝ) ≤ min t u := Nat.cast_nonneg _
    linarith
  have hroot : 2 * (a : ℝ) - 4 + 2 * min t u < degreeL2Norm Gᶜ := by
    have hsqrt := (Real.lt_sqrt hleft).2 hmargin
    unfold TwoOutsideEnergyCertificate at henergy
    unfold degreeL2Norm
    exact hsqrt.trans_le (Real.sqrt_le_sqrt henergy)
  apply conjecture100_of_residual G
  dsimp
  have hlocalN : a - min t u ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp) := by
    by_cases htu : t ≤ u
    · rw [min_eq_left htu]; exact hlocalT
    · rw [min_eq_right (Nat.le_of_not_ge htu)]; exact hlocalU
  have hlocalR : ((a - min t u : ℕ) : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
    exact_mod_cast hlocalN
  have hm : min t u ≤ a := by omega
  rw [Nat.cast_sub hm] at hlocalR
  rw [haG]
  linarith

lemma conjecture100_of_three_outside_energy_two_to_three
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (a t u v : ℕ) (haG : G.indepNum = a) (ha : 2 ≤ a ∧ a ≤ 11)
    (ht : t + 1 ≤ a) (hu : u + 1 ≤ a) (hv : v + 1 ≤ a)
    (hlocalT : a - t ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp))
    (hlocalU : a - u ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp))
    (hlocalV : a - v ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp))
    (henergy : ThreeOutsideEnergyCertificate G a t u v) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  let m := min t (min u v)
  have hmargin := three_attachment_margin_two_to_three a t u v ha ht hu hv
  have hleft : (0 : ℝ) ≤ 2 * (a : ℝ) - 4 + 2 * m := by
    have haR : (2 : ℝ) ≤ a := by exact_mod_cast ha.1
    have hmR : (0 : ℝ) ≤ m := Nat.cast_nonneg _
    linarith
  have hroot : 2 * (a : ℝ) - 4 + 2 * m < degreeL2Norm Gᶜ := by
    have hsqrt := (Real.lt_sqrt hleft).2 hmargin
    unfold ThreeOutsideEnergyCertificate at henergy
    unfold degreeL2Norm
    exact hsqrt.trans_le (Real.sqrt_le_sqrt henergy)
  apply conjecture100_of_residual G
  dsimp
  have hlocalN : a - m ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp) := by
    by_cases htu : t ≤ min u v
    · rw [show m = t by simp [m, htu]]; exact hlocalT
    · have hut : min u v ≤ t := Nat.le_of_not_ge htu
      by_cases huv : u ≤ v
      · have hut' : u ≤ t := by simpa [min_eq_left huv] using hut
        rw [show m = u by simp [m, min_eq_left huv, min_eq_right hut']]
        exact hlocalU
      · have hvu : v ≤ u := Nat.le_of_not_ge huv
        have hut' : v ≤ t := by simpa [min_eq_right hvu] using hut
        rw [show m = v by simp [m, min_eq_right hvu, min_eq_right hut']]
        exact hlocalV
  have hlocalR : ((a - m : ℕ) : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
    exact_mod_cast hlocalN
  have hm : m ≤ a := by omega
  rw [Nat.cast_sub hm] at hlocalR
  rw [haG]
  linarith

/-- The witness classification closes the entire middle range `2 ≤ α ≤ 11`
without complement connectedness. -/
theorem conjecture100_of_connected_of_indepNum_two_to_eleven
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (ha : 2 ≤ G.indepNum ∧ G.indepNum ≤ 11) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  obtain ⟨S, hS⟩ := G.exists_isNIndepSet_indepNum
  have hcard := hS.card_eq
  have hSne : S.Nonempty := card_pos.mp (by omega : 0 < S.card)
  obtain ⟨s, hs⟩ := hSne
  obtain ⟨y₀, hy₀, _⟩ := cross_witness_covers G hG S hS.isIndepSet s hs
  rcases cross_witness_trichotomy G S ⟨y₀, hy₀⟩ with hone | htwo | hthree
  · obtain ⟨y, hy, hunique⟩ := hone
    exact conjecture100_of_zero_attachment_two_to_three G S hS ha y hy.1
      (zero_attachment_of_unique_cross_witness G hG S hS.isIndepSet y hunique)
  · obtain ⟨y, z, hy, hz, hyz, hexhaust⟩ := htwo
    let T := S.filter (fun r ↦ Gᶜ.Adj y r)
    let U := S.filter (fun r ↦ Gᶜ.Adj z r)
    have ht : T.card + 1 ≤ S.card := by
      obtain ⟨r, hrS, hyr⟩ := hy.2
      have hrnot : r ∉ T := by
        simp only [T, mem_filter, hrS, true_and]
        intro hc
        rw [compl_adj] at hc
        exact hc.2 hyr
      have hp : T ⊂ S := Finset.ssubset_iff_subset_ne.mpr
        ⟨filter_subset _ _, fun heq ↦ hrnot (heq.symm ▸ hrS)⟩
      have hlt := card_lt_card hp
      omega
    have hu : U.card + 1 ≤ S.card := by
      obtain ⟨r, hrS, hzr⟩ := hz.2
      have hrnot : r ∉ U := by
        simp only [U, mem_filter, hrS, true_and]
        intro hc
        rw [compl_adj] at hc
        exact hc.2 hzr
      have hp : U ⊂ S := Finset.ssubset_iff_subset_ne.mpr
        ⟨filter_subset _ _, fun heq ↦ hrnot (heq.symm ▸ hrS)⟩
      have hlt := card_lt_card hp
      omega
    have hsum : T.card + U.card ≤ S.card :=
      two_attachment_sum_le_of_exhaustive G hG S hS.isIndepSet y z hexhaust
    have hTy := attachment_tradeoff G S hS.isIndepSet (by omega) y hy.1
    have hUz := attachment_tradeoff G S hS.isIndepSet (by omega) z hz.1
    dsimp only at hTy hUz
    have hlocalT : S.card - T.card ≤
        (Finset.univ.image (indepNeighborsCard G)).max' (by simp) :=
      hTy.1.trans ((Finset.univ.image (indepNeighborsCard G)).le_max'
        _ (mem_image_of_mem _ (mem_univ y)))
    have hlocalU : S.card - U.card ≤
        (Finset.univ.image (indepNeighborsCard G)).max' (by simp) :=
      hUz.1.trans ((Finset.univ.image (indepNeighborsCard G)).le_max'
        _ (mem_image_of_mem _ (mem_univ z)))
    have henergy := two_outside_energy_certificate
      G S hS.isIndepSet (by omega) y z hy.1 hz.1 hyz
    dsimp only at henergy
    exact conjecture100_of_two_outside_energy_two_to_three G S.card T.card U.card
      hcard.symm (hcard ▸ ha) ht hu hsum hlocalT hlocalU henergy
  · obtain ⟨y, z, w, hy, hz, hw, hyz, hyw, hzw⟩ := hthree
    let T := S.filter (fun r ↦ Gᶜ.Adj y r)
    let U := S.filter (fun r ↦ Gᶜ.Adj z r)
    let W := S.filter (fun r ↦ Gᶜ.Adj w r)
    have ht : T.card + 1 ≤ S.card := by
      obtain ⟨r, hrS, hyr⟩ := hy.2
      have hrnot : r ∉ T := by
        simp only [T, mem_filter, hrS, true_and]
        intro hc
        rw [compl_adj] at hc
        exact hc.2 hyr
      have hp : T ⊂ S := Finset.ssubset_iff_subset_ne.mpr
        ⟨filter_subset _ _, fun heq ↦ hrnot (heq.symm ▸ hrS)⟩
      have hlt := card_lt_card hp
      omega
    have hu : U.card + 1 ≤ S.card := by
      obtain ⟨r, hrS, hzr⟩ := hz.2
      have hrnot : r ∉ U := by
        simp only [U, mem_filter, hrS, true_and]
        intro hc
        rw [compl_adj] at hc
        exact hc.2 hzr
      have hp : U ⊂ S := Finset.ssubset_iff_subset_ne.mpr
        ⟨filter_subset _ _, fun heq ↦ hrnot (heq.symm ▸ hrS)⟩
      have hlt := card_lt_card hp
      omega
    have hv : W.card + 1 ≤ S.card := by
      obtain ⟨r, hrS, hwr⟩ := hw.2
      have hrnot : r ∉ W := by
        simp only [W, mem_filter, hrS, true_and]
        intro hc
        rw [compl_adj] at hc
        exact hc.2 hwr
      have hp : W ⊂ S := Finset.ssubset_iff_subset_ne.mpr
        ⟨filter_subset _ _, fun heq ↦ hrnot (heq.symm ▸ hrS)⟩
      have hlt := card_lt_card hp
      omega
    have hTy := attachment_tradeoff G S hS.isIndepSet (by omega) y hy.1
    have hUz := attachment_tradeoff G S hS.isIndepSet (by omega) z hz.1
    have hWw := attachment_tradeoff G S hS.isIndepSet (by omega) w hw.1
    dsimp only at hTy hUz hWw
    have hlocalT : S.card - T.card ≤
        (Finset.univ.image (indepNeighborsCard G)).max' (by simp) :=
      hTy.1.trans ((Finset.univ.image (indepNeighborsCard G)).le_max'
        _ (mem_image_of_mem _ (mem_univ y)))
    have hlocalU : S.card - U.card ≤
        (Finset.univ.image (indepNeighborsCard G)).max' (by simp) :=
      hUz.1.trans ((Finset.univ.image (indepNeighborsCard G)).le_max'
        _ (mem_image_of_mem _ (mem_univ z)))
    have hlocalW : S.card - W.card ≤
        (Finset.univ.image (indepNeighborsCard G)).max' (by simp) :=
      hWw.1.trans ((Finset.univ.image (indepNeighborsCard G)).le_max'
        _ (mem_image_of_mem _ (mem_univ w)))
    have henergy := three_outside_energy_certificate G S hS.isIndepSet
      (by omega) y z w hy.1 hz.1 hw.1 hyz hyw hzw
    dsimp only at henergy
    exact conjecture100_of_three_outside_energy_two_to_three
      G S.card T.card U.card W.card hcard.symm (hcard ▸ ha)
      ht hu hv hlocalT hlocalU hlocalW henergy

omit [DecidableEq V] in
/-- Every connected nontrivial graph has a vertex whose neighborhood contains
an independent singleton. -/
lemma one_le_max_indepNeighborsCard_of_connected
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) :
    1 ≤ (Finset.univ.image (indepNeighborsCard G)).max' (by simp) := by
  let y : V := Classical.choice (inferInstance : Nonempty V)
  obtain ⟨z, hyz⟩ := hG.preconnected.exists_adj_of_nontrivial y
  have hsingle : G.IsIndepSet (({z} : Finset V) : Set V) := by
    simp
  have hlocal : 1 ≤ indepNeighborsCard G y := by
    have hcard := card_le_indepNeighborsCard_of_indep_neighbor_subset
      G y {z} hsingle (by simpa using hyz)
    simpa using hcard
  exact hlocal.trans ((Finset.univ.image (indepNeighborsCard G)).le_max'
    _ (mem_image_of_mem _ (mem_univ y)))

/-- The independence-one row follows solely from the positive local term. -/
lemma conjecture100_of_connected_of_indepNum_one
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (ha : G.indepNum = 1) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  apply conjecture100_of_residual G
  dsimp
  have hL := one_le_max_indepNeighborsCard_of_connected G hG
  have hLR : (1 : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
    exact_mod_cast hL
  have hq : (0 : ℝ) ≤ degreeL2Norm Gᶜ := Real.sqrt_nonneg _
  rw [ha]
  norm_num
  linarith

/-- Consolidated exact-formalization closure for every finite connected
nontrivial graph. -/
theorem conjecture100_of_connected
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  let y : V := Classical.choice (inferInstance : Nonempty V)
  have hyind : G.IsIndepSet (({y} : Finset V) : Set V) := by simp
  have ha1 : 1 ≤ G.indepNum := by
    simpa using hyind.card_le_indepNum
  by_cases h12 : 12 ≤ G.indepNum
  · exact conjecture100_of_connected_of_twelve_le_indepNum G hG h12
  · have hle : G.indepNum ≤ 11 := by omega
    by_cases hone : G.indepNum = 1
    · exact conjecture100_of_connected_of_indepNum_one G hG hone
    · exact conjecture100_of_connected_of_indepNum_two_to_eleven G hG
        ⟨by omega, hle⟩

end WrittenOnTheWallII.GraphConjecture100ConnectedClosure
