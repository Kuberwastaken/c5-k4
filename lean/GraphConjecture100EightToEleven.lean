import GraphConjecture100IncidenceEnergy

/-!
# WOWII 100: unconditional independence range eight through eleven

This file follows the exact upstream Lean expression `degreeL2Norm Gᶜ`, not
the complement-diameter reading in the upstream prose.
-/

namespace WrittenOnTheWallII.GraphConjecture100EightToEleven

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction
open WrittenOnTheWallII.GraphConjecture100MiddleRange

open WrittenOnTheWallII.GraphConjecture100IncidenceEnergy

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

set_option maxHeartbeats 1000000 in
lemma two_attachment_margin
    (a t u : ℕ) (ha : 8 ≤ a ∧ a ≤ 11) (ht : t + 1 ≤ a) (hu : u + 1 ≤ a) :
    (2 * (a : ℝ) - 4 + 2 * min t u) ^ 2 <
      ((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u) + t ^ 2 + u ^ 2 : ℕ) : ℝ) := by
  have ha0 := ha.1
  have ha1 := ha.2
  have ht1 : t ≤ 10 := by omega
  have hu1 : u ≤ 10 := by omega
  by_cases htu : t ≤ u
  · rw [min_eq_left htu]
    have htuR : (t : ℝ) ≤ u := by exact_mod_cast htu
    have hsq : (t : ℝ) ^ 2 ≤ (u : ℝ) ^ 2 :=
      (sq_le_sq₀ (Nat.cast_nonneg _) (Nat.cast_nonneg _)).2 htuR
    interval_cases a
    all_goals interval_cases t
    all_goals norm_num at hsq ⊢
    all_goals nlinarith
  · have hut : u ≤ t := Nat.le_of_not_ge htu
    rw [min_eq_right hut]
    have hutR : (u : ℝ) ≤ t := by exact_mod_cast hut
    have hsq : (u : ℝ) ^ 2 ≤ (t : ℝ) ^ 2 :=
      (sq_le_sq₀ (Nat.cast_nonneg _) (Nat.cast_nonneg _)).2 hutR
    interval_cases a
    all_goals interval_cases u
    all_goals norm_num at hsq ⊢
    all_goals nlinarith

/-- The one-witness zero-attachment branch of the range theorem. -/
lemma conjecture100_of_zero_attachment
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (S : Finset V) (hS : G.IsNIndepSet G.indepNum S)
    (ha : 8 ≤ G.indepNum ∧ G.indepNum ≤ 11)
    (y : V) (hy : y ∉ S)
    (hzero : (S.filter (fun s ↦ Gᶜ.Adj y s)).card = 0) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  let T := S.filter (fun s ↦ Gᶜ.Adj y s)
  have hcard := hS.card_eq
  have htrade := attachment_tradeoff G S hS.isIndepSet (by omega) y hy
  dsimp only at htrade
  have hcase :
      (S.card = 8 ∧ T.card ≤ 5) ∨ (S.card = 9 ∧ T.card ≤ 6) ∨
      (S.card = 10 ∧ T.card ≤ 8) ∨ (S.card = 11 ∧ T.card ≤ 9) := by
    have hzeroT : T.card = 0 := hzero
    omega
  have hmargin := finite_middle_margin S.card T.card
    (by omega)
  have hleft : (0 : ℝ) ≤ 2 * (S.card : ℝ) - 4 + 2 * T.card := by
    have h8 : (8 : ℝ) ≤ S.card := by exact_mod_cast (hcard ▸ ha.1)
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

