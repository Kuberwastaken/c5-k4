import FormalConjecturesUtil

/-!
# WOWII 100: complement-energy extraction

The upstream theorem is stated using `degreeL2Norm Gᶜ`, despite its module
prose discussing the diameter of the complement.  This file works with the
Lean expression exactly as written.

An independent set of size `a` in `G` is a clique of size `a` in `Gᶜ`.
Consequently every one of those vertices has complement degree at least
`a - 1`, and the squared-degree sum of `Gᶜ` is at least
`a * (a - 1)^2`.  This closes Conjecture 100 whenever `a ≥ 17`, without
using the upstream `sorry`, and leaves an exact ceiling-residual criterion
for the remaining finite range.
-/

namespace WrittenOnTheWallII.GraphConjecture100Extraction

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Every vertex of an independent set has at least all the other vertices
of that set as neighbors in the complement. -/
lemma card_sub_one_le_compl_degree_of_indep
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (hS : G.IsIndepSet (S : Set V))
    (v : V) (hv : v ∈ S) :
    S.card - 1 ≤ Gᶜ.degree v := by
  have hsub : S.erase v ⊆ Gᶜ.neighborFinset v := by
    intro w hw
    have hwS : w ∈ S := (mem_erase.mp hw).2
    have hwv : w ≠ v := (mem_erase.mp hw).1
    rw [mem_neighborFinset, compl_adj]
    exact ⟨hwv.symm, fun hAdj ↦ hS hwS hv hwv hAdj.symm⟩
  have hcard := card_le_card hsub
  rw [card_erase_of_mem hv] at hcard
  exact hcard

/-- An explicit independent set forces a lower bound on the squared-degree
energy of the complement. -/
theorem independent_set_compl_degree_energy
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (hS : G.IsIndepSet (S : Set V)) :
    (S.card : ℝ) * ((S.card : ℝ) - 1) ^ 2 ≤
      ∑ v, (Gᶜ.degree v : ℝ) ^ 2 := by
  calc
    (S.card : ℝ) * ((S.card : ℝ) - 1) ^ 2 =
        ∑ _v ∈ S, ((S.card : ℝ) - 1) ^ 2 := by simp
    _ ≤ ∑ v ∈ S, (Gᶜ.degree v : ℝ) ^ 2 := by
      apply sum_le_sum
      intro v hv
      have hnat := card_sub_one_le_compl_degree_of_indep G S hS v hv
      have hreal : ((S.card - 1 : ℕ) : ℝ) ≤ (Gᶜ.degree v : ℝ) := by
        exact_mod_cast hnat
      have hcard : 1 ≤ S.card := by
        exact (Finset.one_le_card.mpr ⟨v, hv⟩)
      rw [Nat.cast_sub hcard] at hreal
      have hcardR : (1 : ℝ) ≤ S.card := by exact_mod_cast hcard
      have hleft : (0 : ℝ) ≤ (S.card : ℝ) - 1 := by linarith
      have hright : (0 : ℝ) ≤ Gᶜ.degree v := Nat.cast_nonneg _
      norm_num at hreal
      have hreal' : (S.card : ℝ) - 1 ≤ (Gᶜ.degree v : ℝ) := by
        linarith
      exact (sq_le_sq₀ hleft hright).2 hreal'
    _ ≤ ∑ v, (Gᶜ.degree v : ℝ) ^ 2 := by
      exact sum_le_sum_of_subset_of_nonneg (subset_univ S)
        (fun _ _ _ ↦ sq_nonneg _)

/-- The complement degree norm is bounded below by the energy contributed by
a maximum independent set. -/
theorem sqrt_indep_energy_le_degreeL2Norm_compl
    (G : SimpleGraph V) [DecidableRel G.Adj] :
    Real.sqrt
        ((G.indepNum : ℝ) * ((G.indepNum : ℝ) - 1) ^ 2) ≤
      degreeL2Norm Gᶜ := by
  obtain ⟨S, hS⟩ := G.exists_isNIndepSet_indepNum
  have henergy := independent_set_compl_degree_energy G S hS.isIndepSet
  rw [hS.card_eq] at henergy
  unfold degreeL2Norm
  exact Real.sqrt_le_sqrt henergy

/-- Exact arithmetic reduction of the upstream ceiling inequality.  Since
the left side is an integer, Conjecture 100 is equivalent to a strict
residual inequality one unit below the target. -/
theorem conjecture100_iff_residual
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nonempty V] :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max'
      (by simp)
    ((G.indepNum : ℝ) ≤
        ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉) ↔
      4 * ((G.indepNum : ℝ) - 1) <
        2 * (maxL : ℝ) + degreeL2Norm Gᶜ := by
  dsimp
  rw [show ((G.indepNum : ℝ) ≤
      (⌈(((Finset.univ.image (indepNeighborsCard G)).max'
          (by simp) : ℝ) +
          (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ : ℝ)) ↔
      ((G.indepNum : ℤ) ≤
        ⌈(((Finset.univ.image (indepNeighborsCard G)).max'
          (by simp) : ℝ) +
          (1 / 2) * degreeL2Norm Gᶜ) / 2⌉) by norm_cast]
  rw [Int.le_ceil_iff]
  norm_num
  constructor <;> intro h <;> linarith

/-- The exact upstream-shaped conclusion follows from the strict residual
bound. -/
theorem conjecture100_of_residual
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nonempty V]
    (hres :
      let maxL := (Finset.univ.image (indepNeighborsCard G)).max'
        (by simp)
      4 * ((G.indepNum : ℝ) - 1) <
        2 * (maxL : ℝ) + degreeL2Norm Gᶜ) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max'
      (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  exact (conjecture100_iff_residual G).2 hres

omit [Fintype V] [DecidableEq V] in
/-- The complement-energy term alone beats the strict residual once the
independence number is at least 17. -/
lemma four_mul_indep_sub_one_lt_sqrt_energy
    (G : SimpleGraph V) (h17 : 17 ≤ G.indepNum) :
    4 * ((G.indepNum : ℝ) - 1) <
      Real.sqrt
        ((G.indepNum : ℝ) * ((G.indepNum : ℝ) - 1) ^ 2) := by
  have ha : (16 : ℝ) < G.indepNum := by exact_mod_cast (by omega : 16 < G.indepNum)
  have hx : (0 : ℝ) < (G.indepNum : ℝ) - 1 := by linarith
  apply (Real.lt_sqrt (mul_nonneg (by norm_num) hx.le)).2
  nlinarith [sq_pos_of_pos hx]

/-- A substantial unconditional specialization of the formalized WOWII 100:
every finite graph with independence number at least 17 satisfies the exact
upstream inequality.  Connectivity assumptions are unnecessary in this
regime. -/
theorem conjecture100_of_indepNum_ge_seventeen
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nonempty V]
    (h17 : 17 ≤ G.indepNum) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max'
      (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  apply conjecture100_of_residual G
  dsimp
  have hstrict := four_mul_indep_sub_one_lt_sqrt_energy G h17
  have hnorm := sqrt_indep_energy_le_degreeL2Norm_compl G
  have hmax : (0 : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max'
        (by simp) : ℝ) := by
    positivity
  linarith

end WrittenOnTheWallII.GraphConjecture100Extraction
