import GraphConjecture100MiddleRange

/-!
# WOWII 100: graph-level two-vertex incidence energy

This file follows the exact upstream Lean expression `degreeL2Norm Gᶜ`, not
the complement-diameter reading in the upstream prose.
-/

namespace WrittenOnTheWallII.GraphConjecture100IncidenceEnergy

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The aggregate energy proposition used by the two-outside coordinate model. -/
def TwoOutsideEnergyCertificate
    (G : SimpleGraph V) [DecidableRel G.Adj] (a t u : ℕ) : Prop :=
  (((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u) + t ^ 2 + u ^ 2 : ℕ) : ℝ) ≤
    ∑ v, (Gᶜ.degree v : ℝ) ^ 2)

/-- For each vertex of an independent set, its complement degree contains all
other set vertices plus every attaching member of the explicit outside pair. -/
lemma card_sub_one_add_pairAttachments_le_degree
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (hS : G.IsIndepSet (S : Set V))
    (y z s : V) (hy : y ∉ S) (hz : z ∉ S) (hs : s ∈ S) :
    S.card - 1 + ((insert y {z} : Finset V).filter (fun w ↦ Gᶜ.Adj s w)).card ≤
      Gᶜ.degree s := by
  let K := (insert y {z} : Finset V).filter (fun w ↦ Gᶜ.Adj s w)
  have hKsub : K ⊆ Gᶜ.neighborFinset s := by
    intro w hw
    rw [mem_neighborFinset]
    exact (mem_filter.mp hw).2
  have hSsub : S.erase s ⊆ Gᶜ.neighborFinset s := by
    intro w hw
    have hwS := (mem_erase.mp hw).2
    have hws := (mem_erase.mp hw).1
    rw [mem_neighborFinset, compl_adj]
    exact ⟨hws.symm, fun hsw ↦ hS hs hwS hws.symm hsw⟩
  have hdisj : Disjoint (S.erase s) K := by
    rw [Finset.disjoint_left]
    intro w hwS hwK
    have hwPair := (mem_filter.mp hwK).1
    simp only [mem_insert, mem_singleton] at hwPair
    rcases hwPair with rfl | rfl
    · exact hy (mem_of_mem_erase hwS)
    · exact hz (mem_of_mem_erase hwS)
  have hunion : S.erase s ∪ K ⊆ Gᶜ.neighborFinset s := union_subset hSsub hKsub
  have hcard : (S.erase s ∪ K).card = S.card - 1 + K.card := by
    rw [card_union_of_disjoint hdisj, card_erase_of_mem hs]
  rw [← hcard]
  exact card_le_card hunion

omit [Fintype V] in
/-- The attachment multiplicities over `S` count exactly the incidences from
the two outside vertices; an edge attached to both is counted twice, once for
each genuine degree increment. -/
lemma sum_pairAttachments_eq
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (y z : V) (hyz : y ≠ z) :
    ∑ s ∈ S, ((insert y {z} : Finset V).filter (fun w ↦ Gᶜ.Adj s w)).card =
      (S.filter (fun s ↦ Gᶜ.Adj y s)).card +
    (S.filter (fun s ↦ Gᶜ.Adj z s)).card := by
  classical
  have hpair : ∀ s : V,
      ((insert y {z} : Finset V).filter (fun w ↦ Gᶜ.Adj s w)).card =
        (if Gᶜ.Adj s y then 1 else 0) + (if Gᶜ.Adj s z then 1 else 0) := by
    intro s
    rw [filter_insert, filter_singleton]
    by_cases hsy : Gᶜ.Adj s y <;> by_cases hsz : Gᶜ.Adj s z <;>
      simp [hsy, hsz, hyz]
  simp_rw [hpair, sum_add_distrib]
  simp [Gᶜ.adj_comm]

