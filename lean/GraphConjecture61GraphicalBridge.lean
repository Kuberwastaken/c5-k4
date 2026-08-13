import FormalConjecturesUtil

/-!
# WOWII 61: admissibility bridge and successor obstruction

This file proves the local Havel--Hakimi admissibility bridge for a broad
explicit degree-sequence class and kernel-checks the first obstruction to
preserving weak prefix order after one canonical step.
-/

namespace WrittenOnTheWallII.GraphConjecture61GraphicalBridge

open SimpleGraph

def StepAdmissible : List ℕ → Prop
  | [] => True
  | d :: rest => d ≤ rest.length ∧ ∀ x ∈ rest.take d, 0 < x

instance instDecidableStepAdmissible (s : List ℕ) : Decidable (StepAdmissible s) := by
  cases s <;> simp [StepAdmissible] <;> infer_instance

def DegreePrefixDominates (source target : List ℕ) : Prop :=
  source.length = target.length ∧
  ∀ k : ℕ, k ≤ source.length →
    (target.take k).sum ≤ (source.take k).sum

/-- Every positive constant degree list has an admissible canonical step as
soon as its head degree fits in the remaining order.  This covers all positive
regular simple-graph degree sequences. -/
theorem stepAdmissible_replicate
    {d n : ℕ} (hd : 0 < d) (hfit : d ≤ n) :
    StepAdmissible (d :: List.replicate n d) := by
  constructor
  · simpa using hfit
  · intro x hx
    have : x = d := by
      have hx' : x ∈ List.replicate n d :=
        List.mem_of_mem_take hx
      simp only [List.mem_replicate] at hx'
      exact hx'.2
    simpa [this] using hd

/-- The all-zero terminal sequence is admissible. -/
theorem stepAdmissible_replicate_zero (n : ℕ) :
    StepAdmissible (List.replicate n 0) := by
  cases n with
  | zero => simp [StepAdmissible]
  | succ n => rw [List.replicate_succ]; simp [StepAdmissible]

/-- Complete graphs give a concrete regular graphical family covered by the
bridge: their degree list is `n` repeated `n+1` times. -/
theorem completeGraph_degree_shape_admissible (n : ℕ) (hn : 0 < n) :
    StepAdmissible (n :: List.replicate n n) :=
  stepAdmissible_replicate hn (le_refl n)

/-- Cycles of order at least three give another infinite realized regular
family: the degree list consists entirely of twos. -/
theorem cycle_degree_shape_admissible (n : ℕ) (hn : 2 ≤ n) :
    StepAdmissible (2 :: List.replicate n 2) :=
  stepAdmissible_replicate (by omega) hn

/-- The source and target of the first transfer are both locally admissible. -/
theorem first_transfer_admissible :
    StepAdmissible [2, 1, 1, 0] ∧ StepAdmissible [1, 1, 1, 1] := by
  decide

theorem first_transfer_degreePrefixDominates :
    DegreePrefixDominates [2, 1, 1, 0] [1, 1, 1, 1] := by
  constructor
  · decide
  · intro k hk
    norm_num at hk
    interval_cases k <;> norm_num

theorem length_le_sum_of_pos {a : List ℕ} (hpos : ∀ x ∈ a, 0 < x) :
    a.length ≤ a.sum := by
  induction a with
  | nil => simp
  | cons x xs ih =>
      have hx : 0 < x := hpos x (by simp)
      have hxs : ∀ y ∈ xs, 0 < y := by
        intro y hy
        exact hpos y (by simp [hy])
      simp only [List.length_cons, List.sum_cons]
      have := ih hxs
      omega

theorem map_pred_sum_eq_sub_length {a : List ℕ}
    (hpos : ∀ x ∈ a, 0 < x) :
    (a.map (· - 1)).sum = a.sum - a.length := by
  induction a with
  | nil => simp
  | cons x xs ih =>
      have hx : 0 < x := hpos x (by simp)
      have hxs : ∀ y ∈ xs, 0 < y := by
        intro y hy
        exact hpos y (by simp [hy])
      rw [List.map_cons, List.sum_cons, List.sum_cons, List.length_cons, ih hxs]
      have hsum := length_le_sum_of_pos hxs
      omega

theorem havelHakimiStep_sum_of_admissible
    (d : ℕ) (rest : List ℕ) (h : StepAdmissible (d :: rest)) :
    (havelHakimiStep (d :: rest)).sum = rest.sum - d := by
  let a := rest.take d
  let b := rest.drop d
  have hpos : ∀ x ∈ a, 0 < x := h.2
  have hlen : a.length = d := by simp [a, h.1]
  have hpred := map_pred_sum_eq_sub_length hpos
  have hperm :
      ((a.map (· - 1) ++ b).mergeSort (· ≥ ·)).sum =
        (a.map (· - 1) ++ b).sum :=
    (List.mergeSort_perm _ _).sum_eq
  rw [show havelHakimiStep (d :: rest) =
      (a.map (· - 1) ++ b).mergeSort (· ≥ ·) by
    simp [havelHakimiStep, a, b, List.splitAt_eq]]
  rw [hperm, List.sum_append, hpred, hlen]
  have hab : a.sum + b.sum = rest.sum := by
    rw [← List.sum_append]
    simp [a, b]
  have hdle : d ≤ a.sum := by
    have ha := length_le_sum_of_pos hpos
    omega
  omega

/-- Weak prefix order is not preserved after one canonical step: the target
successor has degree sum two while the source successor is all zero. -/
theorem first_successor_prefix_obstruction :
    DegreePrefixDominates [2, 1, 1, 0] [1, 1, 1, 1] ∧
    ¬ DegreePrefixDominates
      (havelHakimiStep [2, 1, 1, 0])
      (havelHakimiStep [1, 1, 1, 1]) := by
  refine ⟨first_transfer_degreePrefixDominates, ?_⟩
  intro h
  have hp := h.2 (havelHakimiStep [2, 1, 1, 0]).length (le_refl _)
  rw [List.take_length] at hp
  rw [h.1, List.take_length] at hp
  have hs := havelHakimiStep_sum_of_admissible 2 [1, 1, 0]
    first_transfer_admissible.1
  have ht := havelHakimiStep_sum_of_admissible 1 [1, 1, 1]
    first_transfer_admissible.2
  norm_num at hs ht
  omega

/-- Corrected one-step relation: retain initial prefix order and compare the
source and target successors only through the residual total-degree gap. -/
def ResidualCoupledStep (source target : List ℕ) : Prop :=
  DegreePrefixDominates source target ∧
  target.sum + (havelHakimiStep source).sum ≤
    source.sum + (havelHakimiStep target).sum

/-- The first obstruction to successor prefix order satisfies the corrected
residual coupling strictly. -/
theorem first_transfer_residualCoupledStep :
    ResidualCoupledStep [2, 1, 1, 0] [1, 1, 1, 1] := by
  refine ⟨first_transfer_degreePrefixDominates, ?_⟩
  rw [havelHakimiStep_sum_of_admissible 2 [1, 1, 0]
    first_transfer_admissible.1]
  rw [havelHakimiStep_sum_of_admissible 1 [1, 1, 1]
    first_transfer_admissible.2]
  norm_num

end WrittenOnTheWallII.GraphConjecture61GraphicalBridge
