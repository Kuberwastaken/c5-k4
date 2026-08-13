import GraphConjecture100IncidenceEnergy

/-!
# WOWII 100: three-witness aggregate certificate

This file follows the exact upstream Lean expression `degreeL2Norm Gᶜ`, not
the complement-diameter reading in the upstream prose.
-/

namespace WrittenOnTheWallII.GraphConjecture100ThreeWitness

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The exact energy lower bound contributed by an independent `a`-set and
three distinct outside witnesses with attachment counts `t,u,v`. -/
def ThreeOutsideEnergyCertificate
    (G : SimpleGraph V) [DecidableRel G.Adj] (a t u v : ℕ) : Prop :=
  (((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u + v) +
    t ^ 2 + u ^ 2 + v ^ 2 : ℕ) : ℝ) ≤
      ∑ x, (Gᶜ.degree x : ℝ) ^ 2)

/-- Exact optimization of the three-witness package throughout the remaining
independence range.  The proof reduces all three counts to their minimum and
then checks only the 22 admissible `(a,m)` integer pairs. -/
lemma three_attachment_margin_four_to_seven
    (a t u v : ℕ) (ha : 4 ≤ a ∧ a ≤ 7)
    (ht : t + 1 ≤ a) (hu : u + 1 ≤ a) (hv : v + 1 ≤ a) :
    (2 * (a : ℝ) - 4 + 2 * min t (min u v)) ^ 2 <
      ((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u + v) +
        t ^ 2 + u ^ 2 + v ^ 2 : ℕ) : ℝ) := by
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
  have ha0 := ha.1
  have ha1 := ha.2
  have hmBound : m ≤ 6 := by omega
  have hmA : m + 1 ≤ a := by omega
  have hreduced :
      (2 * (a : ℝ) - 4 + 2 * m) ^ 2 <
        ((a * (a - 1) ^ 2 + (2 * a - 1) * (3 * m) + 3 * m ^ 2 : ℕ) : ℝ) := by
    interval_cases a <;> interval_cases m <;> norm_num at *
  have hsum : (3 : ℝ) * m ≤ t + u + v := by linarith
  have hmono :
      ((a * (a - 1) ^ 2 + (2 * a - 1) * (3 * m) + 3 * m ^ 2 : ℕ) : ℝ) ≤
        ((a * (a - 1) ^ 2 + (2 * a - 1) * (t + u + v) +
          t ^ 2 + u ^ 2 + v ^ 2 : ℕ) : ℝ) := by
    interval_cases a <;> norm_num at htSq huSq hvSq hsum ⊢ <;> nlinarith
  exact hreduced.trans_le hmono

/-- The exact upstream conclusion follows from the three local nonattachment
bounds and the aggregate energy certificate. -/
theorem conjecture100_of_three_outside_energy_certificate
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (a t u v : ℕ) (haG : G.indepNum = a)
    (ha : 4 ≤ a ∧ a ≤ 7)
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
  have hmargin := three_attachment_margin_four_to_seven a t u v ha ht hu hv
  have hleft : (0 : ℝ) ≤ 2 * (a : ℝ) - 4 + 2 * m := by
    have haR : (4 : ℝ) ≤ a := by exact_mod_cast ha.1
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
    · rw [show m = t by simp [m, htu]]
      exact hlocalT
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

/-- Exact residual audit at a worst coordinate in each row.  At `a=4` the
worst point is the zero coordinate; at `a=5,6,7` it is the upper corner. -/
lemma worst_three_witness_margins :
    let margin (a t : ℕ) :=
      ((a * (a - 1) ^ 2 + (2 * a - 1) * (3 * t) + 3 * t ^ 2 : ℕ) : ℤ) -
        (2 * (a : ℤ) - 4 + 2 * t) ^ 2
    margin 4 0 = 20 ∧ margin 5 4 = 40 ∧
      margin 6 5 = 66 ∧ margin 7 6 = 110 := by
  norm_num

end WrittenOnTheWallII.GraphConjecture100ThreeWitness
