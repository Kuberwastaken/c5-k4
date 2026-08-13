import GraphConjecture100ThreeWitness

/-!
# WOWII 100: cross-boundary witness classification

This file follows the exact upstream Lean expression `degreeL2Norm Gᶜ`, not
the complement-diameter reading in the historical prose.
-/

namespace WrittenOnTheWallII.GraphConjecture100WitnessClassification

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction
open WrittenOnTheWallII.GraphConjecture100MiddleRange
open WrittenOnTheWallII.GraphConjecture100IncidenceEnergy
open WrittenOnTheWallII.GraphConjecture100ThreeWitness

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- The three-vertex version of the incidence sum used in v14. -/
lemma sum_tripleAttachments_eq
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (y z w : V)
    (hyz : y ≠ z) (hyw : y ≠ w) (hzw : z ≠ w) :
    ∑ s ∈ S, ((insert y (insert z {w}) : Finset V).filter
      (fun x ↦ Gᶜ.Adj s x)).card =
      (S.filter (fun s ↦ Gᶜ.Adj y s)).card +
      (S.filter (fun s ↦ Gᶜ.Adj z s)).card +
      (S.filter (fun s ↦ Gᶜ.Adj w s)).card := by
  classical
  have hp : ∀ s : V,
      ((insert y (insert z {w}) : Finset V).filter
        (fun x ↦ Gᶜ.Adj s x)).card =
        (if Gᶜ.Adj s y then 1 else 0) +
        (if Gᶜ.Adj s z then 1 else 0) +
        (if Gᶜ.Adj s w then 1 else 0) := by
    intro s
    rw [filter_insert, filter_insert, filter_singleton]
    by_cases hsy : Gᶜ.Adj s y <;> by_cases hsz : Gᶜ.Adj s z <;>
      by_cases hsw : Gᶜ.Adj s w <;> simp [hsy, hsz, hsw, hyz, hyw, hzw]
  simp_rw [hp, sum_add_distrib]
  simp [Gᶜ.adj_comm, add_assoc]

/-- At a member of an independent set, the complement degree contains the
other set vertices and all incidences from an explicit outside triple. -/
lemma card_sub_one_add_tripleAttachments_le_degree
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (hS : G.IsIndepSet (S : Set V))
    (y z w s : V) (hy : y ∉ S) (hz : z ∉ S) (hw : w ∉ S) (hs : s ∈ S) :
    S.card - 1 + ((insert y (insert z {w}) : Finset V).filter
      (fun x ↦ Gᶜ.Adj s x)).card ≤ Gᶜ.degree s := by
  let K := ((insert y (insert z {w}) : Finset V).filter
    (fun x ↦ Gᶜ.Adj s x))
  have hKsub : K ⊆ Gᶜ.neighborFinset s := by
    intro x hx
    rw [mem_neighborFinset]
    exact (mem_filter.mp hx).2
  have hSsub : S.erase s ⊆ Gᶜ.neighborFinset s := by
    intro x hx
    have hxS := (mem_erase.mp hx).2
    have hxs := (mem_erase.mp hx).1
    rw [mem_neighborFinset, compl_adj]
    exact ⟨hxs.symm, fun hsx ↦ hS hs hxS hxs.symm hsx⟩
  have hdisj : Disjoint (S.erase s) K := by
    rw [Finset.disjoint_left]
    intro x hxS hxK
    have hxP := (mem_filter.mp hxK).1
    simp only [mem_insert, mem_singleton] at hxP
    rcases hxP with rfl | rfl | rfl
    · exact hy (mem_of_mem_erase hxS)
    · exact hz (mem_of_mem_erase hxS)
    · exact hw (mem_of_mem_erase hxS)
  have hunion : S.erase s ∪ K ⊆ Gᶜ.neighborFinset s := union_subset hSsub hKsub
  have hcard : (S.erase s ∪ K).card = S.card - 1 + K.card := by
    rw [card_union_of_disjoint hdisj, card_erase_of_mem hs]
  rw [← hcard]
  exact card_le_card hunion

