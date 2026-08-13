import FormalConjecturesUtil

/-!
# WOWII 61: cumulative eliminated-head credit

On an admissible trajectory every loss is twice the eliminated head.  This
file turns cumulative credit into twice a cumulative head-sum difference and
isolates the precise head-prefix invariant needed for induction.
-/

namespace WrittenOnTheWallII.GraphConjecture61CumulativeCredit

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

def headDegree : List ℕ → ℕ
  | [] => 0
  | d :: _ => d

def cumulativeHeadSum : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => headDegree s + cumulativeHeadSum k (havelHakimiStep s)

/-- Explicit premise that the first `k` states are nonempty and admissible. -/
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

/-- Exact trajectory identity: cumulative degree loss is twice the sum of all
eliminated heads. -/
theorem cumulativeStepLoss_eq_twice_cumulativeHeadSum
    {k : ℕ} {s : List ℕ} (h : AdmissibleFor k s) :
    cumulativeStepLoss k s = 2 * cumulativeHeadSum k s := by
  induction k generalizing s with
  | zero => simp [cumulativeStepLoss, cumulativeHeadSum]
  | succ k ih =>
      obtain ⟨d, rest, hs, hadm, htail⟩ := h
      subst s
      simp only [cumulativeStepLoss, cumulativeHeadSum, headDegree]
      rw [stepLoss_eq_twice_head d rest hadm]
      rw [ih htail]
      omega

theorem cumulativeHeadSum_succ (k : ℕ) (s : List ℕ) :
    cumulativeHeadSum (k + 1) s =
      cumulativeHeadSum k s + headDegree ((havelHakimiStep^[k]) s) := by
  induction k generalizing s with
  | zero => simp [cumulativeHeadSum]
  | succ k ih =>
      change headDegree s + cumulativeHeadSum (k + 1) (havelHakimiStep s) =
        headDegree s + cumulativeHeadSum k (havelHakimiStep s) +
          headDegree ((havelHakimiStep^[k + 1]) s)
      rw [ih (havelHakimiStep s)]
      rw [Function.iterate_succ_apply]
      omega

/-- Under cumulative head-prefix order, natural credit is exactly twice the
difference of cumulative eliminated-head sums. -/
theorem creditBalance_eq_twice_headDifference
    {k : ℕ} {source target : List ℕ}
    (hs : AdmissibleFor k source) (ht : AdmissibleFor k target)
    (hheads : cumulativeHeadSum k target ≤ cumulativeHeadSum k source) :
    creditBalance k source target =
      2 * (cumulativeHeadSum k source - cumulativeHeadSum k target) := by
  rw [creditBalance, cumulativeStepLoss_eq_twice_cumulativeHeadSum hs,
    cumulativeStepLoss_eq_twice_cumulativeHeadSum ht]
  omega

/-- The local head-credit inequality is equivalent to extending cumulative
head-sum order by one step. -/
theorem headCredit_iff_next_cumulativeHeadOrder
    {k : ℕ} {source target : List ℕ}
    (hs : AdmissibleFor k source) (ht : AdmissibleFor k target)
    (hheads : cumulativeHeadSum k target ≤ cumulativeHeadSum k source) :
    (2 * headDegree ((havelHakimiStep^[k]) target) ≤
        creditBalance k source target +
          2 * headDegree ((havelHakimiStep^[k]) source)) ↔
      (cumulativeHeadSum k target +
          headDegree ((havelHakimiStep^[k]) target) ≤
        cumulativeHeadSum k source +
          headDegree ((havelHakimiStep^[k]) source)) := by
  rw [creditBalance_eq_twice_headDifference hs ht hheads]
  omega

/-- Minimal exact invariant: every prefix of eliminated target heads is
bounded by the corresponding source prefix. -/
def CumulativeHeadDominates (k : ℕ) (source target : List ℕ) : Prop :=
  ∀ j : ℕ, j ≤ k → cumulativeHeadSum j target ≤ cumulativeHeadSum j source

/-- The head-credit rule extends the cumulative-head invariant by one. -/
theorem cumulativeHeadDominates_succ_of_headCredit
    {k : ℕ} {source target : List ℕ}
    (hs : AdmissibleFor k source) (ht : AdmissibleFor k target)
    (hdom : CumulativeHeadDominates k source target)
    (hcredit : 2 * headDegree ((havelHakimiStep^[k]) target) ≤
      creditBalance k source target +
        2 * headDegree ((havelHakimiStep^[k]) source)) :
    CumulativeHeadDominates (k + 1) source target := by
  intro j hj
  by_cases hle : j ≤ k
  · exact hdom j hle
  · have hjEq : j = k + 1 := by omega
    subst j
    have hk := hdom k (le_refl _)
    have hnext := (headCredit_iff_next_cumulativeHeadOrder hs ht hk).1 hcredit
    rw [cumulativeHeadSum_succ, cumulativeHeadSum_succ]
    exact hnext

end WrittenOnTheWallII.GraphConjecture61CumulativeCredit
