import FormalConjecturesUtil

/-!
# WOWII 61: step-indexed excess-loss profiles

This file strengthens the unit-loss trajectory class by recording, at every
positive Havel--Hakimi step, the excess of its degree-sum loss above two.
The resulting profile gives an exact closed form for the corrected potential.
-/

namespace WrittenOnTheWallII.GraphConjecture61ExcessProfile

open SimpleGraph

def descendingDegreeList {n : ℕ} (G : SimpleGraph (Fin n))
    [DecidableRel G.Adj] : List ℕ :=
  (Finset.univ.val.map fun v ↦ G.degree v).sort (· ≥ ·)

def IsGraphical (s : List ℕ) : Prop :=
  ∃ n : ℕ, ∃ G : SimpleGraph (Fin n), ∃ h : DecidableRel G.Adj,
    @descendingDegreeList n G h = s

def WeakPrefixDominates (s t : List ℕ) : Prop :=
  s.Pairwise (· ≥ ·) ∧
  t.Pairwise (· ≥ ·) ∧
  s.length = t.length ∧
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

/-- `profile` records `stepLoss - 2` at every positive step, in chronological
order.  Requiring each loss to be at least two makes the subtraction exact.
The trajectory ends only at an all-zero list. -/
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

/-- Exact profile closed form.  Each active vertex contributes the baseline
two, while its profile entry contributes the local excess loss. -/
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

/-- Prefix comparison of chronological excess profiles.  The source may have
additional later active steps, but every target prefix is budgeted by the
corresponding source prefix. -/
def PrefixExcessDominates (source target : List ℕ) : Prop :=
  target.length ≤ source.length ∧
  ∀ k : ℕ, k ≤ target.length →
    (target.take k).sum ≤ (source.take k).sum

theorem take_sum_le_sum (s : List ℕ) (k : ℕ) :
    (s.take k).sum ≤ s.sum := by
  have h := congrArg List.sum (List.take_append_drop k s)
  rw [List.sum_append] at h
  omega

theorem PrefixExcessDominates.sum_le {source target : List ℕ}
    (h : PrefixExcessDominates source target) :
    target.sum ≤ source.sum := by
  have hp := h.2 target.length (le_refl _)
  rw [List.take_length] at hp
  exact hp.trans (take_sum_le_sum source target.length)

/-- Realization-aware potential monotonicity under a chronological prefix
coupling of the excess-loss profiles. -/
theorem graphicalWeakPotentialMonotone_of_excessProfiles
    {s t sourceProfile targetProfile : List ℕ}
    (hs : RealizedExcessTrajectory s sourceProfile)
    (ht : RealizedExcessTrajectory t targetProfile)
    (hdom : WeakPrefixDominates s t)
    (hprofile : PrefixExcessDominates sourceProfile targetProfile) :
    residuePotential t ≤ residuePotential s := by
  rw [hs.2.residuePotential_eq]
  rw [ht.2.residuePotential_eq]
  have hlen := hdom.2.2.1
  have hsum := hprofile.sum_le
  omega

/-- The path on three vertices, with degree list `[2,1,1]`. -/
theorem graphical_two_one_one : IsGraphical [2, 1, 1] := by
  let h : DecidableRel (pathGraph 3).Adj := fun u v ↦
    decidable_of_iff (u.val + 1 = v.val ∨ v.val + 1 = u.val) pathGraph_adj.symm
  refine ⟨3, pathGraph 3, h, ?_⟩
  native_decide

/-- One edge together with one isolated vertex. -/
def oneEdgeOneIsolated : SimpleGraph (Fin 3) :=
  SimpleGraph.fromRel fun u v ↦ u.val = 0 ∧ v.val = 1

instance oneEdgeOneIsolated_decidableAdj :
    DecidableRel oneEdgeOneIsolated.Adj := by
  unfold oneEdgeOneIsolated
  infer_instance

theorem graphical_one_one_zero : IsGraphical [1, 1, 0] := by
  refine ⟨3, oneEdgeOneIsolated, inferInstance, ?_⟩
  native_decide

theorem excessTrajectory_two_one_one : ExcessTrajectory [2, 1, 1] [2] := by
  have htail : ExcessTrajectory (havelHakimiStep [2, 1, 1]) [] := by
    convert ExcessTrajectory.zeros 2 using 1
    native_decide
  have hstep :=
    ExcessTrajectory.step 2 [1, 1] [] (by decide) (by native_decide) htail
  convert hstep using 1
  native_decide

theorem excessTrajectory_one_one_zero : ExcessTrajectory [1, 1, 0] [0] := by
  have htail : ExcessTrajectory (havelHakimiStep [1, 1, 0]) [] := by
    convert ExcessTrajectory.zeros 2 using 1
    native_decide
  have hstep :=
    ExcessTrajectory.step 1 [1, 0] [] (by decide) (by native_decide) htail
  convert hstep using 1
  native_decide

/-- Strict extension beyond the unit-loss class.  The source `P₃` has first
loss four and excess profile `[2]`; it couples to the matching-plus-isolate
profile `[0]`, proving the corrected potential comparison `6 ≤ 8`. -/
theorem path_to_matching_excessProfile_certificate :
    RealizedExcessTrajectory [2, 1, 1] [2] ∧
    RealizedExcessTrajectory [1, 1, 0] [0] ∧
    WeakPrefixDominates [2, 1, 1] [1, 1, 0] ∧
    PrefixExcessDominates [2] [0] ∧
    residuePotential [1, 1, 0] = 6 ∧
    residuePotential [2, 1, 1] = 8 := by
  refine ⟨⟨graphical_two_one_one, excessTrajectory_two_one_one⟩,
    ⟨graphical_one_one_zero, excessTrajectory_one_one_zero⟩, ?_⟩
  refine ⟨by native_decide, ?_, by native_decide⟩
  constructor
  · decide
  · intro k hk
    norm_num at hk
    interval_cases k <;> native_decide

end WrittenOnTheWallII.GraphConjecture61ExcessProfile