/-- Exact formalized WOWII 100 for every connected graph with independence
number between eight and eleven.  Complement connectedness is unnecessary. -/
theorem conjecture100_of_connected_of_indepNum_eight_to_eleven
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (ha : 8 ≤ G.indepNum ∧ G.indepNum ≤ 11) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  obtain ⟨S, hS⟩ := G.exists_isNIndepSet_indepNum
  have hcard := hS.card_eq
  have hSne : S.Nonempty := card_pos.mp (by omega : 0 < S.card)
  let s : V := hSne.choose
  have hs : s ∈ S := hSne.choose_spec
  obtain ⟨y, hsy⟩ := hG.preconnected.exists_adj_of_nontrivial s
  have hy : y ∉ S := by
    intro hyS
    exact hS.isIndepSet hs hyS hsy.ne hsy
  let T := S.filter (fun r ↦ Gᶜ.Adj y r)
  by_cases hzero : T.card = 0
  · exact conjecture100_of_zero_attachment G S hS ha y hy hzero
  · have hTne : T.Nonempty := card_pos.mp (Nat.pos_of_ne_zero hzero)
    have hyattach : ∃ r ∈ S, Gᶜ.Adj y r := by
      obtain ⟨r, hrT⟩ := hTne
      exact ⟨r, (mem_filter.mp hrT).1, (mem_filter.mp hrT).2⟩
    have hycross : ∃ r ∈ S, G.Adj y r := ⟨s, hs, hsy.symm⟩
    obtain ⟨z, hz, hzy, hzcross⟩ :=
      exists_second_outside_cross_witness G hG S hS.isIndepSet y hycross hyattach
    let U := S.filter (fun r ↦ Gᶜ.Adj z r)
    have ht : T.card + 1 ≤ S.card := by
      have hsnot : s ∉ T := by
        simp only [T, mem_filter, hs, true_and]
        intro hc
        rw [compl_adj] at hc
        exact hc.2 hsy.symm
      have hp : T ⊂ S := Finset.ssubset_iff_subset_ne.mpr
        ⟨filter_subset _ _, fun heq ↦ hsnot (heq.symm ▸ hs)⟩
      have hlt := card_lt_card hp
      omega
    have hu : U.card + 1 ≤ S.card := by
      obtain ⟨r, hrS, hzr⟩ := hzcross
      have hrnot : r ∉ U := by
        simp only [U, mem_filter, hrS, true_and]
        intro hc
        rw [compl_adj] at hc
        exact hc.2 hzr
      have hp : U ⊂ S := Finset.ssubset_iff_subset_ne.mpr
        ⟨filter_subset _ _, fun heq ↦ hrnot (heq.symm ▸ hrS)⟩
      have hlt := card_lt_card hp
      omega
    have hTy := attachment_tradeoff G S hS.isIndepSet (by omega) y hy
    have hUz := attachment_tradeoff G S hS.isIndepSet (by omega) z hz
    dsimp only at hTy hUz
    have henergyIE := two_outside_energy_certificate
      G S hS.isIndepSet (by omega) y z hy hz hzy.symm
    dsimp only at henergyIE
    have hmargin := two_attachment_margin S.card T.card U.card (hcard ▸ ha) ht hu
    have hleft : (0 : ℝ) ≤ 2 * (S.card : ℝ) - 4 + 2 * min T.card U.card := by
      have h8 : (8 : ℝ) ≤ S.card := by exact_mod_cast (hcard ▸ ha.1)
      linarith
    have hroot : 2 * (S.card : ℝ) - 4 + 2 * min T.card U.card <
        degreeL2Norm Gᶜ := by
      have hsqrt := (Real.lt_sqrt hleft).2 hmargin
      unfold TwoOutsideEnergyCertificate at henergyIE
      unfold degreeL2Norm
      exact hsqrt.trans_le (Real.sqrt_le_sqrt henergyIE)
    apply conjecture100_of_residual G
    dsimp
    have hlocalN : S.card - min T.card U.card ≤
        (Finset.univ.image (indepNeighborsCard G)).max' (by simp) := by
      by_cases htu : T.card ≤ U.card
      · rw [min_eq_left htu]
        exact hTy.1.trans ((Finset.univ.image (indepNeighborsCard G)).le_max'
          _ (mem_image_of_mem _ (mem_univ y)))
      · rw [min_eq_right (Nat.le_of_not_ge htu)]
        exact hUz.1.trans ((Finset.univ.image (indepNeighborsCard G)).le_max'
          _ (mem_image_of_mem _ (mem_univ z)))
    have hlocalR : ((S.card - min T.card U.card : ℕ) : ℝ) ≤
        ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
      exact_mod_cast hlocalN
    have hm : min T.card U.card ≤ S.card := by omega
    rw [Nat.cast_sub hm] at hlocalR
    rw [← hcard]
    linarith

end WrittenOnTheWallII.GraphConjecture100EightToEleven
