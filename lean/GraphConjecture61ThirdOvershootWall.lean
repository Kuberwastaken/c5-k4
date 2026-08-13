import GraphConjecture61EqualityWall

/-!
# WOWII 61: exact first wall for a depth-three overshoot

With full depth-two order available, a depth-three failure in the shared
successor-prefix class is forced onto a zero-credit wall: the original first
heads agree, the first two cumulative sums tie, and the sole bad second-step
survival combination occurs.  This isolates the next tail-transfer lemma.
-/

namespace WrittenOnTheWallII.GraphConjecture61ThirdOvershootWall

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
open WrittenOnTheWallII.GraphConjecture61PrefixSaturation
open WrittenOnTheWallII.GraphConjecture61FirstOvershootBarrier
open WrittenOnTheWallII.GraphConjecture61EqualityWall
open WrittenOnTheWallII.GraphConjecture61ThirdHeadCredit

/-- Exact missing lift: after removing a common original head, full tail-prefix
dominance should transfer the second-step endpoint survival flag between the
canonical successors when those successors share their first two entries. -/
def CommonHeadSuccessorSurvivalTransfer : Prop :=
  ∀ (p d e : ℕ) (sourceRest targetRest sourceTail targetTail : List ℕ),
    DegreePrefixDominates (p :: sourceRest) (p :: targetRest) →
    havelHakimiStep (p :: sourceRest) = d :: e :: sourceTail →
    havelHakimiStep (p :: targetRest) = d :: e :: targetTail →
    UndecrementedMax d e (e :: targetTail) →
    UndecrementedMax d e (e :: sourceTail)

/-- A depth-three failure forces the precise zero-bank/bad-flag wall. -/
theorem depthThree_failure_forces_zeroBank_badFlag_and_commonHead
    (p q a b d e : ℕ)
    (sourceRest targetRest sourceTail targetTail : List ℕ)
    (hp : 0 < p) (hq : 0 < q) (ha : 0 < a) (hb : 0 < b)
    (hd : 0 < d) (he : 0 < e)
    (hsourceDesc : (q :: sourceRest).Pairwise (fun x y ↦ y ≤ x))
    (htargetDesc : (b :: targetRest).Pairwise (fun x y ↦ y ≤ x))
    (hdom : DegreePrefixDominates
      (p :: q :: sourceRest) (a :: b :: targetRest))
    (hsourceStep : havelHakimiStep (p :: q :: sourceRest) =
      d :: e :: sourceTail)
    (htargetStep : havelHakimiStep (a :: b :: targetRest) =
      d :: e :: targetTail)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (hfail : ¬ cumulativeHeadSum 3 (a :: b :: targetRest) ≤
      cumulativeHeadSum 3 (p :: q :: sourceRest)) :
    cumulativeHeadSum 2 (a :: b :: targetRest) =
        cumulativeHeadSum 2 (p :: q :: sourceRest) ∧
      p = a ∧
      ¬ UndecrementedMax d e (e :: sourceTail) ∧
      UndecrementedMax d e (e :: targetTail) := by
  have htwo := cumulativeHeadSum_two_of_degreePrefixDominates p q a b
    sourceRest targetRest hp hq ha hb hsourceDesc htargetDesc hdom
  have htSurvive : UndecrementedMax d e (e :: targetTail) := by
    by_contra ht
    have htHead := (successor_head_eq_pred_iff d e targetTail hd he htBound).2 ht
    have hsLower := pred_second_le_successor_head d e sourceTail hd he hsBound
    have hthird : thirdHead (a :: b :: targetRest) ≤
        thirdHead (p :: q :: sourceRest) := by
      simp only [thirdHead, hsourceStep, htargetStep]
      rw [htHead]
      exact hsLower
    apply hfail
    rw [cumulativeHeadSum_three, cumulativeHeadSum_three]
    omega
  have hsNotSurvive : ¬ UndecrementedMax d e (e :: sourceTail) := by
    intro hs
    have hsHead := (successor_head_eq_second_iff d e sourceTail he hsBound).2 hs
    have htUpper := successor_head_le_second d e targetTail htBound
    have hthird : thirdHead (a :: b :: targetRest) ≤
        thirdHead (p :: q :: sourceRest) := by
      simp only [thirdHead, hsourceStep, htargetStep]
      rw [hsHead]
      exact htUpper
    apply hfail
    rw [cumulativeHeadSum_three, cumulativeHeadSum_three]
    omega
  have hiff := cumulativeHeadSum_three_iff_two_strict_of_bad_secondStep_flag
    (p :: q :: sourceRest) (a :: b :: targetRest) d e sourceTail targetTail
    hsourceStep htargetStep hd he hsBound htBound hsNotSurvive htSurvive
  have hnotStrict : ¬ cumulativeHeadSum 2 (a :: b :: targetRest) <
      cumulativeHeadSum 2 (p :: q :: sourceRest) := by
    intro hstrict
    exact hfail (hiff.2 hstrict)
  have htwoEq : cumulativeHeadSum 2 (a :: b :: targetRest) =
      cumulativeHeadSum 2 (p :: q :: sourceRest) := by omega
  have hpa : p = a := by
    change a + headDegree (havelHakimiStep (a :: b :: targetRest)) =
      p + headDegree (havelHakimiStep (p :: q :: sourceRest)) at htwoEq
    rw [hsourceStep, htargetStep] at htwoEq
    simp only [headDegree] at htwoEq
    omega
  exact ⟨htwoEq, hpa, hsNotSurvive, htSurvive⟩

/-- The isolated survival-transfer lemma closes cumulative order through depth
three in the shared-successor-prefix class. -/
theorem cumulativeHeadSum_three_of_commonHead_survivalTransfer
    (p q a b d e : ℕ)
    (sourceRest targetRest sourceTail targetTail : List ℕ)
    (hp : 0 < p) (hq : 0 < q) (ha : 0 < a) (hb : 0 < b)
    (hd : 0 < d) (he : 0 < e)
    (hsourceDesc : (q :: sourceRest).Pairwise (fun x y ↦ y ≤ x))
    (htargetDesc : (b :: targetRest).Pairwise (fun x y ↦ y ≤ x))
    (hdom : DegreePrefixDominates
      (p :: q :: sourceRest) (a :: b :: targetRest))
    (hsourceStep : havelHakimiStep (p :: q :: sourceRest) =
      d :: e :: sourceTail)
    (htargetStep : havelHakimiStep (a :: b :: targetRest) =
      d :: e :: targetTail)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (htransfer : UndecrementedMax d e (e :: targetTail) →
      UndecrementedMax d e (e :: sourceTail)) :
    cumulativeHeadSum 3 (a :: b :: targetRest) ≤
      cumulativeHeadSum 3 (p :: q :: sourceRest) := by
  have htwo := cumulativeHeadSum_two_of_degreePrefixDominates p q a b
    sourceRest targetRest hp hq ha hb hsourceDesc htargetDesc hdom
  exact cumulativeHeadSum_three_of_secondStep_survival
    (p :: q :: sourceRest) (a :: b :: targetRest) d e sourceTail targetTail
    hsourceStep htargetStep hd he hsBound htBound htransfer htwo

end WrittenOnTheWallII.GraphConjecture61ThirdOvershootWall
