import FormalConjecturesUtil

/-!
# WOWII 61: graphical one-step potential simulation

This file isolates the exact loss budget needed to lift a corrected-potential
comparison through one Havel--Hakimi recursion step.  It also gives the first
graphical counterexample to the stronger, false claim that successor
potentials preserve their current-state order.
-/

namespace WrittenOnTheWallII.GraphConjecture61GraphicalPotential

open SimpleGraph

def descendingDegreeList {n : ℕ} (G : SimpleGraph (Fin n))
    [DecidableRel G.Adj] : List ℕ :=
  (Finset.univ.val.map fun v ↦ G.degree v).sort (· ≥ ·)

/-- Graphicality always carries an explicit finite simple-graph realization. -/
def IsGraphical (s : List ℕ) : Prop :=
  ∃ n : ℕ, ∃ G : SimpleGraph (Fin n), ∃ h : DecidableRel G.Adj,
    @descendingDegreeList n G h = s

/-- Weak prefix dominance, allowing unequal total sums. -/
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

/-- Strongest proved recursive lifting rung.  Successor potential order may
reverse; the exact degree-loss budget restores the current-state comparison. -/
theorem residuePotential_le_of_oneStep_budget
    (ds dt : ℕ) (rs rt : List ℕ)
    (hds : ds ≠ 0) (hdt : dt ≠ 0)
    (hbudget :
      residuePotential (havelHakimiStep (dt :: rt)) + stepLoss (dt :: rt) ≤
      residuePotential (havelHakimiStep (ds :: rs)) + stepLoss (ds :: rs)) :
    residuePotential (dt :: rt) ≤ residuePotential (ds :: rs) := by
  rw [residuePotential_cons_eq_step_add_loss ds rs hds]
  rw [residuePotential_cons_eq_step_add_loss dt rt hdt]
  exact hbudget

/-- The committed first graphical transfer satisfies the loss-budgeted lift. -/
theorem committed_first_transfer_oneStep_budget :
    WeakPrefixDominates [2, 1, 1, 0] [1, 1, 1, 1] ∧
    residuePotential (havelHakimiStep [1, 1, 1, 1]) + stepLoss [1, 1, 1, 1] ≤
      residuePotential (havelHakimiStep [2, 1, 1, 0]) + stepLoss [2, 1, 1, 0] ∧
    residuePotential [1, 1, 1, 1] ≤ residuePotential [2, 1, 1, 0] := by
  native_decide

/-- The paw graph, with degree list `[3,2,2,1]`. -/
def pawFour : SimpleGraph (Fin 4) :=
  SimpleGraph.fromRel fun u v ↦
    (u.val = 0 ∧ v.val = 1) ∨
    (u.val = 0 ∧ v.val = 2) ∨
    (u.val = 0 ∧ v.val = 3) ∨
    (u.val = 1 ∧ v.val = 2)

instance pawFour_decidableAdj : DecidableRel pawFour.Adj := by
  unfold pawFour
  infer_instance

/-- The four-cycle, with degree list `[2,2,2,2]`. -/
def cycleFour : SimpleGraph (Fin 4) :=
  SimpleGraph.fromRel fun u v ↦
    (u.val = 0 ∧ v.val = 1) ∨
    (u.val = 1 ∧ v.val = 2) ∨
    (u.val = 2 ∧ v.val = 3) ∨
    (u.val = 3 ∧ v.val = 0)

instance cycleFour_decidableAdj : DecidableRel cycleFour.Adj := by
  unfold cycleFour
  infer_instance

theorem graphical_three_two_two_one : IsGraphical [3, 2, 2, 1] := by
  refine ⟨4, pawFour, inferInstance, ?_⟩
  native_decide

theorem graphical_two_two_two_two : IsGraphical [2, 2, 2, 2] := by
  refine ⟨4, cycleFour, inferInstance, ?_⟩
  native_decide

/-- Smallest graphical obstruction to the stronger claim that successor
potentials retain their current-state order.  The loss budget is exactly two
and repairs the reversed successor inequality. -/
theorem first_successor_order_obstruction :
    IsGraphical [3, 2, 2, 1] ∧
    IsGraphical [2, 2, 2, 2] ∧
    WeakPrefixDominates [3, 2, 2, 1] [2, 2, 2, 2] ∧
    residuePotential [3, 2, 2, 1] = residuePotential [2, 2, 2, 2] ∧
    residuePotential (havelHakimiStep [3, 2, 2, 1]) = 6 ∧
    residuePotential (havelHakimiStep [2, 2, 2, 2]) = 8 ∧
    stepLoss [3, 2, 2, 1] = 6 ∧
    stepLoss [2, 2, 2, 2] = 4 := by
  refine ⟨graphical_three_two_two_one, graphical_two_two_two_two, ?_⟩
  native_decide

end WrittenOnTheWallII.GraphConjecture61GraphicalPotential
