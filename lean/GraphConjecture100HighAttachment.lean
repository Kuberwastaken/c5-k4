import GraphConjecture100MiddleRange

/-!
# WOWII 100: two-outside-vertex high-attachment certificate

This file follows the exact upstream Lean expression `degreeL2Norm Gᶜ`, not
the complement-diameter reading in the upstream prose.
-/

namespace WrittenOnTheWallII.GraphConjecture100HighAttachment

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Exact aggregate lower bound suggested by two distinct outside vertices.
This predicate deliberately exposes the graph-theoretic energy obligation
instead of hiding it in an axiom. -/
def TwoOutsideEnergyCertificate
    (G : SimpleGraph V) [DecidableRel G.Adj] (a t u : ℕ) : Prop :=
  (((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u) + t ^ 2 + u ^ 2 : ℕ) : ℝ) ≤
    ∑ v, (Gᶜ.degree v : ℝ) ^ 2)

/-- Exact bounded optimization: the two-outside energy package crosses every
attachment pair for independence numbers 8 through 11. -/
set_option maxHeartbeats 1000000 in
lemma two_attachment_margin_eight_to_eleven
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

/-- A warning-clean exact structural slice.  Here `t,u` are the attachment
counts of two outside cross-edge witnesses; the two local hypotheses are the
nonattachment independent sets, and `henergy` is their aggregate complement
energy certificate. -/
theorem conjecture100_of_two_outside_energy_certificate
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (a t u : ℕ) (haG : G.indepNum = a)
    (ha : 8 ≤ a ∧ a ≤ 11) (ht : t + 1 ≤ a) (hu : u + 1 ≤ a)
    (hlocalT : a - t ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp))
    (hlocalU : a - u ≤
      (Finset.univ.image (indepNeighborsCard G)).max' (by simp))
    (henergy : TwoOutsideEnergyCertificate G a t u) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  have hmargin := two_attachment_margin_eight_to_eleven a t u ha ht hu
  have hleft : (0 : ℝ) ≤ 2 * (a : ℝ) - 4 + 2 * min t u := by
    have haR : (8 : ℝ) ≤ a := by exact_mod_cast ha.1
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

/-- Exact negative audit: the same two-witness package is insufficient at the
worst attachment pair for each independence value 4 through 7. -/
lemma two_attachment_package_not_uniform_four_to_seven :
    (∀ a : ℕ, a ∈ Finset.Icc 4 7 →
      let t := a - 1
      ¬ ((2 * (a : ℝ) - 4 + 2 * t) ^ 2 <
        ((a * (a - 1) ^ 2 + (2 * a - 1) * (t + t) + t ^ 2 + t ^ 2 : ℕ) : ℝ))) := by
  intro a ha
  simp only [mem_Icc] at ha
  have ha0 := ha.1
  have ha1 := ha.2
  interval_cases a <;> norm_num

end WrittenOnTheWallII.GraphConjecture100HighAttachment
