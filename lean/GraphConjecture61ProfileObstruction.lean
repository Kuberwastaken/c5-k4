import FormalConjecturesUtil

/-!
# WOWII 61: first excess-profile obstruction and zero-padded repair

The first proposed profile coupling required the target trajectory to be no
longer than the source trajectory.  This file gives the first realized
graphical obstruction and replaces that artificial length condition by
zero-padded chronological prefix comparison.
-/

namespace WrittenOnTheWallII.GraphConjecture61ProfileObstruction

open SimpleGraph

def descendingDegreeList {n : ℕ} (G : SimpleGraph (Fin n))
    [DecidableRel G.Adj] : List ℕ :=
  (Finset.univ.val.map fun v ↦ G.degree v).sort (· ≥ ·)

def IsGraphical (s : List ℕ) : Prop :=
  ∃ n : ℕ, ∃ G : SimpleGraph (Fin n), ∃ h : DecidableRel G.Adj,
    @descendingDegreeList n G h = s

def WeakPrefixDominates (s t : List ℕ) : Prop :=
  s.Pairwise (· ≥ ·) ∧ t.Pairwise (· ≥ ·) ∧ s.length = t.length ∧
  (List.ofFn (fun k : Fin (s.length + 1) ↦
    decide ((t.take k).sum ≤ (s.take k).sum))).all id = true

instance instDecidableWeakPrefixDominates (s t : List ℕ) :
    Decidable (WeakPrefixDominates s t) := by
  unfold WeakPrefixDominates
  infer_instance

def residuePotential (s : List ℕ) : ℕ :=
  2 * residueAux s + s.sum

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

theorem residuePotential_cons_eq_step_add_loss
    (d : ℕ) (rest : List ℕ) (hd : d ≠ 0) :
    residuePotential (d :: rest) =
      residuePotential (havelHakimiStep (d :: rest)) + stepLoss (d :: rest) := by
  have hsum := havelHakimiStep_sum_le (d :: rest)
  unfold residuePotential stepLoss
  rw [residueAux.eq_3 d rest hd]
  omega

inductive ExcessTrajectory : List ℕ → List ℕ → Prop
  | zeros (z : ℕ) : ExcessTrajectory (List.replicate z 0) []
  | step (d : ℕ) (rest profile : List ℕ) (hd : d ≠ 0)
      (htwo : 2 ≤ stepLoss (d :: rest))
      (htail : ExcessTrajectory (havelHakimiStep (d :: rest)) profile) :
      ExcessTrajectory (d :: rest) ((stepLoss (d :: rest) - 2) :: profile)

def RealizedExcessTrajectory (s profile : List ℕ) : Prop :=
  IsGraphical s ∧ ExcessTrajectory s profile

theorem residuePotential_replicate_zero (z : ℕ) :
    residuePotential (List.replicate z 0) = 2 * z := by
  cases z with
  | zero =>
      unfold residuePotential
      simp only [List.replicate_zero, List.sum_nil]
      rw [residueAux.eq_1]
      simp
  | succ z =>
      unfold residuePotential
      rw [List.replicate_succ, residueAux.eq_2]
      simp only [List.length_replicate, List.sum_cons, List.sum_replicate,
        nsmul_zero, Nat.zero_add]
      omega

theorem ExcessTrajectory.residuePotential_eq
    {s profile : List ℕ} (h : ExcessTrajectory s profile) :
    residuePotential s = 2 * s.length + profile.sum := by
  induction h with
  | zeros z => simpa using residuePotential_replicate_zero z
  | step d rest profile hd htwo htail ih =>
      rw [residuePotential_cons_eq_step_add_loss d rest hd, ih]
      rw [havelHakimiStep_length_cons]
      simp only [List.length_cons, List.sum_cons]
      have hloss : stepLoss (d :: rest) = 2 + (stepLoss (d :: rest) - 2) := by
        omega
      rw [hloss]
      omega

/-- The v0.10 coupling.  Its profile-length premise is now known to be too
strong. -/
def PrefixExcessDominates (source target : List ℕ) : Prop :=
  target.length ≤ source.length ∧
  ∀ k : ℕ, k ≤ target.length →
    (target.take k).sum ≤ (source.take k).sum

/-- Corrected coupling: lists are implicitly padded by trailing zeroes, so
only chronological prefix sums matter. -/
def PaddedPrefixExcessDominates (source target : List ℕ) : Prop :=
  ∀ k : ℕ, k ≤ target.length →
    (target.take k).sum ≤ (source.take k).sum

theorem take_sum_le_sum (s : List ℕ) (k : ℕ) :
    (s.take k).sum ≤ s.sum := by
  have h := congrArg List.sum (List.take_append_drop k s)
  rw [List.sum_append] at h
  omega

