import FormalConjecturesUtil

/-!
# WOWII 61: recursive residual coupling without successor prefix order

This file carries only chronological one-step loss comparisons.  It never
requires weak prefix dominance between the successor lists.
-/

namespace WrittenOnTheWallII.GraphConjecture61ResidualCoupling

open SimpleGraph

def stepLoss (s : List ℕ) : ℕ :=
  s.sum - (havelHakimiStep s).sum

def cumulativeStepLoss : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => stepLoss s + cumulativeStepLoss k (havelHakimiStep s)

/-- The excess accumulated over `k` coupled active steps. -/
def cumulativeExcess (k : ℕ) (s : List ℕ) : ℕ :=
  cumulativeStepLoss k s - 2 * k

/-- Recursive coupled state.  At every chronological step the target loses no
more degree sum than the source.  No successor prefix relation is present. -/
def ResidualCouplingFor : ℕ → List ℕ → List ℕ → Prop
  | 0, _, _ => True
  | k + 1, source, target =>
      stepLoss target ≤ stepLoss source ∧
      ResidualCouplingFor k (havelHakimiStep source) (havelHakimiStep target)

theorem ResidualCouplingFor.tail {k : ℕ} {source target : List ℕ}
    (h : ResidualCouplingFor (k + 1) source target) :
    ResidualCouplingFor k (havelHakimiStep source) (havelHakimiStep target) :=
  h.2

/-- The recursive state orders total degree loss accumulated over every
coupled prefix. -/
theorem cumulativeStepLoss_le_of_residualCoupling
    {k : ℕ} {source target : List ℕ}
    (h : ResidualCouplingFor k source target) :
    cumulativeStepLoss k target ≤ cumulativeStepLoss k source := by
  induction k generalizing source target with
  | zero => simp [cumulativeStepLoss]
  | succ k ih =>
      simp only [ResidualCouplingFor, cumulativeStepLoss] at h ⊢
      exact Nat.add_le_add h.1 (ih h.2)

/-- Subtracting the identical `2k` baseline gives chronological excess order.
This is the exact profile-prefix conclusion while both trajectories are
coupled for `k` active steps. -/
theorem cumulativeExcess_le_of_residualCoupling
    {k : ℕ} {source target : List ℕ}
    (h : ResidualCouplingFor k source target) :
    cumulativeExcess k target ≤ cumulativeExcess k source := by
  unfold cumulativeExcess
  exact Nat.sub_le_sub_right (cumulativeStepLoss_le_of_residualCoupling h) _

theorem havelHakimiStep_sum_le (s : List ℕ) :
    (havelHakimiStep s).sum ≤ s.sum := by
  cases s with
  | nil => simp [havelHakimiStep]
  | cons d rest =>
      let a := rest.take d
      let b := rest.drop d
      have hdec : (a.map (· - 1)).sum ≤ a.sum := by
        induction a with
        | nil => simp
        | cons x xs ih =>
            simp only [List.map_cons, List.sum_cons]
            omega
      have hperm :
          ((a.map (· - 1) ++ b).mergeSort (· ≥ ·)).sum =
            (a.map (· - 1) ++ b).sum :=
        (List.mergeSort_perm _ _).sum_eq
      rw [show havelHakimiStep (d :: rest) =
          (a.map (· - 1) ++ b).mergeSort (· ≥ ·) by
        simp [havelHakimiStep, a, b, List.splitAt_eq]]
      rw [hperm, List.sum_append]
      calc
        (a.map (· - 1)).sum + b.sum ≤ a.sum + b.sum :=
          Nat.add_le_add_right hdec _
        _ = rest.sum := by
          rw [← List.sum_append]
          simp [a, b]
        _ ≤ d + rest.sum := Nat.le_add_left _ _

/-- One-step loss order is exactly the residual degree-sum gap inequality. -/
theorem stepLoss_le_iff_residualGap (source target : List ℕ) :
    stepLoss target ≤ stepLoss source ↔
      target.sum + (havelHakimiStep source).sum ≤
        source.sum + (havelHakimiStep target).sum := by
  have hs := havelHakimiStep_sum_le source
  have ht := havelHakimiStep_sum_le target
  unfold stepLoss
  omega

