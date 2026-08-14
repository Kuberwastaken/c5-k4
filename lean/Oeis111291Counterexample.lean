import FormalConjectures.OEIS.«111291»

/-!
# Counterexample to the formalized OEIS A111291 lower bound

The merged declaration quantifies over every real `x > 1`.  At `x = 3/2`,
the formal counting function is `1`, while `x / (2 * log x) > 1`.
-/

namespace OeisA111291

theorem countRefactorable_three_halves :
    countRefactorable (3 / 2 : ℝ) = 1 := by
  rw [countRefactorable]
  simp only [dif_pos (by norm_num : (3 / 2 : ℝ) ≥ 1)]
  norm_num [countRefactorableNat]
  native_decide

theorem one_lt_three_halves_div_two_log :
    (1 : ℝ) < (3 / 2 : ℝ) / (2 * Real.log (3 / 2 : ℝ)) := by
  have hlog_pos : 0 < Real.log (3 / 2 : ℝ) :=
    Real.log_pos (by norm_num)
  have hlog_lt : Real.log (3 / 2 : ℝ) < 1 / 2 := by
    have h := Real.log_lt_sub_one_of_pos
      (x := (3 / 2 : ℝ)) (by norm_num) (by norm_num)
    norm_num at h ⊢
    exact h
  rw [lt_div_iff₀ (mul_pos (by norm_num) hlog_pos)]
  nlinarith

theorem counterexample_at_three_halves :
    ¬(countRefactorable (3 / 2 : ℝ) : ℝ) ≥
      (3 / 2 : ℝ) / (2 * Real.log (3 / 2 : ℝ)) := by
  rw [countRefactorable_three_halves]
  exact not_le_of_gt (by simpa using one_lt_three_halves_div_two_log)

theorem formalized_conjecture_false :
    ¬∀ (x : ℝ), x > 1 →
      (countRefactorable x : ℝ) ≥ x / (2 * Real.log x) := by
  intro h
  exact counterexample_at_three_halves (h (3 / 2 : ℝ) (by norm_num))

end OeisA111291
