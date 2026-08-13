import GraphConjecture61SecondHeadCriterion

/-!
# WOWII 61: survival-flag monotonicity

In the equal-top-two case the second canonical head is controlled by one bit:
whether a maximum survives the decrement boundary.  This file proves the
direct multiplicity criterion that orders this bit and records a graphical
countermodel showing that equality of the first two entries alone is not
enough.
-/

namespace WrittenOnTheWallII.GraphConjecture61SurvivalFlag

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion

/-- Boundary-maximum multiplicity orders the survival flag. -/
theorem survival_monotone_of_count
    (d e : ℕ) (sourceRest targetRest : List ℕ)
    (hsource : d < sourceRest.count e)
    (_htarget : d < targetRest.count e) :
    UndecrementedMax d e targetRest →
      UndecrementedMax d e sourceRest := by
  intro _
  exact undecrementedMax_of_count_gt d e sourceRest hsource

/-- A convenient ordered-count form: target saturation past the boundary and
target-to-source count dominance force source survival. -/
theorem survival_monotone_of_count_dominance
    (d e : ℕ) (sourceRest targetRest : List ℕ)
    (hcount : targetRest.count e ≤ sourceRest.count e)
    (htargetCount : d < targetRest.count e) :
    UndecrementedMax d e targetRest →
      UndecrementedMax d e sourceRest := by
  exact survival_monotone_of_count d e sourceRest targetRest
    (lt_of_lt_of_le htargetCount hcount) htargetCount

/-- Equal-top-two two-step monotonicity after the boundary multiplicity has
been ordered. -/
theorem cumulativeHeadSum_two_monotone_equalPrefix_of_count_dominance
    (d e : ℕ) (sourceTail targetTail : List ℕ)
    (hd : 0 < d) (he : 0 < e)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (hcount : (e :: targetTail).count e ≤
      (e :: sourceTail).count e)
    (htargetCount : d < (e :: targetTail).count e) :
    cumulativeHeadSum 2 (d :: e :: targetTail) ≤
      cumulativeHeadSum 2 (d :: e :: sourceTail) := by
  apply cumulativeHeadSum_two_monotone_equalPrefix_of_survival
    d e sourceTail targetTail hd he hsBound htBound
  exact survival_monotone_of_count_dominance d e
    (e :: sourceTail) (e :: targetTail) hcount htargetCount

/-- Equality of the first two entries alone does not order survival, even for
the graphical degree lists of `P4` and `C4`. -/
theorem equal_top_two_alone_does_not_order_survival :
    UndecrementedMax 2 2 ([2, 2, 2] : List ℕ) ∧
      ¬ UndecrementedMax 2 2 ([2, 1, 1] : List ℕ) := by
  simp [UndecrementedMax]

/-- The same countermodel reaches opposite exact endpoints for the second
canonical head. -/
theorem equal_top_two_endpoint_countermodel :
    headDegree (havelHakimiStep ([2, 2, 2, 2] : List ℕ)) = 2 ∧
      headDegree (havelHakimiStep ([2, 2, 1, 1] : List ℕ)) = 1 := by
  norm_num [headDegree, havelHakimiStep, List.splitAt_eq, List.mergeSort]

end WrittenOnTheWallII.GraphConjecture61SurvivalFlag
