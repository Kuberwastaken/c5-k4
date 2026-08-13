import GraphConjecture61ThirdOvershootWall

/-!
# WOWII 61: successor-survival boundary and a quantifier correction

The broad transfer proposition named in the preceding rung is false without
descending original tails.  This file certifies an exact countermodel, then
proves that only one boundary-prefix sum inequality between the successors is
needed to transfer the survival bit.
-/

namespace WrittenOnTheWallII.GraphConjecture61SuccessorSurvivalBoundary

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
open WrittenOnTheWallII.GraphConjecture61PrefixSaturation
open WrittenOnTheWallII.GraphConjecture61DescendingSurvival
open WrittenOnTheWallII.GraphConjecture61ThirdOvershootWall

/-- Exact countermodel to the unrestricted transfer proposition.  The initial
tails are not descending; this is precisely the omitted premise. -/
theorem commonHeadSuccessorSurvivalTransfer_is_false :
    ¬ CommonHeadSuccessorSurvivalTransfer := by
  intro h
  have hdom : DegreePrefixDominates
      [1, 2, 2, 1, 2, 2] [1, 1, 2, 2, 2, 2] := by
    constructor
    · norm_num
    · intro k hk
      norm_num at hk
      interval_cases k <;> norm_num
  have hsStep : havelHakimiStep [1, 2, 2, 1, 2, 2] = [2, 2, 2, 1, 1] := by
    norm_num [havelHakimiStep, List.splitAt_eq, List.mergeSort]
  have htStep : havelHakimiStep [1, 1, 2, 2, 2, 2] = [2, 2, 2, 2, 0] := by
    norm_num [havelHakimiStep, List.splitAt_eq, List.mergeSort]
  have htSurvive : UndecrementedMax 2 2 [2, 2, 2, 0] := by
    norm_num [UndecrementedMax]
  have hsSurvive := h 1 2 2 [2, 2, 1, 2, 2] [1, 2, 2, 2, 2]
    [2, 1, 1] [2, 2, 0] hdom hsStep htStep htSurvive
  norm_num [UndecrementedMax] at hsSurvive

/-- A single saturated-boundary prefix inequality transfers survival.  Full
successor-prefix dominance is unnecessary. -/
theorem survival_transfer_of_boundaryPrefixSum
    (d e : ℕ) (sourceTail targetTail : List ℕ)
    (hsourceBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htargetDesc : (e :: targetTail).Pairwise (fun x y ↦ y ≤ x))
    (htargetBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (hlen : (e :: sourceTail).length = (e :: targetTail).length)
    (hboundary : ((e :: targetTail).take (d + 1)).sum ≤
      ((e :: sourceTail).take (d + 1)).sum)
    (htargetSurvive : UndecrementedMax d e (e :: targetTail)) :
    UndecrementedMax d e (e :: sourceTail) := by
  have htSat := take_eq_replicate_of_survival d e (e :: targetTail)
    htargetDesc htargetBound htargetSurvive
  have htLen : d + 1 ≤ (e :: targetTail).length := by
    obtain ⟨j, hj, -⟩ := List.mem_iff_getElem.mp htargetSurvive
    simp only [List.length_drop] at hj
    omega
  have hsLen : d + 1 ≤ (e :: sourceTail).length := by
    rw [hlen]
    exact htLen
  have hsTakeLen : ((e :: sourceTail).take (d + 1)).length = d + 1 :=
    List.length_take_of_le hsLen
  have hsTakeBound : ∀ x ∈ (e :: sourceTail).take (d + 1), x ≤ e := by
    intro x hx
    exact hsourceBound x (List.mem_of_mem_take hx)
  have htargetSum : ((e :: targetTail).take (d + 1)).sum = (d + 1) • e := by
    rw [htSat]
    simp
  have hsUpper := sum_le_length_mul_of_forall_le e
    ((e :: sourceTail).take (d + 1)) hsTakeBound
  have hnsmul : (d + 1) • e = (d + 1) * e := by simp [Nat.add_mul]
  have hsSat : ((e :: sourceTail).take (d + 1)).length * e ≤
      ((e :: sourceTail).take (d + 1)).sum := by
    rw [hsTakeLen, ← hnsmul, ← htargetSum]
    exact hboundary
  have hsEq := eq_replicate_of_length_mul_le_sum_of_forall_le e
    ((e :: sourceTail).take (d + 1)) hsTakeBound hsSat
  rw [hsTakeLen] at hsEq
  have hsCount := count_gt_of_saturated_prefix d e (e :: sourceTail) hsEq
  exact undecrementedMax_of_count_gt d e (e :: sourceTail) hsCount

/-- Corrected live bridge: descending common-head originals need only lift one
specific boundary-prefix sum inequality to their shared-prefix successors. -/
def CommonHeadSuccessorBoundaryPrefixLift : Prop :=
  ∀ (p d e : ℕ) (sourceRest targetRest sourceTail targetTail : List ℕ),
    sourceRest.Pairwise (fun x y ↦ y ≤ x) →
    targetRest.Pairwise (fun x y ↦ y ≤ x) →
    DegreePrefixDominates (p :: sourceRest) (p :: targetRest) →
    havelHakimiStep (p :: sourceRest) = d :: e :: sourceTail →
    havelHakimiStep (p :: targetRest) = d :: e :: targetTail →
    ((e :: targetTail).take (d + 1)).sum ≤
      ((e :: sourceTail).take (d + 1)).sum

end WrittenOnTheWallII.GraphConjecture61SuccessorSurvivalBoundary
