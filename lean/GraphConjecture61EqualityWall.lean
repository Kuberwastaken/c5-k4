import GraphConjecture61FirstOvershootBarrier

/-!
# WOWII 61: closing the depth-two equality wall

Full prefix dominance rules out the sole bad successor-endpoint combination on
the two-prefix equality wall.  If the leading entries agree, this is the
existing saturation-transfer theorem.  Otherwise target survival saturates a
later prefix so strongly that it contradicts full prefix dominance directly.
-/

namespace WrittenOnTheWallII.GraphConjecture61EqualityWall

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
open WrittenOnTheWallII.GraphConjecture61PrefixSaturation
open WrittenOnTheWallII.GraphConjecture61DescendingSurvival
open WrittenOnTheWallII.GraphConjecture61FirstOvershootBarrier
open WrittenOnTheWallII.GraphConjecture61ResidualOvershoot

/-- Removing a common first entry preserves full prefix dominance on the
tails. -/
theorem degreePrefixDominates_tail_of_common_head
    (d : ℕ) (source target : List ℕ)
    (hdom : DegreePrefixDominates (d :: source) (d :: target)) :
    DegreePrefixDominates source target := by
  constructor
  · simpa using hdom.1
  · intro k hk
    have hlen : k + 1 ≤ (d :: source).length := by simp; omega
    have hp := hdom.2 (k + 1) hlen
    simpa [List.take_succ_cons] using hp

/-- In the unequal-head part of the equality wall, target endpoint survival
forces a later prefix contradiction. -/
theorem no_targetSurvival_of_unequal_heads_on_twoPrefix_equality
    (d e a b : ℕ) (sourceTail targetTail : List ℕ)
    (ha : 0 < a) (had : a < d)
    (htwoEq : a + b = d + e)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htargetDesc : (b :: targetTail).Pairwise (fun x y ↦ y ≤ x))
    (htBound : ∀ x ∈ b :: targetTail, x ≤ b)
    (hdom : DegreePrefixDominates
      (d :: e :: sourceTail) (a :: b :: targetTail)) :
    ¬ UndecrementedMax a b (b :: targetTail) := by
  intro hsurvive
  have htSat := take_eq_replicate_of_survival a b (b :: targetTail)
    htargetDesc htBound hsurvive
  have htLen : a + 1 ≤ (b :: targetTail).length := by
    obtain ⟨j, hj, -⟩ := List.mem_iff_getElem.mp hsurvive
    simp only [List.length_drop] at hj
    omega
  have hsLen : a + 2 ≤ (d :: e :: sourceTail).length := by
    have htOriginal : a + 2 ≤ (a :: b :: targetTail).length := by
      simp only [List.length_cons] at htLen ⊢
      omega
    rw [hdom.1]
    exact htOriginal
  have hp := hdom.2 (a + 2) hsLen
  have hsTailUpper := sum_le_length_mul_of_forall_le e
    ((e :: sourceTail).take (a + 1)) (by
      intro x hx
      exact hsBound x (List.mem_of_mem_take hx))
  have hsTakeLen : ((e :: sourceTail).take (a + 1)).length = a + 1 := by
    have hrest : a + 1 ≤ (e :: sourceTail).length := by
      simp only [List.length_cons] at hsLen ⊢
      omega
    exact List.length_take_of_le hrest
  have htPrefix : (a :: b :: targetTail).take (a + 2) =
      a :: List.replicate (a + 1) b := by
    simp only [List.take_succ_cons]
    exact congrArg (List.cons a) htSat
  have hsPrefix : (d :: e :: sourceTail).take (a + 2) =
      d :: (e :: sourceTail).take (a + 1) := by
    simp only [List.take_succ_cons]
  rw [htPrefix] at hp
  rw [hsPrefix] at hp
  simp only [List.sum_cons, List.sum_replicate] at hp
  rw [hsTakeLen] at hsTailUpper
  have hnsmul : (a + 1) • b = (a + 1) * b := by
    simp [Nat.add_mul]
  rw [hnsmul] at hp
  nlinarith

