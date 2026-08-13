import FormalConjecturesUtil

/-!
# WOWII 61: partial excess-loss identity

This file identifies the exact residual degree-sum gap needed to transfer weak
degree-prefix order into chronological excess-profile order.
-/

namespace WrittenOnTheWallII.GraphConjecture61PaddedProfile

open SimpleGraph

def stepLoss (s : List ℕ) : ℕ :=
  s.sum - (havelHakimiStep s).sum

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

theorem havelHakimiIterate_sum_le (k : ℕ) (s : List ℕ) :
    ((havelHakimiStep^[k]) s).sum ≤ s.sum := by
  induction k generalizing s with
  | zero => simp
  | succ k ih =>
      rw [Function.iterate_succ_apply]
      exact (ih (havelHakimiStep s)).trans (havelHakimiStep_sum_le s)

inductive ExcessTrajectory : List ℕ → List ℕ → Prop
  | zeros (z : ℕ) : ExcessTrajectory (List.replicate z 0) []
  | step (d : ℕ) (rest profile : List ℕ) (hd : d ≠ 0)
      (htwo : 2 ≤ stepLoss (d :: rest))
      (htail : ExcessTrajectory (havelHakimiStep (d :: rest)) profile) :
      ExcessTrajectory (d :: rest) ((stepLoss (d :: rest) - 2) :: profile)

/-- Exact partial-profile identity.  The first `k` profile entries plus the
baseline `2k` are precisely the degree sum lost in the first `k` canonical
Havel--Hakimi steps. -/
theorem ExcessTrajectory.take_sum_add_two_mul
    {s profile : List ℕ} (h : ExcessTrajectory s profile)
    {k : ℕ} (hk : k ≤ profile.length) :
    (profile.take k).sum + 2 * k =
      s.sum - ((havelHakimiStep^[k]) s).sum := by
  induction h generalizing k with
  | zeros z =>
      have hk0 : k = 0 := by simpa using hk
      subst k
      simp
  | step d rest profile hd htwo htail ih =>
      cases k with
      | zero => simp
      | succ k =>
          have hk' : k ≤ profile.length := by simpa using hk
          have hrec := ih hk'
          have hstep := havelHakimiStep_sum_le (d :: rest)
          have hfinal := havelHakimiIterate_sum_le k (havelHakimiStep (d :: rest))
          have hoverall :
              ((havelHakimiStep^[k]) (havelHakimiStep (d :: rest))).sum ≤
                (d :: rest).sum := hfinal.trans hstep
          have hrecEq :
              (havelHakimiStep (d :: rest)).sum =
                ((havelHakimiStep^[k]) (havelHakimiStep (d :: rest))).sum +
                  ((profile.take k).sum + 2 * k) := by
            omega
          have hlossEq :
              (d :: rest).sum =
                (havelHakimiStep (d :: rest)).sum + stepLoss (d :: rest) := by
            unfold stepLoss
            omega
          have hexcess :
              stepLoss (d :: rest) = (stepLoss (d :: rest) - 2) + 2 := by
            omega
          rw [Function.iterate_succ_apply]
          simp only [List.take_succ_cons, List.sum_cons]
          calc
            stepLoss (d :: rest) - 2 + (profile.take k).sum + 2 * (k + 1) =
                ((profile.take k).sum + 2 * k) + stepLoss (d :: rest) := by
              omega
            _ = ((havelHakimiStep (d :: rest)).sum -
                ((havelHakimiStep^[k]) (havelHakimiStep (d :: rest))).sum) +
                  stepLoss (d :: rest) := by rw [hrec]
            _ = ((havelHakimiStep (d :: rest)).sum + stepLoss (d :: rest)) -
                ((havelHakimiStep^[k]) (havelHakimiStep (d :: rest))).sum := by
              omega
            _ = (d :: rest).sum -
                ((havelHakimiStep^[k]) (havelHakimiStep (d :: rest))).sum := by
              rw [hlossEq]

/-- Direct mathematical form of weak degree-prefix dominance. -/
def DegreePrefixDominates (source target : List ℕ) : Prop :=
  source.length = target.length ∧
  ∀ k : ℕ, k ≤ source.length →
    (target.take k).sum ≤ (source.take k).sum

theorem DegreePrefixDominates.sum_le {source target : List ℕ}
    (h : DegreePrefixDominates source target) :
    target.sum ≤ source.sum := by
  have hp := h.2 source.length (le_refl _)
  rw [List.take_length] at hp
  rwa [h.1, List.take_length] at hp

/-- The residual-gap condition that converts degree-prefix dominance into a
comparison of the first `k` excess losses.  It says the source's degree-sum
advantage has not shrunk after `k` coupled eliminations. -/
def ResidualGapPreserved (k : ℕ) (source target : List ℕ) : Prop :=
  target.sum + ((havelHakimiStep^[k]) source).sum ≤
    source.sum + ((havelHakimiStep^[k]) target).sum

/-- Formal partial coupling theorem.  Weak degree-prefix dominance supplies
the initial total order; preservation of that total gap at time `k` is exactly
enough to order the chronological excess prefixes. -/
theorem take_excess_sum_le_of_residualGap
    {source target sourceProfile targetProfile : List ℕ}
    (hs : ExcessTrajectory source sourceProfile)
    (ht : ExcessTrajectory target targetProfile)
    (hdegree : DegreePrefixDominates source target)
    {k : ℕ} (hks : k ≤ sourceProfile.length)
    (hkt : k ≤ targetProfile.length)
    (hgap : ResidualGapPreserved k source target) :
    (targetProfile.take k).sum ≤ (sourceProfile.take k).sum := by
  have hsEq := hs.take_sum_add_two_mul hks
  have htEq := ht.take_sum_add_two_mul hkt
  have htotal := hdegree.sum_le
  unfold ResidualGapPreserved at hgap
  omega

/-- If the residual gap is preserved at every common active time, then every
common chronological profile prefix is ordered. -/
theorem common_prefixes_ordered_of_residualGaps
    {source target sourceProfile targetProfile : List ℕ}
    (hs : ExcessTrajectory source sourceProfile)
    (ht : ExcessTrajectory target targetProfile)
    (hdegree : DegreePrefixDominates source target)
    (hgaps : ∀ k : ℕ, k ≤ sourceProfile.length → k ≤ targetProfile.length →
      ResidualGapPreserved k source target) :
    ∀ k : ℕ, k ≤ sourceProfile.length → k ≤ targetProfile.length →
      (targetProfile.take k).sum ≤ (sourceProfile.take k).sum := by
  intro k hks hkt
  exact take_excess_sum_le_of_residualGap hs ht hdegree hks hkt
    (hgaps k hks hkt)

/-- Concrete check of the partial identity on the order-four obstruction's
source profile. -/
theorem two_one_one_zero_partial_identity :
    ExcessTrajectory [2, 1, 1, 0] [2] ∧
    (([2] : List ℕ).take 1).sum + 2 * 1 =
      ([2, 1, 1, 0] : List ℕ).sum -
        ((havelHakimiStep^[1]) [2, 1, 1, 0]).sum := by
  have htail : ExcessTrajectory (havelHakimiStep [2, 1, 1, 0]) [] := by
    convert ExcessTrajectory.zeros 3 using 1
    native_decide
  have hstep :=
    ExcessTrajectory.step 2 [1, 1, 0] [] (by decide) (by native_decide) htail
  have htrajectory : ExcessTrajectory [2, 1, 1, 0] [2] := by
    convert hstep using 1
    native_decide
  exact ⟨htrajectory, by native_decide⟩

end WrittenOnTheWallII.GraphConjecture61PaddedProfile
