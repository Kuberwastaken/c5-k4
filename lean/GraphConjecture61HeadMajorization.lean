import FormalConjecturesUtil

/-!
# WOWII 61: boundary of an incident-edge extremal characterization

The tempting identification of cumulative Havel--Hakimi heads with the maximum
number of edges incident to `k` vertices is false.  This file certifies the
degree-sequence side of the first obstruction and records the exact corrected
functional: cumulative heads are half the degree sum removed by canonical
reduction.
-/

namespace WrittenOnTheWallII.GraphConjecture61HeadMajorization

open SimpleGraph

def headDegree : List ℕ → ℕ
  | [] => 0
  | d :: _ => d

def cumulativeHeadSum : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => headDegree s + cumulativeHeadSum k (havelHakimiStep s)

def stepLoss (s : List ℕ) : ℕ :=
  s.sum - (havelHakimiStep s).sum

def cumulativeStepLoss : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => stepLoss s + cumulativeStepLoss k (havelHakimiStep s)

def StepAdmissible : List ℕ → Prop
  | [] => True
  | d :: rest => d ≤ rest.length ∧ ∀ x ∈ rest.take d, 0 < x

def AdmissibleFor : ℕ → List ℕ → Prop
  | 0, _ => True
  | k + 1, s =>
      ∃ d rest, s = d :: rest ∧ StepAdmissible s ∧
        AdmissibleFor k (havelHakimiStep s)

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
      have := length_le_sum_of_pos hxs
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
    have := length_le_sum_of_pos hpos
    omega
  omega

theorem stepLoss_eq_twice_head
    (d : ℕ) (rest : List ℕ) (h : StepAdmissible (d :: rest)) :
    stepLoss (d :: rest) = 2 * d := by
  have hsum := havelHakimiStep_sum_of_admissible d rest h
  have hlen : (rest.take d).length = d := by simp [h.1]
  have htake := length_le_sum_of_pos h.2
  have hsplit := congrArg List.sum (List.take_append_drop d rest)
  rw [List.sum_append] at hsplit
  have hdle : d ≤ rest.sum := by omega
  unfold stepLoss
  simp only [List.sum_cons]
  omega

/-- Correct functional: twice cumulative heads is exactly cumulative removed
degree sum, for every admissible canonical history. -/
theorem twice_cumulativeHeadSum_eq_cumulativeStepLoss
    {k : ℕ} {s : List ℕ} (h : AdmissibleFor k s) :
    2 * cumulativeHeadSum k s = cumulativeStepLoss k s := by
  induction k generalizing s with
  | zero => simp [cumulativeHeadSum, cumulativeStepLoss]
  | succ k ih =>
      obtain ⟨d, rest, hs, hadm, htail⟩ := h
      subst s
      simp only [cumulativeHeadSum, cumulativeStepLoss, headDegree]
      rw [stepLoss_eq_twice_head d rest hadm, ← ih htail]
      omega

/-- The first extremal-characterization obstruction uses degree sequence
`[2,2,2,1,1]`: its first two canonical eliminated heads sum to three. -/
theorem first_incidentExtremal_obstruction_head_value :
    cumulativeHeadSum 2 [2, 2, 2, 1, 1] = 3 := by
  have hstep : havelHakimiStep [2, 2, 2, 1, 1] = [1, 1, 1, 1] := by
    change ([1, 1, 1, 1] : List ℕ).mergeSort (· ≥ ·) = [1, 1, 1, 1]
    exact List.mergeSort_eq_self (r := fun a b : ℕ ↦ a ≥ b) (by decide)
  rw [show cumulativeHeadSum 2 [2, 2, 2, 1, 1] =
      2 + headDegree (havelHakimiStep [2, 2, 2, 1, 1]) by
    rfl]
  rw [hstep]
  rfl

/-- Four edges can be incident to two vertices in a five-vertex path; this
finite edge-list certificate is independent of graph-library evaluation. -/
def pathFiveEdges : List (Fin 5 × Fin 5) :=
  [(0, 1), (1, 2), (2, 3), (3, 4)]

def incidentToPair (u v : Fin 5) (e : Fin 5 × Fin 5) : Bool :=
  e.1 = u || e.2 = u || e.1 = v || e.2 = v

theorem pathFive_two_vertices_incident_four :
    (pathFiveEdges.filter (incidentToPair 1 3)).length = 4 := by
  decide

/-- Hence the proposed equality with maximum incident-edge count cannot hold:
the canonical head value is three while one two-vertex set already sees four
edges. -/
theorem incidentExtremal_identity_false :
    cumulativeHeadSum 2 [2, 2, 2, 1, 1] <
      (pathFiveEdges.filter (incidentToPair 1 3)).length := by
  rw [first_incidentExtremal_obstruction_head_value,
    pathFive_two_vertices_incident_four]
  norm_num

end WrittenOnTheWallII.GraphConjecture61HeadMajorization