/-- Graph-level derivation of the aggregate three-witness energy certificate. -/
theorem three_outside_energy_certificate
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (hS : G.IsIndepSet (S : Set V)) (hpos : 1 ≤ S.card)
    (y z w : V) (hy : y ∉ S) (hz : z ∉ S) (hw : w ∉ S)
    (hyz : y ≠ z) (hyw : y ≠ w) (hzw : z ≠ w) :
    let t := (S.filter (fun s ↦ Gᶜ.Adj y s)).card
    let u := (S.filter (fun s ↦ Gᶜ.Adj z s)).card
    let v := (S.filter (fun s ↦ Gᶜ.Adj w s)).card
    ThreeOutsideEnergyCertificate G S.card t u v := by
  classical
  let T := S.filter (fun s ↦ Gᶜ.Adj y s)
  let U := S.filter (fun s ↦ Gᶜ.Adj z s)
  let W := S.filter (fun s ↦ Gᶜ.Adj w s)
  let k : V → ℕ := fun s ↦
    ((insert y (insert z {w}) : Finset V).filter (fun x ↦ Gᶜ.Adj s x)).card
  have hkSum : ∑ s ∈ S, k s = T.card + U.card + W.card := by
    exact sum_tripleAttachments_eq G S y z w hyz hyw hzw
  have hpoint : ∀ s ∈ S,
      (((S.card - 1 : ℕ) : ℝ) ^ 2 + (2 * S.card - 1 : ℕ) * k s) ≤
        (Gᶜ.degree s : ℝ) ^ 2 := by
    intro s hs
    have hd := card_sub_one_add_tripleAttachments_le_degree
      G S hS y z w s hy hz hw hs
    have hk3 : k s ≤ 3 :=
      (card_le_card (filter_subset _ _)).trans (by simp [hyz, hyw, hzw])
    have hbase : 1 ≤ 2 * S.card := by omega
    have hdR : (((S.card - 1) + k s : ℕ) : ℝ) ≤ Gᶜ.degree s := by
      exact_mod_cast hd
    simp only [Nat.cast_add, Nat.cast_sub hpos, Nat.cast_sub hbase,
      Nat.cast_mul, Nat.cast_one] at hdR ⊢
    have hkR : (0 : ℝ) ≤ k s := Nat.cast_nonneg _
    have haR : (1 : ℝ) ≤ S.card := by exact_mod_cast hpos
    by_cases hk0 : k s = 0
    · rw [hk0] at hdR ⊢
      norm_num at hdR ⊢
      nlinarith [sq_nonneg ((Gᶜ.degree s : ℝ) - ((S.card : ℝ) - 1))]
    · have hkoneN : 1 ≤ k s := Nat.one_le_iff_ne_zero.mpr hk0
      have hkoneR : (1 : ℝ) ≤ k s := by exact_mod_cast hkoneN
      have hbasek : (0 : ℝ) ≤ ((S.card : ℝ) - 1) + k s := by linarith
      have hdeg0 : (0 : ℝ) ≤ Gᶜ.degree s := Nat.cast_nonneg _
      have hsq : (((S.card : ℝ) - 1) + k s) ^ 2 ≤
          (Gᶜ.degree s : ℝ) ^ 2 := (sq_le_sq₀ hbasek hdeg0).2 hdR
      have hid : (((S.card : ℝ) - 1) + k s) ^ 2 =
          ((S.card : ℝ) - 1) ^ 2 + (2 * (S.card : ℝ) - 1) * k s +
            (k s : ℝ) * ((k s : ℝ) - 1) := by ring
      rw [hid] at hsq
      have hnonneg := mul_nonneg hkR (sub_nonneg.mpr hkoneR)
      norm_num only [Nat.cast_ofNat] at hsq ⊢
      linarith
  have hSsum :
      (((S.card * (S.card - 1) ^ 2 + (2 * S.card - 1) *
        (T.card + U.card + W.card) : ℕ) : ℝ) ≤
        ∑ s ∈ S, (Gᶜ.degree s : ℝ) ^ 2) := by
    calc
      (((S.card * (S.card - 1) ^ 2 + (2 * S.card - 1) *
          (T.card + U.card + W.card) : ℕ) : ℝ) =
        ∑ s ∈ S, ((((S.card - 1 : ℕ) : ℝ) ^ 2) +
          ((2 * S.card - 1 : ℕ) : ℝ) * k s)) := by
            rw [← hkSum]
            push_cast
            simp [sum_add_distrib, mul_sum]
      _ ≤ ∑ s ∈ S, (Gᶜ.degree s : ℝ) ^ 2 := sum_le_sum hpoint
  have hydeg : T.card ≤ Gᶜ.degree y := by
    apply card_le_card
    intro s hs
    rw [mem_neighborFinset]
    exact (mem_filter.mp hs).2
  have hzdeg : U.card ≤ Gᶜ.degree z := by
    apply card_le_card
    intro s hs
    rw [mem_neighborFinset]
    exact (mem_filter.mp hs).2
  have hwdeg : W.card ≤ Gᶜ.degree w := by
    apply card_le_card
    intro s hs
    rw [mem_neighborFinset]
    exact (mem_filter.mp hs).2
  have hysq : ((T.card ^ 2 : ℕ) : ℝ) ≤ (Gᶜ.degree y : ℝ) ^ 2 := by
    exact_mod_cast (sq_le_sq₀ (Nat.zero_le _) (Nat.zero_le _)).2 hydeg
  have hzsq : ((U.card ^ 2 : ℕ) : ℝ) ≤ (Gᶜ.degree z : ℝ) ^ 2 := by
    exact_mod_cast (sq_le_sq₀ (Nat.zero_le _) (Nat.zero_le _)).2 hzdeg
  have hwsq : ((W.card ^ 2 : ℕ) : ℝ) ≤ (Gᶜ.degree w : ℝ) ^ 2 := by
    exact_mod_cast (sq_le_sq₀ (Nat.zero_le _) (Nat.zero_le _)).2 hwdeg
  have hins :
      (((S.card * (S.card - 1) ^ 2 + (2 * S.card - 1) *
        (T.card + U.card + W.card) + T.card ^ 2 + U.card ^ 2 + W.card ^ 2 : ℕ) : ℝ) ≤
        ∑ x ∈ insert y (insert z (insert w S)), (Gᶜ.degree x : ℝ) ^ 2) := by
    rw [sum_insert, sum_insert, sum_insert]
    · push_cast at hSsum hysq hzsq hwsq ⊢
      nlinarith
    · exact hw
    · simp [hzw, hz]
    · simp [hyw, hyz, hy]
  unfold ThreeOutsideEnergyCertificate
  exact hins.trans
    (sum_le_sum_of_subset_of_nonneg (subset_univ (insert y (insert z (insert w S))))
      (fun _ _ _ ↦ sq_nonneg _))

