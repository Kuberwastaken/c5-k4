import GraphConjecture61SurvivalFlag

/-!
# WOWII 61: bounded prefix saturation

A list whose entries are bounded by `e` has sum at most `length * e`; equality
forces every entry to equal `e`.  Applied to the `(d+1)`-prefix, weak prefix
dominance transports maximum saturation from target to source and therefore
orders the survival multiplicity.
-/

namespace WrittenOnTheWallII.GraphConjecture61PrefixSaturation

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
open WrittenOnTheWallII.GraphConjecture61SurvivalFlag

def DegreePrefixDominates (source target : List ℕ) : Prop :=
  source.length = target.length ∧
  ∀ k : ℕ, k ≤ source.length →
    (target.take k).sum ≤ (source.take k).sum

/-- A pointwise bounded list has the corresponding length-times-bound sum
upper bound. -/
theorem sum_le_length_mul_of_forall_le
    (e : ℕ) (xs : List ℕ) (hbound : ∀ x ∈ xs, x ≤ e) :
    xs.sum ≤ xs.length * e := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      simp only [List.sum_cons, List.length_cons]
      have hx := hbound x (by simp)
      have htail : ∀ y ∈ xs, y ≤ e := by
        intro y hy
        exact hbound y (by simp [hy])
      have := ih htail
      rw [Nat.add_mul]
      omega

/-- Saturating the maximum possible sum forces a constant list. -/
theorem eq_replicate_of_length_mul_le_sum_of_forall_le
    (e : ℕ) (xs : List ℕ) (hbound : ∀ x ∈ xs, x ≤ e)
    (hsat : xs.length * e ≤ xs.sum) :
    xs = List.replicate xs.length e := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      have hx := hbound x (by simp)
      have htail : ∀ y ∈ xs, y ≤ e := by
        intro y hy
        exact hbound y (by simp [hy])
      have htailUpper := sum_le_length_mul_of_forall_le e xs htail
      have hxEq : x = e := by
        simp only [List.length_cons, List.sum_cons] at hsat
        rw [Nat.add_mul] at hsat
        omega
      have htailSat : xs.length * e ≤ xs.sum := by
        simp only [List.length_cons, List.sum_cons, hxEq] at hsat
        rw [Nat.add_mul] at hsat
        omega
      rw [hxEq, ih htail htailSat]
      simp [List.replicate_succ]

/-- A prefix bounded both above and below by `e` is saturated by `e`. This is
the direct endpoint consumed after descending order transports a surviving
maximum back across the decrement boundary. -/
theorem prefix_eq_replicate_of_forall_ge_le
    (d e : ℕ) (xs : List ℕ) (hlen : d + 1 ≤ xs.length)
    (hupper : ∀ x ∈ xs.take (d + 1), x ≤ e)
    (hlower : ∀ x ∈ xs.take (d + 1), e ≤ x) :
    xs.take (d + 1) = List.replicate (d + 1) e := by
  have hlenTake : (xs.take (d + 1)).length = d + 1 := by
    simp [List.length_take, hlen]
  have hall : ∀ x ∈ xs.take (d + 1), x = e := by
    intro x hx
    exact Nat.le_antisymm (hupper x hx) (hlower x hx)
  have heq : xs.take (d + 1) =
      List.replicate (xs.take (d + 1)).length e := by
    apply List.eq_replicate_iff.mpr
    exact ⟨rfl, hall⟩
  rwa [hlenTake] at heq

/-- A saturated `(d+1)`-prefix contains more than `d` copies of its maximum. -/
theorem count_gt_of_saturated_prefix
    (d e : ℕ) (xs : List ℕ)
    (hsat : xs.take (d + 1) = List.replicate (d + 1) e) :
    d < xs.count e := by
  have hcountTake : (xs.take (d + 1)).count e = d + 1 := by
    rw [hsat]
    simp
  have hle : (xs.take (d + 1)).count e ≤ xs.count e := by
    have hsplit := congrArg (fun l : List ℕ ↦ l.count e)
      (List.take_append_drop (d + 1) xs)
    simp only [List.count_append] at hsplit
    omega
  omega

/-- Weak prefix dominance transports a saturated target boundary prefix to a
saturated source boundary prefix. -/
theorem source_prefix_saturated_of_degreePrefixDominates
    (d e : ℕ) (source target : List ℕ)
    (hdom : DegreePrefixDominates source target)
    (hsourceBound : ∀ x ∈ source, x ≤ e)
    (htargetSat : target.take (d + 1) = List.replicate (d + 1) e)
    (hlen : d + 1 ≤ source.length) :
    source.take (d + 1) = List.replicate (d + 1) e := by
  have hp := hdom.2 (d + 1) hlen
  rw [htargetSat] at hp
  have htakeLen : (source.take (d + 1)).length = d + 1 := by
    simp [List.length_take, hlen]
  have hbound : ∀ x ∈ source.take (d + 1), x ≤ e := by
    intro x hx
    exact hsourceBound x (List.mem_of_mem_take hx)
  have hsat : (source.take (d + 1)).length * e ≤
      (source.take (d + 1)).sum := by
    rw [htakeLen]
    simpa using hp
  have heq := eq_replicate_of_length_mul_le_sum_of_forall_le
    e (source.take (d + 1)) hbound hsat
  rwa [htakeLen] at heq

/-- Consequently the source has more than `d` copies of `e`, which is the
exact multiplicity condition needed by the survival theorem. -/
theorem source_count_gt_of_degreePrefixDominates_of_target_saturated
    (d e : ℕ) (source target : List ℕ)
    (hdom : DegreePrefixDominates source target)
    (hsourceBound : ∀ x ∈ source, x ≤ e)
    (htargetSat : target.take (d + 1) = List.replicate (d + 1) e)
    (hlen : d + 1 ≤ source.length) :
    d < source.count e := by
  apply count_gt_of_saturated_prefix d e source
  exact source_prefix_saturated_of_degreePrefixDominates
    d e source target hdom hsourceBound htargetSat hlen

/-- Equal-top-two cumulative monotonicity from full weak prefix dominance once
target survival has been exposed as boundary-prefix saturation. -/
theorem cumulativeHeadSum_two_monotone_of_prefix_saturation
    (d e : ℕ) (sourceTail targetTail : List ℕ)
    (hd : 0 < d) (he : 0 < e)
    (hdom : DegreePrefixDominates (e :: sourceTail) (e :: targetTail))
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (htargetSat : (e :: targetTail).take (d + 1) =
      List.replicate (d + 1) e)
    (hlen : d + 1 ≤ (e :: sourceTail).length) :
    cumulativeHeadSum 2 (d :: e :: targetTail) ≤
      cumulativeHeadSum 2 (d :: e :: sourceTail) := by
  have hsCount := source_count_gt_of_degreePrefixDominates_of_target_saturated
    d e (e :: sourceTail) (e :: targetTail) hdom hsBound htargetSat hlen
  have htCount := count_gt_of_saturated_prefix
    d e (e :: targetTail) htargetSat
  apply cumulativeHeadSum_two_monotone_equalPrefix_of_survival
    d e sourceTail targetTail hd he hsBound htBound
  intro _
  exact undecrementedMax_of_count_gt d e (e :: sourceTail) hsCount

end WrittenOnTheWallII.GraphConjecture61PrefixSaturation
