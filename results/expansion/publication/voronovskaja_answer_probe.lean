import FormalConjecturesUtil
/-! # Probe: `bezier_bernstein_operators` forces its closed answer to `0`
Definitions copied verbatim from upstream `main` @ 638da20e. -/

open Topology Filter Real unitInterval Polynomial
namespace VoronovskajaTypeFormula

noncomputable def bernsteinTail (n k : ℕ) : Polynomial ℝ :=
  ∑ j ∈ Finset.Icc k n, bernsteinPolynomial ℝ n j

noncomputable def bezierBernstein (n : ℕ) (α : ℝ) (f : ℝ → ℝ) (x : ℝ) : ℝ :=
  ∑ k ∈ Finset.range (n + 1),
    f (k / n) * ((bernsteinTail n k).eval x ^ α - (bernsteinTail n (k + 1)).eval x ^ α)

/-- `J_{n,0} = 1`. -/
theorem bernsteinTail_zero (n : ℕ) : bernsteinTail n 0 = 1 := by
  rw [bernsteinTail, ← Nat.range_succ_eq_Icc_zero]
  exact bernsteinPolynomial.sum ℝ n

/-- `J_{n,n+1} = 0`. -/
theorem bernsteinTail_succ_self (n : ℕ) : bernsteinTail n (n + 1) = 0 := by
  simp [bernsteinTail]

/-- The operator reproduces constants (for `α ≠ 0`): the weights telescope to `1`. -/
theorem bezierBernstein_const (n : ℕ) (α c x : ℝ) (hα : α ≠ 0) :
    bezierBernstein n α (fun _ ↦ c) x = c := by
  rw [bezierBernstein, ← Finset.mul_sum, Finset.sum_range_sub']
  rw [bernsteinTail_zero, bernsteinTail_succ_self]
  simp [hα]

/-- Hence any closed `L : ℝ` satisfying the upstream statement for all admissible
`α`, `f`, `x` is forced to be `0`. -/
theorem answer_forced_zero (L : ℝ)
    (h : ∀ (α : ℝ), 0 < α → α ≠ 1 → ∀ (f : ℝ → ℝ) (x : ℝ), x ∈ I → ContDiffOn ℝ 2 f I →
      Tendsto (fun n : ℕ => Real.sqrt n * (bezierBernstein n α f x - f x)) atTop (𝓝 L)) :
    L = 0 := by
  have hx : (0 : ℝ) ∈ I := ⟨le_refl 0, zero_le_one⟩
  have hf : ContDiffOn ℝ 2 (fun _ : ℝ ↦ (0 : ℝ)) I := contDiffOn_const
  have key := h 2 two_pos (by norm_num) (fun _ ↦ (0 : ℝ)) 0 hx hf
  have hzero : (fun n : ℕ => Real.sqrt n * (bezierBernstein n 2 (fun _ : ℝ ↦ (0 : ℝ)) 0 - 0))
      = fun _ : ℕ => (0 : ℝ) := by
    funext n
    rw [bezierBernstein_const n 2 0 0 two_ne_zero]
    ring
  rw [hzero] at key
  exact (tendsto_nhds_unique tendsto_const_nhds key).symm

end VoronovskajaTypeFormula
