import FormalConjecturesUtil

/-!
# Conjecture 1.6 on the private-leaf cone

Write `a=q-1`, let `M` be the maximum positive private-leaf count, and let
`T` be the sum of all other counts.  The graph coordinates proved by the
separate private-leaf certificate are

`D=a+M`, `i=1+T`, and `n=a+1+M+T`.

This file proves the exact arithmetic consequence for every such coordinate
triple.  It does not construct the graph or reprove the independent-domination
formula; those remain the explicit graph-adapter boundary.
-/

namespace IndependentDominationPrivateLeafCone

/-- The even residual identity after substituting the private-leaf
coordinates. -/
theorem even_residual_identity (a M T : ℤ) :
    ((a + M) ^ 2 + 4) * (a + 1 + M + T) -
        (a + M + 2) ^ 2 * (1 + T) =
      (a + M) * ((a + M) ^ 2 - 4 * T) := by
  ring

/-- The odd residual identity after substituting the private-leaf
coordinates. -/
theorem odd_residual_identity (a M T : ℤ) :
    ((a + M) ^ 2 + 3) * (a + 1 + M + T) -
        (a + M + 1) * (a + M + 3) * (1 + T) =
      (a + M) * ((a + M) ^ 2 - 1 - 4 * T) := by
  ring

/-- The square gap proves the even bracket is nonnegative throughout the
whole positive-private-leaf cone. -/
theorem four_mul_tail_le_square (a M T : ℕ) (hT : T ≤ a * M) :
    4 * T ≤ (a + M) ^ 2 := by
  have hTz : (T : ℤ) ≤ (a : ℤ) * M := by exact_mod_cast hT
  have hz : (4 : ℤ) * T ≤ ((a : ℤ) + M) ^ 2 := by
    nlinarith [sq_nonneg ((a : ℤ) - M)]
  exact_mod_cast hz

/-- If `a+M` is odd, the square gap is at least one rather than merely
nonnegative. -/
theorem four_mul_tail_add_one_le_square_of_odd
    (a M T : ℕ) (hT : T ≤ a * M) (hOdd : Odd (a + M)) :
    4 * T + 1 ≤ (a + M) ^ 2 := by
  have hne : a ≠ M := by
    intro h
    obtain ⟨k, hk⟩ := hOdd
    subst M
    omega
  rcases lt_or_gt_of_ne hne with ham | hma
  · have hgap : (a : ℤ) + 1 ≤ M := by exact_mod_cast ham
    have hTz : (T : ℤ) ≤ (a : ℤ) * M := by exact_mod_cast hT
    have hz : (4 : ℤ) * T + 1 ≤ ((a : ℤ) + M) ^ 2 := by
      nlinarith [sq_nonneg ((a : ℤ) - M)]
    exact_mod_cast hz
  · have hgap : (M : ℤ) + 1 ≤ a := by exact_mod_cast hma
    have hTz : (T : ℤ) ≤ (a : ℤ) * M := by exact_mod_cast hT
    have hz : (4 : ℤ) * T + 1 ≤ ((a : ℤ) + M) ^ 2 := by
      nlinarith [sq_nonneg ((a : ℤ) - M)]
    exact_mod_cast hz

/-- Conjecture 1.6's even inequality holds for every private-leaf coordinate
vector. -/
theorem independentDominationEven_privateLeafCone
    (a M T : ℕ) (hT : T ≤ a * M) :
    (a + M + 2) ^ 2 * (1 + T) ≤
      ((a + M) ^ 2 + 4) * (a + 1 + M + T) := by
  have h := four_mul_tail_le_square a M T hT
  nlinarith

/-- Conjecture 1.6's odd inequality holds for every private-leaf coordinate
vector. -/
theorem independentDominationOdd_privateLeafCone
    (a M T : ℕ) (hT : T ≤ a * M) (hOdd : Odd (a + M)) :
    (a + M + 1) * (a + M + 3) * (1 + T) ≤
      ((a + M) ^ 2 + 3) * (a + 1 + M + T) := by
  have h := four_mul_tail_add_one_le_square_of_odd a M T hT hOdd
  nlinarith

#print axioms independentDominationEven_privateLeafCone
#print axioms independentDominationOdd_privateLeafCone

end IndependentDominationPrivateLeafCone
