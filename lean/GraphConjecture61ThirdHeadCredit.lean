import GraphConjecture61DescendingSurvival

/-!
# WOWII 61: third-head credit and the exact second-step flag split

Successor-prefix dominance is false, so the three-step comparison must not
silently assume it.  This file instead records the exact local obstruction.
After the first two heads have been compared, the third head is controlled by
the endpoint-survival flag in each successor state.  Three of the four flag
combinations are monotone.  In the sole bad combination the target gains
exactly one, so one unit of previously banked two-head surplus is necessary
and sufficient.
-/

namespace WrittenOnTheWallII.GraphConjecture61ThirdHeadCredit

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion

/-- The head exposed after two Havel--Hakimi reductions. -/
def thirdHead (s : List ℕ) : ℕ :=
  headDegree (havelHakimiStep (havelHakimiStep s))

theorem cumulativeHeadSum_three (s : List ℕ) :
    cumulativeHeadSum 3 s = cumulativeHeadSum 2 s + thirdHead s := by
  simp [cumulativeHeadSum, thirdHead, Nat.add_assoc]

/-- Exact arithmetic form of the credit rule at the third head. -/
theorem cumulativeHeadSum_three_iff_bankedCredit
    (source target : List ℕ)
    (hbank : cumulativeHeadSum 2 target ≤ cumulativeHeadSum 2 source) :
    cumulativeHeadSum 3 target ≤ cumulativeHeadSum 3 source ↔
      thirdHead target ≤
        cumulativeHeadSum 2 source - cumulativeHeadSum 2 target + thirdHead source := by
  rw [cumulativeHeadSum_three, cumulativeHeadSum_three]
  omega

/-- If the target's second-step endpoint survives only when the source's does,
then its third head cannot exceed the source's third head. -/
theorem thirdHead_le_of_secondStep_survival
    (source target : List ℕ) (d e : ℕ) (sourceTail targetTail : List ℕ)
    (hsourceStep : havelHakimiStep source = d :: e :: sourceTail)
    (htargetStep : havelHakimiStep target = d :: e :: targetTail)
    (hd : 0 < d) (he : 0 < e)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (hsurvive : UndecrementedMax d e (e :: targetTail) →
      UndecrementedMax d e (e :: sourceTail)) :
    thirdHead target ≤ thirdHead source := by
  have h := cumulativeHeadSum_two_monotone_equalPrefix_of_survival
    d e sourceTail targetTail hd he hsBound htBound hsurvive
  change d + headDegree (havelHakimiStep (d :: e :: targetTail)) ≤
    d + headDegree (havelHakimiStep (d :: e :: sourceTail)) at h
  simp only [thirdHead, hsourceStep, htargetStep]
  omega

/-- The three good endpoint-flag combinations require no extra credit beyond
the weak two-head comparison. -/
theorem cumulativeHeadSum_three_of_secondStep_survival
    (source target : List ℕ) (d e : ℕ) (sourceTail targetTail : List ℕ)
    (hsourceStep : havelHakimiStep source = d :: e :: sourceTail)
    (htargetStep : havelHakimiStep target = d :: e :: targetTail)
    (hd : 0 < d) (he : 0 < e)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (hsurvive : UndecrementedMax d e (e :: targetTail) →
      UndecrementedMax d e (e :: sourceTail))
    (hbank : cumulativeHeadSum 2 target ≤ cumulativeHeadSum 2 source) :
    cumulativeHeadSum 3 target ≤ cumulativeHeadSum 3 source := by
  rw [cumulativeHeadSum_three, cumulativeHeadSum_three]
  have hthird := thirdHead_le_of_secondStep_survival source target d e
    sourceTail targetTail hsourceStep htargetStep hd he hsBound htBound hsurvive
  omega

/-- In the unique bad flag combination (target survives, source does not), the
target's third head is exactly one larger.  Consequently the three-head order
holds exactly when the earlier two-head comparison has strict surplus. -/
theorem cumulativeHeadSum_three_iff_two_strict_of_bad_secondStep_flag
    (source target : List ℕ) (d e : ℕ) (sourceTail targetTail : List ℕ)
    (hsourceStep : havelHakimiStep source = d :: e :: sourceTail)
    (htargetStep : havelHakimiStep target = d :: e :: targetTail)
    (hd : 0 < d) (he : 0 < e)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (hsourceDoesNotSurvive : ¬ UndecrementedMax d e (e :: sourceTail))
    (htargetSurvives : UndecrementedMax d e (e :: targetTail)) :
    cumulativeHeadSum 3 target ≤ cumulativeHeadSum 3 source ↔
      cumulativeHeadSum 2 target < cumulativeHeadSum 2 source := by
  have hsHead := (successor_head_eq_pred_iff d e sourceTail hd he hsBound).2
    hsourceDoesNotSurvive
  have htHead := (successor_head_eq_second_iff d e targetTail he htBound).2
    htargetSurvives
  rw [cumulativeHeadSum_three, cumulativeHeadSum_three]
  simp only [thirdHead, hsourceStep, htargetStep]
  rw [hsHead, htHead]
  omega

/-- A graphical countermodel to extending a merely weak two-head comparison
to three heads: `(2,1,1)` is the path on three vertices, while six ones are a
matching of three edges.  Their first two cumulative heads tie at `2`, but the
matching has cumulative third head `3` against `2`. -/
theorem weak_two_head_order_does_not_imply_three_head_order :
    cumulativeHeadSum 2 [1, 1, 1, 1, 1, 1] ≤ cumulativeHeadSum 2 [2, 1, 1] ∧
      ¬ cumulativeHeadSum 3 [1, 1, 1, 1, 1, 1] ≤ cumulativeHeadSum 3 [2, 1, 1] := by
  norm_num [cumulativeHeadSum, headDegree, havelHakimiStep, List.splitAt_eq,
    List.mergeSort]

end WrittenOnTheWallII.GraphConjecture61ThirdHeadCredit