/-- Equivalent algebraic presentation of one recursive layer. -/
theorem residualCoupling_succ_iff
    (k : ℕ) (source target : List ℕ) :
    ResidualCouplingFor (k + 1) source target ↔
      (target.sum + (havelHakimiStep source).sum ≤
          source.sum + (havelHakimiStep target).sum) ∧
        ResidualCouplingFor k
          (havelHakimiStep source) (havelHakimiStep target) := by
  rw [ResidualCouplingFor, stepLoss_le_iff_residualGap]

/-- Complete telescoping identity for accumulated degree loss. -/
theorem sum_eq_iterate_add_cumulativeStepLoss (k : ℕ) (s : List ℕ) :
    s.sum = ((havelHakimiStep^[k]) s).sum + cumulativeStepLoss k s := by
  induction k generalizing s with
  | zero => simp [cumulativeStepLoss]
  | succ k ih =>
      have hstep := havelHakimiStep_sum_le s
      have hrec := ih (havelHakimiStep s)
      rw [Function.iterate_succ_apply]
      simp only [cumulativeStepLoss, stepLoss]
      omega

/-- Hence the recursive state orders every `k`-step total loss directly in
terms of the two residual graph-degree sums. -/
theorem iterate_residualGap_of_coupling
    {k : ℕ} {source target : List ℕ}
    (h : ResidualCouplingFor k source target) :
    target.sum + ((havelHakimiStep^[k]) source).sum ≤
      source.sum + ((havelHakimiStep^[k]) target).sum := by
  have hs := sum_eq_iterate_add_cumulativeStepLoss k source
  have ht := sum_eq_iterate_add_cumulativeStepLoss k target
  have hloss := cumulativeStepLoss_le_of_residualCoupling h
  omega

/-- Corrected recursive state: cumulative residual loss is compared at every
prefix.  Individual later losses may reverse, provided earlier source credit
budgets the reversal. -/
def CumulativeResidualCouplingFor (k : ℕ) (source target : List ℕ) : Prop :=
  ∀ j : ℕ, j ≤ k →
    cumulativeStepLoss j target ≤ cumulativeStepLoss j source

theorem cumulativeResidualCoupling_of_stepwise
    {k : ℕ} {source target : List ℕ}
    (h : ResidualCouplingFor k source target) :
    CumulativeResidualCouplingFor k source target := by
  intro j hj
  induction k generalizing j source target with
  | zero =>
      have : j = 0 := by omega
      subst j
      simp [cumulativeStepLoss]
  | succ k ih =>
      by_cases hj0 : j = 0
      · subst j
        simp [cumulativeStepLoss]
      · obtain ⟨i, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hj0
        simp only [ResidualCouplingFor, cumulativeStepLoss] at h ⊢
        exact Nat.add_le_add h.1 (ih h.2 i (by omega))

/-- The corrected state gives every desired chronological excess-prefix
comparison directly, while allowing pointwise loss reversals. -/
theorem cumulativeExcess_le_of_cumulativeResidualCoupling
    {k : ℕ} {source target : List ℕ}
    (h : CumulativeResidualCouplingFor k source target) :
    ∀ j : ℕ, j ≤ k → cumulativeExcess j target ≤ cumulativeExcess j source := by
  intro j hj
  unfold cumulativeExcess
  exact Nat.sub_le_sub_right (h j hj) _

/-- Equivalent iterate-sum presentation at every prefix. -/
theorem all_iterate_residualGaps_of_cumulativeCoupling
    {k : ℕ} {source target : List ℕ}
    (h : CumulativeResidualCouplingFor k source target) :
    ∀ j : ℕ, j ≤ k →
      target.sum + ((havelHakimiStep^[j]) source).sum ≤
        source.sum + ((havelHakimiStep^[j]) target).sum := by
  intro j hj
  have hs := sum_eq_iterate_add_cumulativeStepLoss j source
  have ht := sum_eq_iterate_add_cumulativeStepLoss j target
  have hloss := h j hj
  omega

end WrittenOnTheWallII.GraphConjecture61ResidualCoupling
