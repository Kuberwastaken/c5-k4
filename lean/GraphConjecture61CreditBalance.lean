import FormalConjecturesUtil

/-!
# WOWII 61: explicit credit-balance recursion

The source banks earlier excess degree loss as natural-number credit.  A later
target loss may exceed the simultaneous source loss exactly when the banked
credit covers the difference.
-/

namespace WrittenOnTheWallII.GraphConjecture61CreditBalance

open SimpleGraph

def stepLoss (s : List ℕ) : ℕ :=
  s.sum - (havelHakimiStep s).sum

def cumulativeStepLoss : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => stepLoss s + cumulativeStepLoss k (havelHakimiStep s)

/-- Banked source advantage after `k` canonical steps. -/
def creditBalance (k : ℕ) (source target : List ℕ) : ℕ :=
  cumulativeStepLoss k source - cumulativeStepLoss k target

/-- Cumulative residual coupling, restated as credit solvency at every time. -/
def CreditSolventFor (k : ℕ) (source target : List ℕ) : Prop :=
  ∀ j : ℕ, j ≤ k →
    cumulativeStepLoss j target ≤ cumulativeStepLoss j source

/-- The local rule: the next target loss may use both the simultaneous source
loss and all credit banked before this step. -/
def LocalCreditRuleFor (k : ℕ) (source target : List ℕ) : Prop :=
  ∀ j : ℕ, j < k →
    stepLoss ((havelHakimiStep^[j]) target) ≤
      creditBalance j source target +
        stepLoss ((havelHakimiStep^[j]) source)

theorem cumulativeStepLoss_succ (k : ℕ) (s : List ℕ) :
    cumulativeStepLoss (k + 1) s =
      cumulativeStepLoss k s + stepLoss ((havelHakimiStep^[k]) s) := by
  induction k generalizing s with
  | zero => simp [cumulativeStepLoss]
  | succ k ih =>
      change stepLoss s + cumulativeStepLoss (k + 1) (havelHakimiStep s) =
        stepLoss s + cumulativeStepLoss k (havelHakimiStep s) +
          stepLoss ((havelHakimiStep^[k + 1]) s)
      rw [ih (havelHakimiStep s)]
      rw [Function.iterate_succ_apply]
      omega

/-- Under current solvency, the natural credit is the exact integer-free
difference between cumulative source and target losses. -/
theorem creditBalance_add_target_eq_source
    {k : ℕ} {source target : List ℕ}
    (h : cumulativeStepLoss k target ≤ cumulativeStepLoss k source) :
    creditBalance k source target + cumulativeStepLoss k target =
      cumulativeStepLoss k source := by
  unfold creditBalance
  omega

/-- Exact local update equation.  The budget premise is precisely what makes
natural subtraction nontruncating. -/
theorem creditBalance_succ
    {k : ℕ} {source target : List ℕ}
    (hsolvent : cumulativeStepLoss k target ≤ cumulativeStepLoss k source) :
    creditBalance (k + 1) source target =
      creditBalance k source target +
        stepLoss ((havelHakimiStep^[k]) source) -
          stepLoss ((havelHakimiStep^[k]) target) := by
  rw [creditBalance, cumulativeStepLoss_succ, cumulativeStepLoss_succ]
  have hcredit := creditBalance_add_target_eq_source hsolvent
  unfold creditBalance at hcredit ⊢
  omega

/-- One locally budgeted step extends cumulative solvency. -/
theorem solvent_succ_of_localBudget
    {k : ℕ} {source target : List ℕ}
    (hsolvent : CreditSolventFor k source target)
    (hbudget : stepLoss ((havelHakimiStep^[k]) target) ≤
      creditBalance k source target +
        stepLoss ((havelHakimiStep^[k]) source)) :
    CreditSolventFor (k + 1) source target := by
  intro j hj
  by_cases hle : j ≤ k
  · exact hsolvent j hle
  · have hjEq : j = k + 1 := by omega
    subst j
    rw [cumulativeStepLoss_succ, cumulativeStepLoss_succ]
    have hk := hsolvent k (le_refl _)
    have hcredit := creditBalance_add_target_eq_source hk
    omega

/-- Every solvent cumulative coupling supplies the local credit rule. -/
theorem localCreditRule_of_solvent
    {k : ℕ} {source target : List ℕ}
    (h : CreditSolventFor k source target) :
    LocalCreditRuleFor k source target := by
  intro j hj
  have hjSolvent := h j (by omega)
  have hsucc := h (j + 1) (by omega)
  rw [cumulativeStepLoss_succ, cumulativeStepLoss_succ] at hsucc
  have hcredit := creditBalance_add_target_eq_source hjSolvent
  omega

/-- Conversely, the local banked-credit rule implies solvency at every prefix. -/
theorem solvent_of_localCreditRule
    {k : ℕ} {source target : List ℕ}
    (h : LocalCreditRuleFor k source target) :
    CreditSolventFor k source target := by
  intro j hj
  induction j with
  | zero => simp [cumulativeStepLoss]
  | succ j ih =>
      have hjlt : j < k := by omega
      have hbudget := h j hjlt
      have hcredit := creditBalance_add_target_eq_source (ih (by omega))
      rw [cumulativeStepLoss_succ, cumulativeStepLoss_succ]
      omega

/-- Exact equivalence: cumulative residual coupling is precisely local
solvency of the explicit credit recursion. -/
theorem localCreditRule_iff_solvent
    (k : ℕ) (source target : List ℕ) :
    LocalCreditRuleFor k source target ↔ CreditSolventFor k source target := by
  constructor
  · exact solvent_of_localCreditRule
  · exact localCreditRule_of_solvent

/-- Strongest preserved class: any pair satisfying the local credit budget
through `k` steps has ordered cumulative excess after subtracting `2k`. -/
theorem cumulativeExcess_le_of_localCreditRule
    {k : ℕ} {source target : List ℕ}
    (h : LocalCreditRuleFor k source target) :
    cumulativeStepLoss k target - 2 * k ≤
      cumulativeStepLoss k source - 2 * k := by
  have hs := solvent_of_localCreditRule h
  exact Nat.sub_le_sub_right (hs k (le_refl _)) _

end WrittenOnTheWallII.GraphConjecture61CreditBalance