/-- The two-witness package closes the small range when coverage prevents the
two complement-attachment sets from having more than `a` total members. -/
lemma two_attachment_margin_four_to_seven_of_sum_le
    (a t u : ℕ) (ha : 4 ≤ a ∧ a ≤ 7)
    (ht : t + 1 ≤ a) (hu : u + 1 ≤ a) (hsum : t + u ≤ a) :
    (2 * (a : ℝ) - 4 + 2 * min t u) ^ 2 <
      ((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u) + t ^ 2 + u ^ 2 : ℕ) : ℝ) := by
  have ha0 := ha.1
  have ha1 := ha.2
  have ht7 : t ≤ 6 := by omega
  have hu7 : u ≤ 6 := by omega
  interval_cases a <;> interval_cases t <;> interval_cases u <;> norm_num at *

/-- A cross-boundary witness is outside `S` and adjacent in `G` to a member
of `S`. -/
def CrossWitness (G : SimpleGraph V) (S : Finset V) (y : V) : Prop :=
  y ∉ S ∧ ∃ s ∈ S, G.Adj y s

omit [Fintype V] [DecidableEq V] in
lemma cross_witness_covers
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (S : Finset V) (hS : G.IsIndepSet (S : Set V))
    (s : V) (hs : s ∈ S) :
    ∃ y, CrossWitness G S y ∧ G.Adj y s := by
  obtain ⟨y, hsy⟩ := hG.preconnected.exists_adj_of_nontrivial s
  have hy : y ∉ S := by
    intro hyS
    exact hS hs hyS hsy.ne hsy
  exact ⟨y, ⟨hy, s, hs, hsy.symm⟩, hsy.symm⟩

omit [Fintype V] [DecidableEq V] in
/-- Pure witness classification: one exhaustive witness, two exhaustive
witnesses, or three distinct witnesses. -/
lemma cross_witness_trichotomy
    (G : SimpleGraph V) (S : Finset V)
    (hne : ∃ y, CrossWitness G S y) :
    (∃ y, CrossWitness G S y ∧ ∀ x, CrossWitness G S x → x = y) ∨
    (∃ y z, CrossWitness G S y ∧ CrossWitness G S z ∧ y ≠ z ∧
      ∀ x, CrossWitness G S x → x = y ∨ x = z) ∨
    (∃ y z w, CrossWitness G S y ∧ CrossWitness G S z ∧
      CrossWitness G S w ∧ y ≠ z ∧ y ≠ w ∧ z ≠ w) := by
  obtain ⟨y, hy⟩ := hne
  by_cases hone : ∀ x, CrossWitness G S x → x = y
  · exact Or.inl ⟨y, hy, hone⟩
  · right
    push_neg at hone
    obtain ⟨z, hz, hzy⟩ := hone
    by_cases htwo : ∀ x, CrossWitness G S x → x = y ∨ x = z
    · exact Or.inl ⟨y, z, hy, hz, hzy.symm, htwo⟩
    · right
      push_neg at htwo
      obtain ⟨w, hw, hwy, hwz⟩ := htwo
      exact ⟨y, z, w, hy, hz, hw, hzy.symm, hwy.symm, hwz.symm⟩

