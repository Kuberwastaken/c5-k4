import FormalConjecturesUtil

/-!
# Erdős 23: weighted `C5` blow-up quotient

This module extracts the two finite combinatorial facts behind the exact
bipartization formula for independent-set blow-ups of the five-cycle.

* A false-twin bag contributes linearly once all other cut assignments are
  fixed, so moving the whole bag to one side never decreases the cut.
* Among whole-bag two-colorings of `C5`, the least monochromatic interface
  weight is exactly the minimum of the five interface weights.

The statements are graph-API independent and can be reused as the quotient
kernel of a later nonuniform blow-up construction.
-/

namespace Erdos23.C5BlowupQuotient

/-- The minimum of five interface weights. -/
def minFive (w01 w12 w23 w34 w40 : ℕ) : ℕ :=
  min w01 (min w12 (min w23 (min w34 w40)))

/-- Weight deleted by a whole-bag two-coloring of the five-cycle: precisely
the interfaces whose endpoints receive the same color. -/
def monochromaticCost (w01 w12 w23 w34 w40 : ℕ)
    (c0 c1 c2 c3 c4 : Bool) : ℕ :=
  (if c0 = c1 then w01 else 0) +
  (if c1 = c2 then w12 else 0) +
  (if c2 = c3 then w23 else 0) +
  (if c3 = c4 then w34 else 0) +
  (if c4 = c0 then w40 else 0)

/-- Every two-coloring of an odd five-cycle has a monochromatic adjacent
interface, quantitatively: its deleted weight is at least the lightest
interface. -/
theorem minFive_le_monochromaticCost
    (w01 w12 w23 w34 w40 : ℕ) (c0 c1 c2 c3 c4 : Bool) :
    minFive w01 w12 w23 w34 w40 ≤
      monochromaticCost w01 w12 w23 w34 w40 c0 c1 c2 c3 c4 := by
  have h01 : minFive w01 w12 w23 w34 w40 ≤ w01 :=
    min_le_left _ _
  have h12 : minFive w01 w12 w23 w34 w40 ≤ w12 :=
    le_trans (min_le_right _ _) (min_le_left _ _)
  have h23 : minFive w01 w12 w23 w34 w40 ≤ w23 :=
    le_trans (min_le_right _ _)
      (le_trans (min_le_right _ _) (min_le_left _ _))
  have h34 : minFive w01 w12 w23 w34 w40 ≤ w34 :=
    le_trans (min_le_right _ _)
      (le_trans (min_le_right _ _)
        (le_trans (min_le_right _ _) (min_le_left _ _)))
  have h40 : minFive w01 w12 w23 w34 w40 ≤ w40 :=
    le_trans (min_le_right _ _)
      (le_trans (min_le_right _ _)
        (le_trans (min_le_right _ _) (min_le_right _ _)))
  cases c0 <;> cases c1 <;> cases c2 <;> cases c3 <;> cases c4 <;>
    simp [monochromaticCost] <;> omega

/-- Each chosen interface can be made the unique monochromatic interface.
These five explicit quotient colorings give the deletion upper certificates. -/
theorem each_interface_is_unique_monochromatic
    (w01 w12 w23 w34 w40 : ℕ) :
    monochromaticCost w01 w12 w23 w34 w40 false false true false true = w01 ∧
    monochromaticCost w01 w12 w23 w34 w40 true false false true false = w12 ∧
    monochromaticCost w01 w12 w23 w34 w40 false true false false true = w23 ∧
    monochromaticCost w01 w12 w23 w34 w40 true false true false false = w34 ∧
    monochromaticCost w01 w12 w23 w34 w40 false true false true false = w40 := by
  simp [monochromaticCost]