theorem PaddedPrefixExcessDominates.sum_le {source target : List ℕ}
    (h : PaddedPrefixExcessDominates source target) :
    target.sum ≤ source.sum := by
  have hp := h target.length (le_refl _)
  rw [List.take_length] at hp
  exact hp.trans (take_sum_le_sum source target.length)

theorem graphicalWeakPotentialMonotone_of_paddedExcessProfiles
    {s t sourceProfile targetProfile : List ℕ}
    (hs : RealizedExcessTrajectory s sourceProfile)
    (ht : RealizedExcessTrajectory t targetProfile)
    (hdom : WeakPrefixDominates s t)
    (hprofile : PaddedPrefixExcessDominates sourceProfile targetProfile) :
    residuePotential t ≤ residuePotential s := by
  rw [hs.2.residuePotential_eq]
  rw [ht.2.residuePotential_eq]
  have hlen := hdom.2.2.1
  have hsum := hprofile.sum_le
  omega

/-- `P3` together with an isolated vertex. -/
def pathThreeWithIsolated : SimpleGraph (Fin 4) :=
  SimpleGraph.fromRel fun u v ↦
    (u.val = 0 ∧ v.val = 1) ∨ (u.val = 1 ∧ v.val = 2)

instance pathThreeWithIsolated_decidableAdj :
    DecidableRel pathThreeWithIsolated.Adj := by
  unfold pathThreeWithIsolated
  infer_instance

/-- A perfect matching on four vertices. -/
def matchingFour : SimpleGraph (Fin 4) :=
  SimpleGraph.fromRel fun u v ↦
    (u.val = 0 ∧ v.val = 1) ∨ (u.val = 2 ∧ v.val = 3)

instance matchingFour_decidableAdj : DecidableRel matchingFour.Adj := by
  unfold matchingFour
  infer_instance

theorem graphical_two_one_one_zero : IsGraphical [2, 1, 1, 0] := by
  refine ⟨4, pathThreeWithIsolated, inferInstance, ?_⟩
  native_decide

theorem graphical_one_one_one_one : IsGraphical [1, 1, 1, 1] := by
  refine ⟨4, matchingFour, inferInstance, ?_⟩
  native_decide

theorem excessTrajectory_two_one_one_zero :
    ExcessTrajectory [2, 1, 1, 0] [2] := by
  have htail : ExcessTrajectory (havelHakimiStep [2, 1, 1, 0]) [] := by
    convert ExcessTrajectory.zeros 3 using 1
    native_decide
  have hstep :=
    ExcessTrajectory.step 2 [1, 1, 0] [] (by decide) (by native_decide) htail
  convert hstep using 1
  native_decide

theorem excessTrajectory_one_one_one_one :
    ExcessTrajectory [1, 1, 1, 1] [0, 0] := by
  have hzero : ExcessTrajectory [0, 0] [] := ExcessTrajectory.zeros 2
  have hsecond : ExcessTrajectory [1, 1, 0] [0] := by
    have htail : ExcessTrajectory (havelHakimiStep [1, 1, 0]) [] := by
      convert hzero using 1
      native_decide
    have hstep :=
      ExcessTrajectory.step 1 [1, 0] [] (by decide) (by native_decide) htail
    convert hstep using 1
    native_decide
  have htail : ExcessTrajectory (havelHakimiStep [1, 1, 1, 1]) [0] := by
    convert hsecond using 1
    native_decide
  have hfirst :=
    ExcessTrajectory.step 1 [1, 1, 1] [0] (by decide) (by native_decide) htail
  convert hfirst using 1
  native_decide

/-- First obstruction by graph order.  Both endpoints are explicitly realized
and weakly prefix ordered, but the target profile is longer.  Zero padding
repairs the coupling and preserves the desired potential direction. -/
theorem first_profileLength_obstruction :
    RealizedExcessTrajectory [2, 1, 1, 0] [2] ∧
    RealizedExcessTrajectory [1, 1, 1, 1] [0, 0] ∧
    WeakPrefixDominates [2, 1, 1, 0] [1, 1, 1, 1] ∧
    ¬ PrefixExcessDominates [2] [0, 0] ∧
    PaddedPrefixExcessDominates [2] [0, 0] ∧
    residuePotential [1, 1, 1, 1] = 8 ∧
    residuePotential [2, 1, 1, 0] = 10 := by
  refine ⟨⟨graphical_two_one_one_zero, excessTrajectory_two_one_one_zero⟩,
    ⟨graphical_one_one_one_one, excessTrajectory_one_one_one_one⟩,
    by native_decide, ?_, ?_, by native_decide⟩
  · intro h
    exact (by omega : ¬ 2 ≤ 1) h.1
  · intro k hk
    norm_num at hk
    interval_cases k <;> native_decide

end WrittenOnTheWallII.GraphConjecture61ProfileObstruction
