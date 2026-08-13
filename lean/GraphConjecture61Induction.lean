import FormalConjecturesUtil

/-!
# WOWII 61: exact Havel--Hakimi trajectory accounting

This file iterates the one-step corrected-potential identity.  It also proves
that the accumulated loss credit is exactly the degree-sum lost along the
trajectory.  Consequently, carrying only this credit is an exact reformulation
of the desired potential comparison, not a stronger inductive invariant.
-/

namespace WrittenOnTheWallII.GraphConjecture61Induction

open SimpleGraph

def residuePotential (s : List ℕ) : ℕ :=
  2 * residueAux s + s.sum

def stepLoss (s : List ℕ) : ℕ :=
  s.sum - (havelHakimiStep s).sum

/-- Sum of the exact degree losses over the first `k` canonical steps. -/
def cumulativeStepLoss : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => stepLoss s + cumulativeStepLoss k (havelHakimiStep s)

/-- Every one of the first `k` lists has a positive head.  This records the
precise premise needed to unfold `residueAux` at every step. -/
def ActiveFor : ℕ → List ℕ → Prop
  | 0, _ => True
  | k + 1, s =>
      ∃ d rest, s = d :: rest ∧ d ≠ 0 ∧ ActiveFor k (havelHakimiStep s)

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

theorem residuePotential_cons_eq_step_add_loss
    (d : ℕ) (rest : List ℕ) (hd : d ≠ 0) :
    residuePotential (d :: rest) =
      residuePotential (havelHakimiStep (d :: rest)) + stepLoss (d :: rest) := by
  have hsum := havelHakimiStep_sum_le (d :: rest)
  unfold residuePotential stepLoss
  rw [residueAux.eq_3 d rest hd]
  omega

/-- Degree loss telescopes for every list, without graphicality or positivity
assumptions. -/
theorem sum_eq_iterate_add_cumulativeStepLoss (k : ℕ) (s : List ℕ) :
    s.sum = ((havelHakimiStep^[k]) s).sum + cumulativeStepLoss k s := by
  induction k generalizing s with
  | zero => simp [cumulativeStepLoss]
  | succ k ih =>
      have hle := havelHakimiStep_sum_le s
      have hrec := ih (havelHakimiStep s)
      rw [Function.iterate_succ_apply]
      simp only [cumulativeStepLoss, stepLoss]
      omega

/-- Thus accumulated credit has no hidden slack: it is exactly the initial
sum minus the current sum. -/
theorem cumulativeStepLoss_eq_sum_sub_iterate (k : ℕ) (s : List ℕ) :
    cumulativeStepLoss k s = s.sum - ((havelHakimiStep^[k]) s).sum := by
  have h := sum_eq_iterate_add_cumulativeStepLoss k s
  omega

/-- Iterating the one-step identity gives exact potential accounting along
every positive-head trajectory. -/
theorem residuePotential_eq_iterate_add_cumulativeStepLoss
    {k : ℕ} {s : List ℕ} (hactive : ActiveFor k s) :
    residuePotential s =
      residuePotential ((havelHakimiStep^[k]) s) + cumulativeStepLoss k s := by
  induction k generalizing s with
  | zero => simp [cumulativeStepLoss]
  | succ k ih =>
      obtain ⟨d, rest, hs, hd, htail⟩ := hactive
      subst s
      rw [residuePotential_cons_eq_step_add_loss d rest hd]
      have hrec := ih htail
      rw [Function.iterate_succ_apply]
      simp only [cumulativeStepLoss]
      omega

/-- The residue itself is invariant along a positive-head trajectory. -/
theorem residueAux_eq_iterate {k : ℕ} {s : List ℕ}
    (hactive : ActiveFor k s) :
    residueAux s = residueAux ((havelHakimiStep^[k]) s) := by
  have hpotential :=
    residuePotential_eq_iterate_add_cumulativeStepLoss hactive
  have hsum := sum_eq_iterate_add_cumulativeStepLoss k s
  unfold residuePotential at hpotential
  omega

/-- Full multi-step lift.  The endpoint potential together with accumulated
loss credit suffices for the initial potential comparison. -/
theorem residuePotential_le_of_trajectory_budget
    {ks kt : ℕ} {s t : List ℕ}
    (hs : ActiveFor ks s) (ht : ActiveFor kt t)
    (hbudget :
      residuePotential ((havelHakimiStep^[kt]) t) + cumulativeStepLoss kt t ≤
        residuePotential ((havelHakimiStep^[ks]) s) + cumulativeStepLoss ks s) :
    residuePotential t ≤ residuePotential s := by
  have htEq := residuePotential_eq_iterate_add_cumulativeStepLoss ht
  have hsEq := residuePotential_eq_iterate_add_cumulativeStepLoss hs
  calc
    residuePotential t =
        residuePotential ((havelHakimiStep^[kt]) t) + cumulativeStepLoss kt t := htEq
    _ ≤ residuePotential ((havelHakimiStep^[ks]) s) +
        cumulativeStepLoss ks s := hbudget
    _ = residuePotential s := hsEq.symm

/-- Exact boundary of the trajectory-credit method: under the positivity
premises, its terminal budget is equivalent to the original goal. -/
theorem trajectory_budget_iff_initial_potential
    {ks kt : ℕ} {s t : List ℕ}
    (hs : ActiveFor ks s) (ht : ActiveFor kt t) :
    (residuePotential ((havelHakimiStep^[kt]) t) + cumulativeStepLoss kt t ≤
        residuePotential ((havelHakimiStep^[ks]) s) + cumulativeStepLoss ks s) ↔
      residuePotential t ≤ residuePotential s := by
  constructor
  · exact residuePotential_le_of_trajectory_budget hs ht
  · intro h
    have htEq := residuePotential_eq_iterate_add_cumulativeStepLoss ht
    have hsEq := residuePotential_eq_iterate_add_cumulativeStepLoss hs
    calc
      residuePotential ((havelHakimiStep^[kt]) t) + cumulativeStepLoss kt t =
          residuePotential t := htEq.symm
      _ ≤ residuePotential s := h
      _ = residuePotential ((havelHakimiStep^[ks]) s) +
          cumulativeStepLoss ks s := hsEq

/-- A concrete two-step trajectory checks that the induction theorem is
nonvacuous and reaches the all-zero terminal list. -/
theorem pathThreeWithIsolated_oneStep_certificate :
    ActiveFor 1 [2, 1, 1, 0] ∧
    (havelHakimiStep^[1]) [2, 1, 1, 0] = [0, 0, 0] ∧
    cumulativeStepLoss 1 [2, 1, 1, 0] = 4 ∧
    residuePotential [2, 1, 1, 0] =
      residuePotential ((havelHakimiStep^[1]) [2, 1, 1, 0]) +
        cumulativeStepLoss 1 [2, 1, 1, 0] := by
  refine ⟨?_, ?_⟩
  · refine ⟨2, [1, 1, 0], rfl, by decide, ?_⟩
    trivial
  · native_decide

end WrittenOnTheWallII.GraphConjecture61Induction