/-- Graph-level proof of the aggregate certificate `E2`, with overlap handled
by the incidence multiplicity at each vertex of `S`. -/
theorem two_outside_energy_certificate
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (hS : G.IsIndepSet (S : Set V)) (hpos : 1 ≤ S.card)
    (y z : V) (hy : y ∉ S) (hz : z ∉ S) (hyz : y ≠ z) :
    let t := (S.filter (fun s ↦ Gᶜ.Adj y s)).card
    let u := (S.filter (fun s ↦ Gᶜ.Adj z s)).card
    TwoOutsideEnergyCertificate G S.card t u := by
  classical
  let T := S.filter (fun s ↦ Gᶜ.Adj y s)
  let U := S.filter (fun s ↦ Gᶜ.Adj z s)
  let k : V → ℕ := fun s ↦
    ((insert y {z} : Finset V).filter (fun w ↦ Gᶜ.Adj s w)).card
  have hkSum : ∑ s ∈ S, k s = T.card + U.card := by
    exact sum_pairAttachments_eq G S y z hyz
  have hpoint : ∀ s ∈ S,
      (((S.card - 1 : ℕ) : ℝ) ^ 2 + (2 * S.card - 1 : ℕ) * k s) ≤
        (Gᶜ.degree s : ℝ) ^ 2 := by
    intro s hs
    have hd := card_sub_one_add_pairAttachments_le_degree G S hS y z s hy hz hs
    have hk2 : k s ≤ 2 := by
      exact (card_le_card (filter_subset _ _)).trans (by simp [hyz])
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
        (T.card + U.card) : ℕ) : ℝ) ≤
        ∑ s ∈ S, (Gᶜ.degree s : ℝ) ^ 2) := by
    calc
      (((S.card * (S.card - 1) ^ 2 + (2 * S.card - 1) *
          (T.card + U.card) : ℕ) : ℝ) =
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
  have hysq : ((T.card ^ 2 : ℕ) : ℝ) ≤ (Gᶜ.degree y : ℝ) ^ 2 := by
    exact_mod_cast (sq_le_sq₀ (Nat.zero_le _) (Nat.zero_le _)).2 hydeg
  have hzsq : ((U.card ^ 2 : ℕ) : ℝ) ≤ (Gᶜ.degree z : ℝ) ^ 2 := by
    exact_mod_cast (sq_le_sq₀ (Nat.zero_le _) (Nat.zero_le _)).2 hzdeg
  have hins :
      (((S.card * (S.card - 1) ^ 2 + (2 * S.card - 1) *
        (T.card + U.card) + T.card ^ 2 + U.card ^ 2 : ℕ) : ℝ) ≤
        ∑ v ∈ insert y (insert z S), (Gᶜ.degree v : ℝ) ^ 2) := by
    rw [sum_insert, sum_insert]
    · push_cast at hSsum hysq hzsq ⊢
      nlinarith
    · exact hz
    · simp [hyz, hy]
  unfold TwoOutsideEnergyCertificate
  exact hins.trans
    (sum_le_sum_of_subset_of_nonneg (subset_univ (insert y (insert z S)))
      (fun _ _ _ ↦ sq_nonneg _))

omit [Fintype V] [DecidableEq V] in
/-- If one outside cross-edge witness also has a complement attachment into
`S`, connectedness supplies a second distinct outside cross-edge witness.
This is exactly the branch not already favorable to the one-vertex bound. -/
theorem exists_second_outside_cross_witness
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (S : Finset V) (hS : G.IsIndepSet (S : Set V))
    (y : V) (_hycross : ∃ r ∈ S, G.Adj y r)
    (hyattach : ∃ s ∈ S, Gᶜ.Adj y s) :
    ∃ z : V, z ∉ S ∧ z ≠ y ∧ ∃ s ∈ S, G.Adj z s := by
  obtain ⟨s, hs, hysC⟩ := hyattach
  obtain ⟨z, hsz⟩ := hG.preconnected.exists_adj_of_nontrivial s
  have hzout : z ∉ S := by
    intro hzS
    exact hS hs hzS hsz.ne hsz
  have hzy : z ≠ y := by
    intro hzy
    subst z
    rw [compl_adj] at hysC
    exact hysC.2 hsz.symm
  exact ⟨z, hzout, hzy, s, hs, hsz.symm⟩

end WrittenOnTheWallII.GraphConjecture100IncidenceEnergy
