import FormalConjecturesUtil

/-!
# WOWII 61: head-credit funding

For every admissible positive Havel--Hakimi step, degree-sum loss is twice the
head.  Therefore the local banked-credit rule is exactly a head inequality.
-/

namespace WrittenOnTheWallII.GraphConjecture61HeadCredit

open SimpleGraph

def stepLoss (s : List ℕ) : ℕ :=
  s.sum - (havelHakimiStep s).sum

def cumulativeStepLoss : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => stepLoss s + cumulativeStepLoss k (havelHakimiStep s)

def creditBalance (k : ℕ) (source target : List ℕ) : ℕ :=
  cumulativeStepLoss k source - cumulativeStepLoss k target

def StepAdmissible : List ℕ → Prop
  | [] => True
  | d :: rest => d ≤ rest.length ∧ ∀ x ∈ rest.take d, 0 < x

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

/-- Reused admissible-step identity: loss is exactly twice the head. -/
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

/-- At one coupled active time, local credit funding and head-credit funding
are definitionally the same after admissible loss evaluation. -/
theorem localFunding_iff_headCredit
    (credit ds dt : ℕ) (rs rt : List ℕ)
    (hs : StepAdmissible (ds :: rs))
    (ht : StepAdmissible (dt :: rt)) :
    stepLoss (dt :: rt) ≤ credit + stepLoss (ds :: rs) ↔
      2 * dt ≤ credit + 2 * ds := by
  rw [stepLoss_eq_twice_head dt rt ht, stepLoss_eq_twice_head ds rs hs]

/-- Time-indexed local funding predicate, retaining explicit nonempty
successor decompositions and admissibility. -/
def HeadCreditFundedAt (k : ℕ) (source target : List ℕ) : Prop :=
  ∃ ds rs dt rt,
    (havelHakimiStep^[k]) source = ds :: rs ∧
    (havelHakimiStep^[k]) target = dt :: rt ∧
    StepAdmissible (ds :: rs) ∧ StepAdmissible (dt :: rt) ∧
    2 * dt ≤ creditBalance k source target + 2 * ds

/-- A funded head inequality supplies the exact local credit rule. -/
theorem localCreditBudget_of_headCreditFundedAt
    {k : ℕ} {source target : List ℕ}
    (h : HeadCreditFundedAt k source target) :
    stepLoss ((havelHakimiStep^[k]) target) ≤
      creditBalance k source target +
        stepLoss ((havelHakimiStep^[k]) source) := by
  obtain ⟨ds, rs, dt, rt, hsEq, htEq, hs, ht, hhead⟩ := h
  rw [hsEq, htEq]
  exact (localFunding_iff_headCredit (creditBalance k source target)
    ds dt rs rt hs ht).2 hhead

/-- Conversely the local credit rule yields the head inequality whenever both
current lists are explicitly admissible and nonempty. -/
theorem headCreditFundedAt_of_localCreditBudget
    {k : ℕ} {source target : List ℕ}
    {ds dt : ℕ} {rs rt : List ℕ}
    (hsEq : (havelHakimiStep^[k]) source = ds :: rs)
    (htEq : (havelHakimiStep^[k]) target = dt :: rt)
    (hs : StepAdmissible (ds :: rs))
    (ht : StepAdmissible (dt :: rt))
    (hbudget : stepLoss ((havelHakimiStep^[k]) target) ≤
      creditBalance k source target +
        stepLoss ((havelHakimiStep^[k]) source)) :
    HeadCreditFundedAt k source target := by
  refine ⟨ds, rs, dt, rt, hsEq, htEq, hs, ht, ?_⟩
  rw [hsEq, htEq] at hbudget
  exact (localFunding_iff_headCredit (creditBalance k source target)
    ds dt rs rt hs ht).1 hbudget

/-- The regular-shape class has the required local admissibility. -/
theorem regularShape_admissible {d n : ℕ} (hd : 0 < d) (hfit : d ≤ n) :
    StepAdmissible (d :: List.replicate n d) := by
  constructor
  · simpa using hfit
  · intro x hx
    have hx' : x ∈ List.replicate n d := List.mem_of_mem_take hx
    simp only [List.mem_replicate] at hx'
    simpa [hx'.2] using hd

end WrittenOnTheWallII.GraphConjecture61HeadCredit