/-- Full depth-two cumulative monotonicity from ordinary initial prefix
dominance for descending positive lists. -/
theorem cumulativeHeadSum_two_of_degreePrefixDominates
    (d e a b : ℕ) (sourceTail targetTail : List ℕ)
    (hd : 0 < d) (he : 0 < e) (ha : 0 < a) (hb : 0 < b)
    (hsourceDesc : (e :: sourceTail).Pairwise (fun x y ↦ y ≤ x))
    (htargetDesc : (b :: targetTail).Pairwise (fun x y ↦ y ≤ x))
    (hdom : DegreePrefixDominates
      (d :: e :: sourceTail) (a :: b :: targetTail)) :
    cumulativeHeadSum 2 (a :: b :: targetTail) ≤
      cumulativeHeadSum 2 (d :: e :: sourceTail) := by
  have hsBound : ∀ x ∈ e :: sourceTail, x ≤ e := by
    intro x hx
    rcases (by simpa using hx : x = e ∨ x ∈ sourceTail) with rfl | hx
    · exact le_refl _
    · exact (List.pairwise_cons.mp hsourceDesc).1 x hx
  have htBound : ∀ x ∈ b :: targetTail, x ≤ b := by
    intro x hx
    rcases (by simpa using hx : x = b ∨ x ∈ targetTail) with rfl | hx
    · exact le_refl _
    · exact (List.pairwise_cons.mp htargetDesc).1 x hx
  have hfirst : a ≤ d := by
    have hp := hdom.2 1 (by simp)
    simpa using hp
  have htwo : a + b ≤ d + e := by
    have hp := hdom.2 2 (by simp)
    simpa using hp
  by_cases hstrict : a + b < d + e
  · exact cumulativeHeadSum_two_of_strict_twoPrefix d e a b sourceTail
      targetTail hd he hsBound htBound hstrict
  have htwoEq : a + b = d + e := by omega
  by_cases had : a = d
  · subst a
    have hbe : b = e := by omega
    subst b
    have htailDom := degreePrefixDominates_tail_of_common_head d
      (e :: sourceTail) (e :: targetTail) hdom
    exact cumulativeHeadSum_two_monotone_equalPrefix_of_degreePrefixDominates
      d e sourceTail targetTail hd he hsourceDesc htargetDesc htailDom
  · have hadStrict : a < d := by omega
    have htNotSurvive := no_targetSurvival_of_unequal_heads_on_twoPrefix_equality
      d e a b sourceTail targetTail ha hadStrict htwoEq hsBound htargetDesc
      htBound hdom
    have htHead := (successor_head_eq_pred_iff a b targetTail ha hb htBound).2
      htNotSurvive
    have hsLower := pred_second_le_successor_head d e sourceTail hd he hsBound
    change a + headDegree (havelHakimiStep (a :: b :: targetTail)) ≤
      d + headDegree (havelHakimiStep (d :: e :: sourceTail))
    rw [htHead]
    omega

/-- Hence full initial prefix dominance blocks residual-gap overshoot through
the first two Havel--Hakimi eliminations. -/
theorem residualGap_noOvershootThrough_two_of_degreePrefixDominates
    (d e a b : ℕ) (sourceTail targetTail : List ℕ)
    (hd : 0 < d) (he : 0 < e) (ha : 0 < a) (hb : 0 < b)
    (hsourceDesc : (e :: sourceTail).Pairwise (fun x y ↦ y ≤ x))
    (htargetDesc : (b :: targetTail).Pairwise (fun x y ↦ y ≤ x))
    (hdom : DegreePrefixDominates
      (d :: e :: sourceTail) (a :: b :: targetTail))
    (hsAdm :
      WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor 2
        (d :: e :: sourceTail))
    (htAdm :
      WrittenOnTheWallII.GraphConjecture61CumulativeCredit.AdmissibleFor 2
        (a :: b :: targetTail)) :
    ResidualGapDoesNotOvershootThrough 2
      (d :: e :: sourceTail) (a :: b :: targetTail) := by
  have hfirst : a ≤ d := by
    have hp := hdom.2 1 (by simp)
    simpa using hp
  intro j hj
  have hsJ := admissibleFor_mono hj hsAdm
  have htJ := admissibleFor_mono hj htAdm
  apply (cumulativeHeadOrder_iff_residualGap_noOvershoot hsJ htJ).1
  interval_cases j
  · simp [cumulativeHeadSum]
  · exact cumulativeHeadSum_one_of_first_le d a (e :: sourceTail)
      (b :: targetTail) hfirst
  · exact cumulativeHeadSum_two_of_degreePrefixDominates d e a b sourceTail
      targetTail hd he ha hb hsourceDesc htargetDesc hdom

end WrittenOnTheWallII.GraphConjecture61EqualityWall
