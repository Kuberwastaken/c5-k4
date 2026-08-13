import FormalConjecturesUtil

/-!
# WOWII 61: one-step residual-gap preservation

The remaining residual-gap condition reduces at one step to comparison of the
two degree-sum losses.  This file proves that an admissible positive-head
Havel--Hakimi step loses exactly twice its head, so weak first-prefix order
preserves the residual gap.
-/

namespace WrittenOnTheWallII.GraphConjecture61ResidualGap

open SimpleGraph

def stepLoss (s : List ℕ) : ℕ :=
  s.sum - (havelHakimiStep s).sum

/-- The exact local property supplied by a genuine graphical descending
degree list: the head fits in the tail and every decremented follower is
positive. -/
def StepAdmissible : List ℕ → Prop
  | [] => True
  | d :: rest => d ≤ rest.length ∧ ∀ x ∈ rest.take d, 0 < x

instance instDecidableStepAdmissible (s : List ℕ) : Decidable (StepAdmissible s) := by
  cases s <;> simp [StepAdmissible] <;> infer_instance

/-- Direct weak prefix dominance, including equal list lengths. -/
def DegreePrefixDominates (source target : List ℕ) : Prop :=
  source.length = target.length ∧
  ∀ k : ℕ, k ≤ source.length →
    (target.take k).sum ≤ (source.take k).sum

def ResidualGapPreserved (source target : List ℕ) : Prop :=
  target.sum + (havelHakimiStep source).sum ≤
    source.sum + (havelHakimiStep target).sum

instance instDecidableResidualGapPreserved (source target : List ℕ) :
    Decidable (ResidualGapPreserved source target) := by
  unfold ResidualGapPreserved
  infer_instance

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
      have htail := ih hxs
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

/-- An admissible Havel--Hakimi step loses exactly twice its head. -/
theorem stepLoss_eq_twice_head
    (d : ℕ) (rest : List ℕ) (h : StepAdmissible (d :: rest)) :
    stepLoss (d :: rest) = 2 * d := by
  have hsum := havelHakimiStep_sum_of_admissible d rest h
  have hdle : d ≤ rest.sum := by
    have hlen : (rest.take d).length = d := by simp [h.1]
    have hpos := h.2
    have htake : d ≤ (rest.take d).sum := by
      have hp := length_le_sum_of_pos hpos
      omega
    have hsplit := congrArg List.sum (List.take_append_drop d rest)
    rw [List.sum_append] at hsplit
    omega
  unfold stepLoss
  simp only [List.sum_cons]
  omega

theorem head_le_of_degreePrefixDominates
    {ds dt : ℕ} {rs rt : List ℕ}
    (h : DegreePrefixDominates (ds :: rs) (dt :: rt)) :
    dt ≤ ds := by
  have hp := h.2 1 (by simp)
  simpa using hp

/-- Strongest one-step result: weak degree-prefix order and local graphical
admissibility preserve the residual degree-sum gap. -/
theorem residualGapPreserved_oneStep
    {ds dt : ℕ} {rs rt : List ℕ}
    (hs : StepAdmissible (ds :: rs))
    (ht : StepAdmissible (dt :: rt))
    (hdom : DegreePrefixDominates (ds :: rs) (dt :: rt)) :
    ResidualGapPreserved (ds :: rs) (dt :: rt) := by
  have hhead := head_le_of_degreePrefixDominates hdom
  have hsLoss := stepLoss_eq_twice_head ds rs hs
  have htLoss := stepLoss_eq_twice_head dt rt ht
  have hsFormula := havelHakimiStep_sum_of_admissible ds rs hs
  have htFormula := havelHakimiStep_sum_of_admissible dt rt ht
  have hsStepLe : (havelHakimiStep (ds :: rs)).sum ≤ (ds :: rs).sum := by
    calc
      (havelHakimiStep (ds :: rs)).sum = rs.sum - ds := hsFormula
      _ ≤ rs.sum := Nat.sub_le _ _
      _ ≤ (ds :: rs).sum := by simp
  have htStepLe : (havelHakimiStep (dt :: rt)).sum ≤ (dt :: rt).sum := by
    calc
      (havelHakimiStep (dt :: rt)).sum = rt.sum - dt := htFormula
      _ ≤ rt.sum := Nat.sub_le _ _
      _ ≤ (dt :: rt).sum := by simp
  have hsEq : (ds :: rs).sum =
      (havelHakimiStep (ds :: rs)).sum + 2 * ds := by
    unfold stepLoss at hsLoss
    omega
  have htEq : (dt :: rt).sum =
      (havelHakimiStep (dt :: rt)).sum + 2 * dt := by
    unfold stepLoss at htLoss
    omega
  unfold ResidualGapPreserved
  omega

/-- Equivalently, target one-step excess is bounded by source one-step excess. -/
theorem first_excess_le
    {ds dt : ℕ} {rs rt : List ℕ}
    (hs : StepAdmissible (ds :: rs))
    (ht : StepAdmissible (dt :: rt))
    (hdom : DegreePrefixDominates (ds :: rs) (dt :: rt)) :
    stepLoss (dt :: rt) - 2 ≤ stepLoss (ds :: rs) - 2 := by
  rw [stepLoss_eq_twice_head dt rt ht, stepLoss_eq_twice_head ds rs hs]
  have := head_le_of_degreePrefixDominates hdom
  omega

/-- The first graphical transfer is an explicit non-equality instance. -/
theorem two_one_one_zero_to_matching_gap :
    StepAdmissible [2, 1, 1, 0] ∧
    StepAdmissible [1, 1, 1, 1] ∧
    DegreePrefixDominates [2, 1, 1, 0] [1, 1, 1, 1] ∧
    ResidualGapPreserved [2, 1, 1, 0] [1, 1, 1, 1] ∧
    stepLoss [2, 1, 1, 0] = 4 ∧
    stepLoss [1, 1, 1, 1] = 2 := by
  have hs : StepAdmissible [2, 1, 1, 0] := by decide
  have ht : StepAdmissible [1, 1, 1, 1] := by decide
  have hdom : DegreePrefixDominates [2, 1, 1, 0] [1, 1, 1, 1] := by
    constructor
    · decide
    · intro k hk
      norm_num at hk
      interval_cases k <;> norm_num
  refine ⟨hs, ht, hdom, residualGapPreserved_oneStep hs ht hdom, ?_, ?_⟩
  · simpa using stepLoss_eq_twice_head 2 [1, 1, 0] hs
  · simpa using stepLoss_eq_twice_head 1 [1, 1, 1] ht

end WrittenOnTheWallII.GraphConjecture61ResidualGap
