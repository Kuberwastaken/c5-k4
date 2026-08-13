import GraphConjecture100NearMiss

/-!
# WOWII 100: the independence-thirteen tradeoff

This file follows the exact upstream Lean term `degreeL2Norm Gᶜ`, not the
complement-diameter description in the upstream prose.

For a maximum independent 13-set `S` and an outside vertex `y`, let `t` be the
number of complement attachments from `y` into `S`.  The attachments raise
complement degree energy, while the other `13 - t` vertices form an
independent subset of the `G`-neighborhood of `y` and raise the local term.
The exact one-variable tradeoff closes the `indepNum = 13` near miss.
-/

namespace WrittenOnTheWallII.GraphConjecture100AlphaThirteen

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction
open WrittenOnTheWallII.GraphConjecture100FiniteRange

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [DecidableEq V] in
/-- Any explicit independent subset of the open neighborhood gives a lower
bound on local independence. -/
theorem card_le_indepNeighborsCard_of_indep_neighbor_subset
    (G : SimpleGraph V) [DecidableRel G.Adj] (y : V) (A : Finset V)
    (hA : G.IsIndepSet (A : Set V)) (hAy : ∀ a ∈ A, G.Adj y a) :
    A.card ≤ indepNeighborsCard G y := by
  let f : {a // a ∈ A} ↪ G.neighborSet y :=
    ⟨fun a ↦ ⟨a, hAy a a.property⟩,
      fun a b h ↦ by
        apply Subtype.ext
        exact congrArg (fun z : G.neighborSet y ↦ (z : V)) h⟩
  let A' : Finset (G.neighborSet y) := A.attach.map f
  have hA' : (G.induce (G.neighborSet y)).IsIndepSet (A' : Set _) := by
    intro a ha b hb hab hadj
    obtain ⟨a', ha'att, ha'eq⟩ := mem_map.mp (mem_coe.mp ha)
    obtain ⟨b', hb'att, hb'eq⟩ := mem_map.mp (mem_coe.mp hb)
    apply hA a'.property b'.property
    · intro habv
      apply hab
      rw [← ha'eq, ← hb'eq]
      exact Subtype.ext habv
    · rw [← ha'eq, ← hb'eq] at hadj
      exact induce_adj.mp hadj
  have hbound := hA'.card_le_indepNum
  simpa [A', indepNeighborsCard] using hbound

/-- The attachment/nonattachment tradeoff for an independent 13-set and an
outside vertex.  Here `t` is the number of complement attachments. -/
theorem alpha_thirteen_attachment_tradeoff
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (hS : G.IsIndepSet (S : Set V)) (hcard : S.card = 13)
    (y : V) (hy : y ∉ S) :
    let T := S.filter (fun s ↦ Gᶜ.Adj y s)
    let t := T.card
    (13 - t ≤ indepNeighborsCard G y) ∧
      ((1872 + 25 * t + t ^ 2 : ℕ) : ℝ) ≤
        ∑ v, (Gᶜ.degree v : ℝ) ^ 2 := by
  classical
  let T := S.filter (fun s ↦ Gᶜ.Adj y s)
  let A := S.filter (fun s ↦ G.Adj y s)
  have hpartition : A = S.filter (fun s ↦ ¬Gᶜ.Adj y s) := by
    ext s
    simp only [A, mem_filter]
    constructor
    · rintro ⟨hs, hys⟩
      refine ⟨hs, fun hcy ↦ ?_⟩
      rw [compl_adj] at hcy
      exact hcy.2 hys
    · rintro ⟨hs, hncy⟩
      have hne : y ≠ s := fun h ↦ hy (h ▸ hs)
      refine ⟨hs, ?_⟩
      by_contra hnG
      apply hncy
      rw [compl_adj]
      exact ⟨hne, hnG⟩
  have hcards : T.card + A.card = 13 := by
    rw [hpartition]
    simpa [T, hcard] using
      (card_filter_add_card_filter_not (s := S) (fun s ↦ Gᶜ.Adj y s))
  have hAind : G.IsIndepSet (A : Set V) := by
    intro u hu v hv huv hadj
    have huA : u ∈ A := mem_coe.mp hu
    have hvA : v ∈ A := mem_coe.mp hv
    exact hS (mem_filter.mp huA).1 (mem_filter.mp hvA).1 huv hadj
  have hAlocal : A.card ≤ indepNeighborsCard G y := by
    apply card_le_indepNeighborsCard_of_indep_neighbor_subset G y A hAind
    intro a ha
    exact (mem_filter.mp ha).2
  have hlocal : 13 - T.card ≤ indepNeighborsCard G y := by omega
  have hbase : ∀ s ∈ S, 12 ≤ Gᶜ.degree s := by
    intro s hs
    have h := card_sub_one_le_compl_degree_of_indep G S hS s hs
    omega
  have hatt : ∀ s ∈ T, 13 ≤ Gᶜ.degree s := by
    intro s hsT
    have hsS : s ∈ S := (mem_filter.mp hsT).1
    have hys : Gᶜ.Adj y s := (mem_filter.mp hsT).2
    have hsub : insert y (S.erase s) ⊆ Gᶜ.neighborFinset s := by
      intro v hv
      simp only [mem_insert, mem_erase] at hv
      rcases hv with rfl | ⟨hvs, hvS⟩
      · simpa only [mem_neighborFinset] using hys.symm
      · rw [mem_neighborFinset, compl_adj]
        exact ⟨hvs.symm, fun hsv ↦ hS hsS hvS hvs.symm hsv⟩
    have hc : (insert y (S.erase s)).card = 13 := by
      rw [card_insert_of_notMem]
      · rw [card_erase_of_mem hsS, hcard]
      · exact fun hyerase ↦ hy (mem_of_mem_erase hyerase)
    rw [← hc]
    exact card_le_card hsub
  have hydeg : T.card ≤ Gᶜ.degree y := by
    apply card_le_card
    intro s hs
    rw [mem_neighborFinset]
    exact (mem_filter.mp hs).2
  let U := S.filter (fun s ↦ ¬Gᶜ.Adj y s)
  have hTU : T.card + U.card = 13 := by
    simpa [T, U, hcard] using
      (card_filter_add_card_filter_not (s := S) (fun s ↦ Gᶜ.Adj y s))
  have hTsum : ((169 * T.card : ℕ) : ℝ) ≤
      ∑ s ∈ T, (Gᶜ.degree s : ℝ) ^ 2 := by
    calc
      ((169 * T.card : ℕ) : ℝ) = ∑ _s ∈ T, (169 : ℝ) := by
        simp [mul_comm]
      _ ≤ ∑ s ∈ T, (Gᶜ.degree s : ℝ) ^ 2 := by
        apply sum_le_sum
        intro s hs
        have hdegR : (13 : ℝ) ≤ Gᶜ.degree s := by exact_mod_cast hatt s hs
        nlinarith [sq_nonneg ((Gᶜ.degree s : ℝ) - 13)]
  have hUsum : ((144 * U.card : ℕ) : ℝ) ≤
      ∑ s ∈ U, (Gᶜ.degree s : ℝ) ^ 2 := by
    calc
      ((144 * U.card : ℕ) : ℝ) = ∑ _s ∈ U, (144 : ℝ) := by
        simp [mul_comm]
      _ ≤ ∑ s ∈ U, (Gᶜ.degree s : ℝ) ^ 2 := by
        apply sum_le_sum
        intro s hs
        have hsS : s ∈ S := (mem_filter.mp hs).1
        have hdegR : (12 : ℝ) ≤ Gᶜ.degree s := by exact_mod_cast hbase s hsS
        nlinarith [sq_nonneg ((Gᶜ.degree s : ℝ) - 12)]
  have hSsplit : ∑ s ∈ S, (Gᶜ.degree s : ℝ) ^ 2 =
      (∑ s ∈ T, (Gᶜ.degree s : ℝ) ^ 2) +
      ∑ s ∈ U, (Gᶜ.degree s : ℝ) ^ 2 := by
    simpa [T, U] using
      (sum_filter_add_sum_filter_not
        (s := S) (p := fun s ↦ Gᶜ.Adj y s)
        (f := fun s ↦ (Gᶜ.degree s : ℝ) ^ 2)).symm
  have hSenergy : ((1872 + 25 * T.card : ℕ) : ℝ) ≤
      ∑ s ∈ S, (Gᶜ.degree s : ℝ) ^ 2 := by
    rw [hSsplit]
    have hTUreal : (T.card : ℝ) + U.card = 13 := by exact_mod_cast hTU
    push_cast at hTsum hUsum ⊢
    nlinarith
  have hyenergy : ((T.card ^ 2 : ℕ) : ℝ) ≤ (Gᶜ.degree y : ℝ) ^ 2 := by
    exact_mod_cast (sq_le_sq₀ (Nat.zero_le _) (Nat.zero_le _)).2 hydeg
  have hins : ((1872 + 25 * T.card + T.card ^ 2 : ℕ) : ℝ) ≤
      ∑ v ∈ insert y S, (Gᶜ.degree v : ℝ) ^ 2 := by
    rw [sum_insert hy]
    push_cast at hSenergy hyenergy ⊢
    nlinarith
  have hall := hins.trans
    (sum_le_sum_of_subset_of_nonneg (subset_univ (insert y S))
      (fun _ _ _ ↦ sq_nonneg _))
  exact ⟨hlocal, hall⟩

/-- The exact arithmetic optimization of the attachment tradeoff for
`0 ≤ t ≤ 13`. -/
lemma twenty_two_add_two_mul_lt_sqrt_tradeoff (t : ℕ) (ht : t ≤ 13) :
    (22 : ℝ) + 2 * t <
      Real.sqrt ((1872 + 25 * t + t ^ 2 : ℕ) : ℝ) := by
  have htR : (t : ℝ) ≤ 13 := by exact_mod_cast ht
  have hfactor : (0 : ℝ) ≤ (13 - t) * (102 + 3 * t) :=
    mul_nonneg (sub_nonneg.mpr htR) (by positivity)
  apply (Real.lt_sqrt (by positivity)).2
  push_cast
  nlinarith

/-- The exact formalized WOWII 100 conclusion at independence number thirteen.
The proof balances complement energy against local independence rather than
requiring either universal lower bound to cross the wall alone. -/
theorem conjecture100_of_connected_of_indepNum_eq_thirteen
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (hthirteen : G.indepNum = 13) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  obtain ⟨S, hS⟩ := G.exists_isNIndepSet_indepNum
  have hcard : S.card = 13 := hS.card_eq.trans hthirteen
  have hSne : S.Nonempty := card_pos.mp (by omega : 0 < S.card)
  let s : V := hSne.choose
  have hs : s ∈ S := hSne.choose_spec
  obtain ⟨z, hszG⟩ := hG.preconnected.exists_adj_of_nontrivial s
  have hzout : z ∉ S := by
    intro hz
    exact hS.isIndepSet hs hz hszG.ne hszG
  let T := S.filter (fun a ↦ Gᶜ.Adj z a)
  have htrade := alpha_thirteen_attachment_tradeoff
    G S hS.isIndepSet hcard z hzout
  dsimp only at htrade
  have ht : T.card ≤ 13 := by
    exact (card_le_card (filter_subset _ _)).trans_eq hcard
  have hsqrt := twenty_two_add_two_mul_lt_sqrt_tradeoff T.card ht
  have hnorm : Real.sqrt (((1872 + 25 * T.card + T.card ^ 2 : ℕ) : ℝ)) ≤
      degreeL2Norm Gᶜ := by
    unfold degreeL2Norm
    exact Real.sqrt_le_sqrt htrade.2
  apply conjecture100_of_residual G
  dsimp
  have hlocalN : 13 - T.card ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp) :=
    htrade.1.trans
      ((Finset.univ.image (indepNeighborsCard G)).le_max'
        (indepNeighborsCard G z) (mem_image_of_mem _ (mem_univ z)))
  have hlocalR : ((13 - T.card : ℕ) : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
    exact_mod_cast hlocalN
  rw [hthirteen]
  norm_num
  have htN : T.card ≤ 13 := ht
  rw [Nat.cast_sub htN] at hlocalR
  push_cast at hlocalR
  linarith

end WrittenOnTheWallII.GraphConjecture100AlphaThirteen
