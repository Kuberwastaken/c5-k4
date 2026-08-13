import GraphConjecture100AlphaThirteen

/-!
# WOWII 100: parameterized middle-range attachment tradeoff

This file follows the exact upstream Lean expression `degreeL2Norm Gᶜ`, not
the complement-diameter reading described in the upstream prose.
-/

namespace WrittenOnTheWallII.GraphConjecture100MiddleRange

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction
open WrittenOnTheWallII.GraphConjecture100AlphaThirteen

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Parameterized attachment tradeoff.  If `S` is independent and `y ∉ S`,
write `t` for the number of complement neighbors of `y` in `S`.  Then the
other `|S|-t` vertices lower-bound local independence, while the complement
degree energy receives the displayed attachment correction. -/
theorem attachment_tradeoff
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (hS : G.IsIndepSet (S : Set V))
    (hpos : 1 ≤ S.card) (y : V) (hy : y ∉ S) :
    let T := S.filter (fun s ↦ Gᶜ.Adj y s)
    let t := T.card
    (S.card - t ≤ indepNeighborsCard G y) ∧
      ((((S.card - 1) ^ 2 * (S.card - t) + S.card ^ 2 * t + t ^ 2 : ℕ) : ℝ) ≤
        ∑ v, (Gᶜ.degree v : ℝ) ^ 2) := by
  classical
  let T := S.filter (fun s ↦ Gᶜ.Adj y s)
  let U := S.filter (fun s ↦ ¬Gᶜ.Adj y s)
  have hTU : T.card + U.card = S.card := by
    simpa [T, U] using
      (card_filter_add_card_filter_not (s := S) (fun s ↦ Gᶜ.Adj y s))
  have hUadj : ∀ s ∈ U, G.Adj y s := by
    intro s hs
    have hsS := (mem_filter.mp hs).1
    have hnot := (mem_filter.mp hs).2
    have hne : y ≠ s := fun h ↦ hy (h ▸ hsS)
    by_contra hn
    apply hnot
    rw [compl_adj]
    exact ⟨hne, hn⟩
  have hUind : G.IsIndepSet (U : Set V) := by
    intro a ha b hb hab hadj
    exact hS (mem_filter.mp (mem_coe.mp ha)).1
      (mem_filter.mp (mem_coe.mp hb)).1 hab hadj
  have hUlocal : U.card ≤ indepNeighborsCard G y :=
    card_le_indepNeighborsCard_of_indep_neighbor_subset G y U hUind hUadj
  have hlocal : S.card - T.card ≤ indepNeighborsCard G y := by omega
  have hbase : ∀ s ∈ S, S.card - 1 ≤ Gᶜ.degree s := by
    intro s hs
    exact card_sub_one_le_compl_degree_of_indep G S hS s hs
  have hatt : ∀ s ∈ T, S.card ≤ Gᶜ.degree s := by
    intro s hsT
    have hsS := (mem_filter.mp hsT).1
    have hys := (mem_filter.mp hsT).2
    have hsub : insert y (S.erase s) ⊆ Gᶜ.neighborFinset s := by
      intro v hv
      simp only [mem_insert, mem_erase] at hv
      rcases hv with rfl | ⟨hvs, hvS⟩
      · simpa only [mem_neighborFinset] using hys.symm
      · rw [mem_neighborFinset, compl_adj]
        exact ⟨hvs.symm, fun hsv ↦ hS hsS hvS hvs.symm hsv⟩
    have hc : (insert y (S.erase s)).card = S.card := by
      rw [card_insert_of_notMem]
      · rw [card_erase_of_mem hsS]
        omega
      · exact fun hyerase ↦ hy (mem_of_mem_erase hyerase)
    rw [← hc]
    exact card_le_card hsub
  have hydeg : T.card ≤ Gᶜ.degree y := by
    apply card_le_card
    intro s hs
    rw [mem_neighborFinset]
    exact (mem_filter.mp hs).2
  have hTsum : (((S.card ^ 2) * T.card : ℕ) : ℝ) ≤
      ∑ s ∈ T, (Gᶜ.degree s : ℝ) ^ 2 := by
    calc
      (((S.card ^ 2) * T.card : ℕ) : ℝ) =
          ∑ _s ∈ T, ((S.card : ℝ) ^ 2) := by simp [mul_comm]
      _ ≤ ∑ s ∈ T, (Gᶜ.degree s : ℝ) ^ 2 := by
        apply sum_le_sum
        intro s hs
        have hd : (S.card : ℝ) ≤ Gᶜ.degree s := by exact_mod_cast hatt s hs
        exact (sq_le_sq₀ (Nat.cast_nonneg _) (Nat.cast_nonneg _)).2 hd
  have hUsum : ((((S.card - 1) ^ 2) * U.card : ℕ) : ℝ) ≤
      ∑ s ∈ U, (Gᶜ.degree s : ℝ) ^ 2 := by
    calc
      ((((S.card - 1) ^ 2) * U.card : ℕ) : ℝ) =
          ∑ _s ∈ U, (((S.card - 1 : ℕ) : ℝ) ^ 2) := by simp [mul_comm]
      _ ≤ ∑ s ∈ U, (Gᶜ.degree s : ℝ) ^ 2 := by
        apply sum_le_sum
        intro s hs
        have hsS := (mem_filter.mp hs).1
        have hd : ((S.card - 1 : ℕ) : ℝ) ≤ Gᶜ.degree s := by
          exact_mod_cast hbase s hsS
        exact (sq_le_sq₀ (Nat.cast_nonneg _) (Nat.cast_nonneg _)).2 hd
  have hsplit : ∑ s ∈ S, (Gᶜ.degree s : ℝ) ^ 2 =
      (∑ s ∈ T, (Gᶜ.degree s : ℝ) ^ 2) +
      ∑ s ∈ U, (Gᶜ.degree s : ℝ) ^ 2 := by
    simpa [T, U] using
      (sum_filter_add_sum_filter_not
        (s := S) (p := fun s ↦ Gᶜ.Adj y s)
        (f := fun s ↦ (Gᶜ.degree s : ℝ) ^ 2)).symm
  have hSenergy :
      (((S.card - 1) ^ 2 * (S.card - T.card) + S.card ^ 2 * T.card : ℕ) : ℝ) ≤
        ∑ s ∈ S, (Gᶜ.degree s : ℝ) ^ 2 := by
    rw [hsplit]
    have hTUreal : (T.card : ℝ) + U.card = S.card := by exact_mod_cast hTU
    have ht : T.card ≤ S.card := by omega
    simp only [Nat.cast_add, Nat.cast_mul, Nat.cast_pow,
      Nat.cast_sub ht, Nat.cast_sub hpos] at hTsum hUsum ⊢
    nlinarith
  have hyenergy : ((T.card ^ 2 : ℕ) : ℝ) ≤ (Gᶜ.degree y : ℝ) ^ 2 := by
    exact_mod_cast (sq_le_sq₀ (Nat.zero_le _) (Nat.zero_le _)).2 hydeg
  have hins :
      ((((S.card - 1) ^ 2 * (S.card - T.card) + S.card ^ 2 * T.card +
        T.card ^ 2 : ℕ) : ℝ) ≤
        ∑ v ∈ insert y S, (Gᶜ.degree v : ℝ) ^ 2) := by
    rw [sum_insert hy]
    push_cast at hSenergy hyenergy ⊢
    nlinarith
  exact ⟨hlocal, hins.trans
    (sum_le_sum_of_subset_of_nonneg (subset_univ (insert y S))
      (fun _ _ _ ↦ sq_nonneg _))⟩

