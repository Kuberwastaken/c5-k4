import FormalConjecturesUtil

/-!
# WOWII 61: a realization-aware unit-loss coupling class

The scalar accumulated-loss state is circular in general.  This file adds
genuine structural information: both realized degree lists must admit complete
Havel--Hakimi trajectories in which every positive step loses exactly two
units of degree sum.  On this matching-type class the corrected potential is
forced to be twice the order, so every same-order coupling is exact equality.
-/

namespace WrittenOnTheWallII.GraphConjecture61Coupling

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

/-- Structural certificate for a matching-type elimination history.  Unlike
an accumulated scalar budget, it records that every individual active step
has the minimum graphical degree-sum loss two, and that the terminal state is
an all-zero list. -/
inductive UnitLossTrajectory : List ℕ → Prop
  | zeros (z : ℕ) : UnitLossTrajectory (List.replicate z 0)
  | step (d : ℕ) (rest : List ℕ) (hd : d ≠ 0)
      (hloss : stepLoss (d :: rest) = 2)
      (htail : UnitLossTrajectory (havelHakimiStep (d :: rest))) :
      UnitLossTrajectory (d :: rest)

/-- Realization-aware version of the class.  Numerical trajectories alone do
not qualify: the list must be the complete degree list of a finite graph. -/
def RealizedUnitLossTrajectory (s : List ℕ) : Prop :=
  IsGraphical s ∧ UnitLossTrajectory s

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

/-- The structural class has a closed-form potential: exactly twice its list
length, independently of how many matching edges were eliminated. -/
theorem UnitLossTrajectory.residuePotential_eq_twice_length
    {s : List ℕ} (hs : UnitLossTrajectory s) :
    residuePotential s = 2 * s.length := by
  induction hs with
  | zeros z => simpa using residuePotential_replicate_zero z
  | step d rest hd hloss htail ih =>
      rw [residuePotential_cons_eq_step_add_loss d rest hd, hloss, ih]
      rw [havelHakimiStep_length_cons]
      simp only [List.length_cons]
      omega

/-- A genuine same-order coupled class for the desired potential direction.
Weak prefix dominance supplies the common order; the structural trajectories
force equality, not merely an inequality. -/
theorem graphicalWeakPotentialMonotone_of_unitLossTrajectories
    {s t : List ℕ}
    (hs : RealizedUnitLossTrajectory s)
    (ht : RealizedUnitLossTrajectory t)
    (hdom : WeakPrefixDominates s t) :
    residuePotential t ≤ residuePotential s := by
  rw [hs.2.residuePotential_eq_twice_length]
  rw [ht.2.residuePotential_eq_twice_length]
  rw [hdom.2.2.1]

/-- The stronger equality exposed by the coupling theorem. -/
theorem graphicalWeakPotential_eq_of_unitLossTrajectories
    {s t : List ℕ}
    (hs : RealizedUnitLossTrajectory s)
    (ht : RealizedUnitLossTrajectory t)
    (hdom : WeakPrefixDominates s t) :
    residuePotential t = residuePotential s := by
  rw [hs.2.residuePotential_eq_twice_length]
  rw [ht.2.residuePotential_eq_twice_length]
  exact congrArg (2 * ·) hdom.2.2.1.symm

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

theorem graphical_zero_zero_zero : IsGraphical [0, 0, 0] := by
  refine ⟨3, ⊥, inferInstance, ?_⟩
  native_decide

theorem unitLossTrajectory_one_one_zero : UnitLossTrajectory [1, 1, 0] := by
  apply UnitLossTrajectory.step 1 [1, 0] (by decide) (by native_decide)
  convert UnitLossTrajectory.zeros 2 using 1
  native_decide

theorem unitLossTrajectory_zero_zero_zero : UnitLossTrajectory [0, 0, 0] := by
  exact UnitLossTrajectory.zeros 3

/-- Nonvacuous coupled transfer: a realized matching plus isolate weakly
dominates the realized empty graph on the same vertices, and both corrected
potentials are six. -/
theorem matching_to_empty_coupling_certificate :
    RealizedUnitLossTrajectory [1, 1, 0] ∧
    RealizedUnitLossTrajectory [0, 0, 0] ∧
    WeakPrefixDominates [1, 1, 0] [0, 0, 0] ∧
    residuePotential [0, 0, 0] = residuePotential [1, 1, 0] ∧
    residuePotential [1, 1, 0] = 6 := by
  refine ⟨⟨graphical_one_one_zero, unitLossTrajectory_one_one_zero⟩,
    ⟨graphical_zero_zero_zero, unitLossTrajectory_zero_zero_zero⟩, ?_⟩
  native_decide

end WrittenOnTheWallII.GraphConjecture61Coupling