/-- The lightest interface is attained by a whole-bag coloring. -/
theorem exists_coloring_monochromaticCost_eq_minFive
    (w01 w12 w23 w34 w40 : ℕ) :
    ∃ c0 c1 c2 c3 c4 : Bool,
      monochromaticCost w01 w12 w23 w34 w40 c0 c1 c2 c3 c4 =
        minFive w01 w12 w23 w34 w40 := by
  have hcert := each_interface_is_unique_monochromatic
    w01 w12 w23 w34 w40
  rcases min_choice w01 (min w12 (min w23 (min w34 w40))) with h01 | hrest
  · exact ⟨false, false, true, false, true, hcert.1.trans h01.symm⟩
  · rcases min_choice w12 (min w23 (min w34 w40)) with h12 | hrest'
    · refine ⟨true, false, false, true, false, ?_⟩
      calc
        _ = w12 := hcert.2.1
        _ = min w12 (min w23 (min w34 w40)) := h12.symm
        _ = min w01 (min w12 (min w23 (min w34 w40))) := hrest.symm
        _ = minFive w01 w12 w23 w34 w40 := rfl
    · rcases min_choice w23 (min w34 w40) with h23 | hrest''
      · refine ⟨false, true, false, false, true, ?_⟩
        calc
          _ = w23 := hcert.2.2.1
          _ = min w23 (min w34 w40) := h23.symm
          _ = min w12 (min w23 (min w34 w40)) := hrest'.symm
          _ = min w01 (min w12 (min w23 (min w34 w40))) := hrest.symm
          _ = minFive w01 w12 w23 w34 w40 := rfl
      · rcases min_choice w34 w40 with h34 | h40
        · refine ⟨true, false, true, false, false, ?_⟩
          calc
            _ = w34 := hcert.2.2.2.1
            _ = min w34 w40 := h34.symm
            _ = min w23 (min w34 w40) := hrest''.symm
            _ = min w12 (min w23 (min w34 w40)) := hrest'.symm
            _ = min w01 (min w12 (min w23 (min w34 w40))) := hrest.symm
            _ = minFive w01 w12 w23 w34 w40 := rfl
        · refine ⟨false, true, false, true, false, ?_⟩
          calc
            _ = w40 := hcert.2.2.2.2
            _ = min w34 w40 := h40.symm
            _ = min w23 (min w34 w40) := hrest''.symm
            _ = min w12 (min w23 (min w34 w40)) := hrest'.symm
            _ = min w01 (min w12 (min w23 (min w34 w40))) := hrest.symm
            _ = minFive w01 w12 w23 w34 w40 := rfl

/-- Exact weighted odd-cycle quotient identity: the optimum number of deleted
interface edges is the lightest interface weight. -/
theorem weighted_c5_exact
    (w01 w12 w23 w34 w40 : ℕ) :
    (∀ c0 c1 c2 c3 c4 : Bool,
      minFive w01 w12 w23 w34 w40 ≤
        monochromaticCost w01 w12 w23 w34 w40 c0 c1 c2 c3 c4) ∧
    (∃ c0 c1 c2 c3 c4 : Bool,
      monochromaticCost w01 w12 w23 w34 w40 c0 c1 c2 c3 c4 =
        minFive w01 w12 w23 w34 w40) := by
  exact ⟨minFive_le_monochromaticCost w01 w12 w23 w34 w40,
    exists_coloring_monochromaticCost_eq_minFive w01 w12 w23 w34 w40⟩

/-- For a false-twin bag of order `n`, let `x` vertices lie on one cut side.
If the already-fixed neighboring vertices contribute aggregate weights `r`
and `l` to the two choices, then one of the two whole-bag placements has at
least the contribution of the split placement.  This is the exact local
rounding step used to normalize an optimal cut bag by bag. -/
theorem split_bag_contribution_le_whole_bag
    (n x l r : ℕ) (hx : x ≤ n) :
    x * r + (n - x) * l ≤ max (n * r) (n * l) := by
  rcases le_total l r with hlr | hrl
  · rw [max_eq_left (Nat.mul_le_mul_left n hlr)]
    calc
      x * r + (n - x) * l ≤ x * r + (n - x) * r := by
        exact Nat.add_le_add_left (Nat.mul_le_mul_left (n - x) hlr) _
      _ = n * r := by
        rw [← Nat.add_mul, Nat.add_comm, Nat.sub_add_cancel hx]
  · rw [max_eq_right (Nat.mul_le_mul_left n hrl)]
    calc
      x * r + (n - x) * l ≤ x * l + (n - x) * l := by
        exact Nat.add_le_add_right (Nat.mul_le_mul_left x hrl) _
      _ = n * l := by
        rw [← Nat.add_mul, Nat.add_comm, Nat.sub_add_cancel hx]

/-- Product-weight specialization for a nonuniform independent-set blow-up of
`C5`: after whole-bag normalization, the exact quotient deletion cost is the
minimum adjacent bag product. -/
theorem product_weight_c5_exact (a0 a1 a2 a3 a4 : ℕ) :
    (∀ c0 c1 c2 c3 c4 : Bool,
      minFive (a0 * a1) (a1 * a2) (a2 * a3) (a3 * a4) (a4 * a0) ≤
        monochromaticCost (a0 * a1) (a1 * a2) (a2 * a3) (a3 * a4) (a4 * a0)
          c0 c1 c2 c3 c4) ∧
    (∃ c0 c1 c2 c3 c4 : Bool,
      monochromaticCost (a0 * a1) (a1 * a2) (a2 * a3) (a3 * a4) (a4 * a0)
          c0 c1 c2 c3 c4 =
        minFive (a0 * a1) (a1 * a2) (a2 * a3) (a3 * a4) (a4 * a0)) := by
  exact weighted_c5_exact (a0 * a1) (a1 * a2) (a2 * a3) (a3 * a4) (a4 * a0)

end Erdos23.C5BlowupQuotient