/-- Symbolic range: for every `a ≥ 12` and every attachment count
`t ≤ a-1`, the parameterized tradeoff crosses the exact residual wall. -/
lemma symbolic_margin_of_twelve_le
    (a t : ℕ) (ha : 12 ≤ a) (ht : t + 1 ≤ a) :
    (2 * (a : ℝ) - 4 + 2 * t) ^ 2 <
      (((a - 1) ^ 2 * (a - t) + a ^ 2 * t + t ^ 2 : ℕ) : ℝ) := by
  have ht' : t ≤ a := by omega
  have ha1 : 1 ≤ a := by omega
  simp only [Nat.cast_add, Nat.cast_mul, Nat.cast_pow,
    Nat.cast_sub ht', Nat.cast_sub ha1]
  have haR : (12 : ℝ) ≤ a := by exact_mod_cast ha
  have htR : (t : ℝ) + 1 ≤ a := by exact_mod_cast ht
  let k : ℝ := a - 12
  have hk : 0 ≤ k := sub_nonneg.mpr haR
  have hbase : (0 : ℝ) < k ^ 3 + 21 * k ^ 2 + 116 * k + 62 := by
    have hk2 : 0 ≤ k ^ 2 := sq_nonneg k
    have hk3 : 0 ≤ k ^ 3 := by
      rw [pow_succ]
      exact mul_nonneg hk2 hk
    positivity
  have hdec : (0 : ℝ) ≤ 3 * (a - 1 - t) * (3 * a + t - 6) := by
    have hleft : 0 ≤ (a : ℝ) - 1 - t := by linarith
    have hright : 0 ≤ 3 * (a : ℝ) + t - 6 := by linarith
    positivity
  dsimp [k] at hbase
  have hid :
      (((a - 1 : ℝ) ^ 2 * (a - t) + a ^ 2 * t + t ^ 2) -
        (2 * a - 4 + 2 * t) ^ 2) =
      ((a - 12) ^ 3 + 21 * (a - 12) ^ 2 + 116 * (a - 12) + 62) +
        3 * (a - 1 - t) * (3 * a + t - 6) := by
    ring
  norm_num only [Nat.cast_one] at *
  nlinarith

/-- Exact finite exceptions below the symbolic range.  These are conditional
attachment-count slices, not unconditional graph classes. -/
lemma finite_middle_margin
    (a t : ℕ)
    (hcase :
      (a = 4 ∧ t ≤ 1) ∨ (a = 5 ∧ t ≤ 2) ∨ (a = 6 ∧ t ≤ 2) ∨
      (a = 7 ∧ t ≤ 3) ∨ (a = 8 ∧ t ≤ 5) ∨ (a = 9 ∧ t ≤ 6) ∨
      (a = 10 ∧ t ≤ 8) ∨ (a = 11 ∧ t ≤ 9)) :
    (2 * (a : ℝ) - 4 + 2 * t) ^ 2 <
      (((a - 1) ^ 2 * (a - t) + a ^ 2 * t + t ^ 2 : ℕ) : ℝ) := by
  rcases hcase with h | h | h | h | h | h | h | h
  all_goals rcases h with ⟨rfl, ht⟩
  all_goals interval_cases t <;> norm_num

/-- Connected graphs in the symbolic range `indepNum ≥ 12` satisfy the exact
formalized WOWII 100 inequality.  Complement connectedness is unnecessary. -/
theorem conjecture100_of_connected_of_twelve_le_indepNum
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (ha : 12 ≤ G.indepNum) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  obtain ⟨S, hS⟩ := G.exists_isNIndepSet_indepNum
  have hcard : S.card = G.indepNum := hS.card_eq
  have hSne : S.Nonempty := card_pos.mp (by omega : 0 < S.card)
  let s : V := hSne.choose
  have hs : s ∈ S := hSne.choose_spec
  obtain ⟨y, hsy⟩ := hG.preconnected.exists_adj_of_nontrivial s
  have hy : y ∉ S := by
    intro hyS
    exact hS.isIndepSet hs hyS hsy.ne hsy
  let T := S.filter (fun a ↦ Gᶜ.Adj y a)
  have htrade := attachment_tradeoff G S hS.isIndepSet (by omega) y hy
  dsimp only at htrade
  have ht : T.card + 1 ≤ S.card := by
    have hsnot : s ∉ T := by
      simp only [T, mem_filter, hs, true_and]
      intro hc
      rw [compl_adj] at hc
      exact hc.2 hsy.symm
    have hsubset : T ⊆ S := filter_subset _ _
    have hne : T ≠ S := by
      intro heq
      exact hsnot (heq.symm ▸ hs)
    have hproper : T ⊂ S := Finset.ssubset_iff_subset_ne.mpr ⟨hsubset, hne⟩
    have hlt := card_lt_card hproper
    omega
  have hmargin := symbolic_margin_of_twelve_le S.card T.card
    (hcard ▸ ha) ht
  have hroot :
      2 * (S.card : ℝ) - 4 + 2 * T.card <
        Real.sqrt
          (((S.card - 1) ^ 2 * (S.card - T.card) +
            S.card ^ 2 * T.card + T.card ^ 2 : ℕ) : ℝ) := by
    have hleft : (0 : ℝ) ≤ 2 * (S.card : ℝ) - 4 + 2 * T.card := by
      have hcardR : (12 : ℝ) ≤ S.card := by exact_mod_cast (hcard ▸ ha)
      linarith
    apply (Real.lt_sqrt hleft).2
    exact hmargin
  have hnorm := Real.sqrt_le_sqrt htrade.2
  apply conjecture100_of_residual G
  dsimp
  have hlocalN : S.card - T.card ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp) :=
    htrade.1.trans
      ((Finset.univ.image (indepNeighborsCard G)).le_max'
        (indepNeighborsCard G y) (mem_image_of_mem _ (mem_univ y)))
  have hlocalR : ((S.card - T.card : ℕ) : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
    exact_mod_cast hlocalN
  have ht0 : T.card ≤ S.card := by omega
  rw [Nat.cast_sub ht0] at hlocalR
  rw [← hcard]
  unfold degreeL2Norm at hnorm ⊢
  linarith

end WrittenOnTheWallII.GraphConjecture100MiddleRange
