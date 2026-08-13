import GraphConjecture61SuccessorSurvivalBoundary

/-!
# WOWII 61: exact original-tail multiplicity behind successor survival

The needed successor boundary-prefix inequality is equivalent, on the
saturation wall, to one count in the unsorted laid-off tail.  This file pulls
that count back exactly to the original tail: copies of `e+1` among the first
`p` entries plus copies of `e` after the first `p` entries.
-/

namespace WrittenOnTheWallII.GraphConjecture61BoundaryMultiplicity

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
open WrittenOnTheWallII.GraphConjecture61PrefixSaturation
open WrittenOnTheWallII.GraphConjecture61SurvivalFlag
open WrittenOnTheWallII.GraphConjecture61DescendingSurvival

/-- The unsorted tail produced before the final Havel--Hakimi merge sort. -/
def laidOffTail (p : ℕ) (rest : List ℕ) : List ℕ :=
  (rest.take p).map (· - 1) ++ rest.drop p

/-- Original-tail scalar controlling how many copies of `e` occur after the
layoff: selected `e+1` entries fall to `e`, and unselected `e` entries stay. -/
def boundaryMultiplicity (p e : ℕ) (rest : List ℕ) : ℕ :=
  (rest.take p).count (e + 1) + (rest.drop p).count e

theorem count_pred_map (e : ℕ) (xs : List ℕ) (he : 0 < e) :
    (xs.map (· - 1)).count e = xs.count (e + 1) := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      simp only [List.map_cons, List.count_cons, ih]
      by_cases hx : x = e + 1
      · subst x
        simp
      · have hpred : x - 1 ≠ e := by omega
        simp [hx, hpred]

/-- Exact pullback of the successor maximum multiplicity to the original
tail, before sorting. -/
theorem laidOffTail_count_eq_boundaryMultiplicity
    (p e : ℕ) (rest : List ℕ) (he : 0 < e) :
    (laidOffTail p rest).count e = boundaryMultiplicity p e rest := by
  unfold laidOffTail boundaryMultiplicity
  rw [List.count_append]
  rw [count_pred_map e (rest.take p) he]

/-- Sorting the laid-off tail does not change this controlling multiplicity. -/
theorem havelHakimiStep_count_eq_boundaryMultiplicity
    (p e : ℕ) (rest : List ℕ) (he : 0 < e) :
    (havelHakimiStep (p :: rest)).count e = boundaryMultiplicity p e rest := by
  have hp := List.mergeSort_perm (laidOffTail p rest) (· ≥ ·)
  have hc := hp.count_eq e
  rw [show havelHakimiStep (p :: rest) =
      (laidOffTail p rest).mergeSort (· ≥ ·) by
    simp [havelHakimiStep, laidOffTail, List.splitAt_eq]]
  rw [hc]
  exact laidOffTail_count_eq_boundaryMultiplicity p e rest he

/-- Survival itself implies strictly more than `d` copies of the surviving
maximum in the whole list. -/
theorem count_gt_of_survival
    (d e : ℕ) (tail : List ℕ)
    (hdesc : (e :: tail).Pairwise (fun x y ↦ y ≤ x))
    (hbound : ∀ x ∈ e :: tail, x ≤ e)
    (hsurvive : UndecrementedMax d e (e :: tail)) :
    d < (e :: tail).count e := by
  have hsat := take_eq_replicate_of_survival d e (e :: tail)
    hdesc hbound hsurvive
  exact count_gt_of_saturated_prefix d e (e :: tail) hsat

/-- Ordering the original-tail boundary multiplicity transfers the successor
survival bit.  This avoids any successor-prefix comparison. -/
theorem successor_survival_transfer_of_boundaryMultiplicity
    (p d e : ℕ) (sourceRest targetRest sourceTail targetTail : List ℕ)
    (he : 0 < e)
    (hsourceStep : havelHakimiStep (p :: sourceRest) = d :: e :: sourceTail)
    (htargetStep : havelHakimiStep (p :: targetRest) = d :: e :: targetTail)
    (htargetDesc : (e :: targetTail).Pairwise (fun x y ↦ y ≤ x))
    (htargetBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (hmult : boundaryMultiplicity p e targetRest ≤
      boundaryMultiplicity p e sourceRest)
    (htargetSurvive : UndecrementedMax d e (e :: targetTail)) :
    UndecrementedMax d e (e :: sourceTail) := by
  have htCount : d < (e :: targetTail).count e :=
    count_gt_of_survival d e targetTail htargetDesc htargetBound htargetSurvive
  have hsCountEq := havelHakimiStep_count_eq_boundaryMultiplicity
    p e sourceRest he
  have htCountEq := havelHakimiStep_count_eq_boundaryMultiplicity
    p e targetRest he
  rw [hsourceStep] at hsCountEq
  rw [htargetStep] at htCountEq
  have hsTailCount : (e :: sourceTail).count e = sourceTail.count e + 1 := by
    simp
  have htTailCount : (e :: targetTail).count e = targetTail.count e + 1 := by
    simp
  have hcount : (e :: targetTail).count e ≤ (e :: sourceTail).count e := by
    by_cases hde : d = e
    · subst d
      simp at hsCountEq htCountEq
      omega
    · simp [hde] at hsCountEq htCountEq
      omega
  exact survival_monotone_of_count_dominance d e
    (e :: sourceTail) (e :: targetTail) hcount htCount htargetSurvive

/-- The exact remaining scalar relation on descending originals.  Proving this
from full prefix dominance and the shared successor prefix closes the v0.31
survival transfer via the preceding theorem. -/
def CommonHeadBoundaryMultiplicityMonotone : Prop :=
  ∀ (p d e : ℕ) (sourceRest targetRest sourceTail targetTail : List ℕ),
    0 < e →
    sourceRest.Pairwise (fun x y ↦ y ≤ x) →
    targetRest.Pairwise (fun x y ↦ y ≤ x) →
    DegreePrefixDominates (p :: sourceRest) (p :: targetRest) →
    havelHakimiStep (p :: sourceRest) = d :: e :: sourceTail →
    havelHakimiStep (p :: targetRest) = d :: e :: targetTail →
    boundaryMultiplicity p e targetRest ≤ boundaryMultiplicity p e sourceRest

end WrittenOnTheWallII.GraphConjecture61BoundaryMultiplicity
