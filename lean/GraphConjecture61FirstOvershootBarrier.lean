import GraphConjecture61ResidualOvershoot

/-!
# WOWII 61: the first residual-overshoot barrier

The first trajectory step is funded directly by prefix-one dominance.  At the
second step, strict dominance of the original two-entry prefix pays for the
only possible one-unit loss in the source successor head.  Thus a first
overshoot at depth two can occur only on the exact two-prefix equality wall.
-/

namespace WrittenOnTheWallII.GraphConjecture61FirstOvershootBarrier

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
open WrittenOnTheWallII.GraphConjecture61FundedTrajectory
open WrittenOnTheWallII.GraphConjecture61ResidualOvershoot

/-- A descending positive-head list loses at most one from its second entry
when exposing the successor head. -/
theorem pred_second_le_successor_head
    (d e : ℕ) (tail : List ℕ) (hd : 0 < d) (he : 0 < e)
    (hbound : ∀ x ∈ e :: tail, x ≤ e) :
    e - 1 ≤ headDegree (havelHakimiStep (d :: e :: tail)) := by
  by_cases hsurvive : UndecrementedMax d e (e :: tail)
  · have hhead :=
      (successor_head_eq_second_iff d e tail he hbound).2 hsurvive
    omega
  · rw [(successor_head_eq_pred_iff d e tail hd he hbound).2 hsurvive]

/-- Prefix-one dominance always funds the first exposed head. -/
theorem cumulativeHeadSum_one_of_first_le
    (d a : ℕ) (sourceTail targetTail : List ℕ) (hfirst : a ≤ d) :
    cumulativeHeadSum 1 (a :: targetTail) ≤
      cumulativeHeadSum 1 (d :: sourceTail) := by
  simpa [cumulativeHeadSum, headDegree] using hfirst

/-- Main depth-two barrier.  Strict source advantage on the first two original
degrees covers even the worst endpoint combination in the successor heads. -/
theorem cumulativeHeadSum_two_of_strict_twoPrefix
    (d e a b : ℕ) (sourceTail targetTail : List ℕ)
    (hd : 0 < d) (he : 0 < e)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ b :: targetTail, x ≤ b)
    (htwoStrict : a + b < d + e) :
    cumulativeHeadSum 2 (a :: b :: targetTail) ≤
      cumulativeHeadSum 2 (d :: e :: sourceTail) := by
  have hsLower := pred_second_le_successor_head d e sourceTail hd he hsBound
  have htUpper := successor_head_le_second a b targetTail htBound
  change a + headDegree (havelHakimiStep (a :: b :: targetTail)) ≤
    d + headDegree (havelHakimiStep (d :: e :: sourceTail))
  omega

/-- Consequently no residual-gap overshoot is possible through depth two in
the strict two-prefix class. -/
theorem residualGap_noOvershootThrough_two_of_strict_twoPrefix
    (d e a b : ℕ) (sourceTail targetTail : List ℕ)
    (hd : 0 < d) (he : 0 < e)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ b :: targetTail, x ≤ b)
    (hfirst : a ≤ d) (htwoStrict : a + b < d + e)
    (hsAdm :
      WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor 2
        (d :: e :: sourceTail))
    (htAdm :
      WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor 2
        (a :: b :: targetTail)) :
    ResidualGapDoesNotOvershootThrough 2
      (d :: e :: sourceTail) (a :: b :: targetTail) := by
  intro j hj
  have hsJ := admissibleFor_mono hj hsAdm
  have htJ := admissibleFor_mono hj htAdm
  apply (cumulativeHeadOrder_iff_residualGap_noOvershoot hsJ htJ).1
  interval_cases j
  · simp [cumulativeHeadSum]
  · exact cumulativeHeadSum_one_of_first_le d a (e :: sourceTail)
      (b :: targetTail) hfirst
  · exact cumulativeHeadSum_two_of_strict_twoPrefix d e a b sourceTail
      targetTail hd he hsBound htBound htwoStrict

/-- Exact localization of any first depth-two failure: the original two-entry
prefix comparison must lie on its equality wall. -/
theorem depthTwo_failure_forces_prefix_equalities
    (d e a b : ℕ) (sourceTail targetTail : List ℕ)
    (hd : 0 < d) (he : 0 < e)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ b :: targetTail, x ≤ b)
    (htwo : a + b ≤ d + e)
    (hfail : ¬ cumulativeHeadSum 2 (a :: b :: targetTail) ≤
      cumulativeHeadSum 2 (d :: e :: sourceTail)) :
    a + b = d + e := by
  by_contra hne
  have hstrict : a + b < d + e := by omega
  exact hfail (cumulativeHeadSum_two_of_strict_twoPrefix d e a b sourceTail
    targetTail hd he hsBound htBound hstrict)

/-- The equality wall cannot be resolved from the first two original entries
alone, even for graphical sequences.  An edge plus two isolates and a perfect
matching have equal top-two entries, but the matching exposes one more head. -/
theorem topTwoPrefixData_alone_does_not_block_depthTwo_failure :
    (List.take 1 [1, 1, 1, 1]).sum = (List.take 1 [1, 1, 0, 0]).sum ∧
      (List.take 2 [1, 1, 1, 1]).sum = (List.take 2 [1, 1, 0, 0]).sum ∧
      ¬ cumulativeHeadSum 2 [1, 1, 1, 1] ≤
        cumulativeHeadSum 2 [1, 1, 0, 0] := by
  norm_num [cumulativeHeadSum, headDegree, havelHakimiStep,
    List.splitAt_eq, List.mergeSort]

end WrittenOnTheWallII.GraphConjecture61FirstOvershootBarrier