omit [Fintype V] in
/-- A single exhaustive cross witness is adjacent to every member of `S`, so
its complement attachment count is zero. -/
lemma zero_attachment_of_unique_cross_witness
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (S : Finset V) (hS : G.IsIndepSet (S : Set V))
    (y : V)
    (hunique : ∀ x, CrossWitness G S x → x = y) :
    (S.filter (fun s ↦ Gᶜ.Adj y s)).card = 0 := by
  rw [card_eq_zero]
  by_contra hne
  obtain ⟨s, hsT⟩ := nonempty_iff_ne_empty.mpr hne
  obtain ⟨x, hx, hxs⟩ := cross_witness_covers G hG S hS s (mem_filter.mp hsT).1
  have hxy := hunique x hx
  subst x
  have hc := (mem_filter.mp hsT).2
  rw [compl_adj] at hc
  exact hc.2 hxs

omit [Fintype V] in
/-- With exactly two exhaustive cross witnesses, their complement attachment
sets are disjoint, hence their total attachment count is at most `|S|`. -/
lemma two_attachment_sum_le_of_exhaustive
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (S : Finset V) (hS : G.IsIndepSet (S : Set V))
    (y z : V) (hexhaust : ∀ x, CrossWitness G S x → x = y ∨ x = z) :
    (S.filter (fun s ↦ Gᶜ.Adj y s)).card +
      (S.filter (fun s ↦ Gᶜ.Adj z s)).card ≤ S.card := by
  let T := S.filter (fun s ↦ Gᶜ.Adj y s)
  let U := S.filter (fun s ↦ Gᶜ.Adj z s)
  have hd : Disjoint T U := by
    rw [Finset.disjoint_left]
    intro s hsT hsU
    obtain ⟨x, hx, hxs⟩ := cross_witness_covers G hG S hS s (mem_filter.mp hsT).1
    rcases hexhaust x hx with rfl | rfl
    · have hc := (mem_filter.mp hsT).2
      rw [compl_adj] at hc
      exact hc.2 hxs
    · have hc := (mem_filter.mp hsU).2
      rw [compl_adj] at hc
      exact hc.2 hxs
  rw [← card_union_of_disjoint hd]
  exact card_le_card (union_subset (filter_subset _ _) (filter_subset _ _))

/-- The zero-attachment one-witness branch closes every remaining row. -/
lemma conjecture100_of_zero_attachment_four_to_seven
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (S : Finset V) (hS : G.IsNIndepSet G.indepNum S)
    (ha : 4 ≤ G.indepNum ∧ G.indepNum ≤ 7)
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
    have ha' : 4 ≤ S.card ∧ S.card ≤ 7 := hcard ▸ ha
    have hlo := ha'.1
    have hhi := ha'.2
    rw [hz]
    interval_cases hSc : S.card <;> norm_num at *
  have hleft : (0 : ℝ) ≤ 2 * (S.card : ℝ) - 4 + 2 * T.card := by
    have h4 : (4 : ℝ) ≤ S.card := by exact_mod_cast (hcard ▸ ha.1)
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

/-- Exact two-witness conclusion in the small range under the coverage sum
constraint. -/
lemma conjecture100_of_two_outside_energy_of_sum_le
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (a t u : ℕ) (haG : G.indepNum = a) (ha : 4 ≤ a ∧ a ≤ 7)
    (ht : t + 1 ≤ a) (hu : u + 1 ≤ a) (hsum : t + u ≤ a)
    (hlocalT : a - t ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp))
    (hlocalU : a - u ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp))
    (henergy : TwoOutsideEnergyCertificate G a t u) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  have hmargin := two_attachment_margin_four_to_seven_of_sum_le
    a t u ha ht hu hsum
  have hleft : (0 : ℝ) ≤ 2 * (a : ℝ) - 4 + 2 * min t u := by
    have haR : (4 : ℝ) ≤ a := by exact_mod_cast ha.1
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
    · rw [min_eq_left htu]
      exact hlocalT
    · rw [min_eq_right (Nat.le_of_not_ge htu)]
      exact hlocalU
  have hlocalR : ((a - min t u : ℕ) : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
    exact_mod_cast hlocalN
  have hm : min t u ≤ a := by omega
  rw [Nat.cast_sub hm] at hlocalR
  rw [haG]
  linarith

/-- Exact formalized WOWII #100 for connected graphs in the final independence
range `4 ≤ α ≤ 7`.  Complement connectedness is unnecessary. -/
theorem conjecture100_of_connected_of_indepNum_four_to_seven
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (ha : 4 ≤ G.indepNum ∧ G.indepNum ≤ 7) :
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
    exact conjecture100_of_zero_attachment_four_to_seven G S hS ha y hy.1
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
    exact conjecture100_of_two_outside_energy_of_sum_le G S.card T.card U.card
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
    exact conjecture100_of_three_outside_energy_certificate
      G S.card T.card U.card W.card hcard.symm (hcard ▸ ha)
      ht hu hv hlocalT hlocalU hlocalW henergy

end WrittenOnTheWallII.GraphConjecture100WitnessClassification
