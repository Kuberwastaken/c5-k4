import GraphConjecture61PrefixSaturation

/-!
# WOWII 61: descending survival implies prefix saturation

If a descending list bounded by `e` contains an `e` after the first `d`
entries, then every entry in its `(d+1)`-prefix equals `e`.  This closes the
last indexing gap in the equal-top-two two-step comparison.
-/

namespace WrittenOnTheWallII.GraphConjecture61DescendingSurvival

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
open WrittenOnTheWallII.GraphConjecture61PrefixSaturation

/-- Every entry before a surviving maximum in a descending list is at least
that maximum. -/
theorem take_forall_ge_of_mem_drop_of_pairwise
    (d e : ℕ) (xs : List ℕ)
    (hdesc : xs.Pairwise (fun a b ↦ b ≤ a))
    (hsurvive : e ∈ xs.drop d) :
    ∀ x ∈ xs.take (d + 1), e ≤ x := by
  obtain ⟨j, hj, hje⟩ := List.mem_iff_getElem.mp hsurvive
  intro x hx
  obtain ⟨i, hi, hix⟩ := List.mem_iff_getElem.mp hx
  have hiBound : i < d + 1 := by
    have := hi
    simp only [List.length_take] at this
    omega
  have habs : d + j < xs.length := by
    have hdropLen := hj
    simp only [List.length_drop] at hdropLen
    omega
  have hiXs : i < xs.length := by omega
  have hleIndex : i ≤ d + j := by omega
  have hrel := hdesc.rel_get_of_le
    (a := ⟨i, hiXs⟩) (b := ⟨d + j, habs⟩) hleIndex
  have htakeGet : (xs.take (d + 1))[i] = xs[i] :=
    List.getElem_take (xs := xs) (j := d + 1) (i := i)
  have hdropGet : (xs.drop d)[j] = xs[d + j] :=
    List.getElem_drop (xs := xs) (i := d) (j := j)
  rw [htakeGet] at hix
  rw [hdropGet] at hje
  simpa [hix, hje] using hrel

/-- Exact boundary-prefix saturation from descending survival and the maximum
upper bound. -/
theorem take_eq_replicate_of_survival
    (d e : ℕ) (xs : List ℕ)
    (hdesc : xs.Pairwise (fun a b ↦ b ≤ a))
    (hbound : ∀ x ∈ xs, x ≤ e)
    (hsurvive : UndecrementedMax d e xs) :
    xs.take (d + 1) = List.replicate (d + 1) e := by
  have hlen : d + 1 ≤ xs.length := by
    obtain ⟨j, hj, -⟩ := List.mem_iff_getElem.mp hsurvive
    simp only [List.length_drop] at hj
    omega
  apply prefix_eq_replicate_of_forall_ge_le d e xs hlen
  · intro x hx
    exact hbound x (List.mem_of_mem_take hx)
  · exact take_forall_ge_of_mem_drop_of_pairwise d e xs hdesc hsurvive

/-- Full equal-top-two two-step monotonicity from ordinary weak prefix
dominance and descending tails. No survival or saturation premise remains. -/
theorem cumulativeHeadSum_two_monotone_equalPrefix_of_degreePrefixDominates
    (d e : ℕ) (sourceTail targetTail : List ℕ)
    (hd : 0 < d) (he : 0 < e)
    (hsourceDesc : (e :: sourceTail).Pairwise (fun a b ↦ b ≤ a))
    (htargetDesc : (e :: targetTail).Pairwise (fun a b ↦ b ≤ a))
    (hdom : DegreePrefixDominates (e :: sourceTail) (e :: targetTail)) :
    cumulativeHeadSum 2 (d :: e :: targetTail) ≤
      cumulativeHeadSum 2 (d :: e :: sourceTail) := by
  have hsBound : ∀ x ∈ e :: sourceTail, x ≤ e := by
    intro x hx
    simp only [List.mem_cons] at hx
    rcases hx with rfl | hx
    · exact le_refl _
    · exact (List.pairwise_cons.mp hsourceDesc).1 x hx
  have htBound : ∀ x ∈ e :: targetTail, x ≤ e := by
    intro x hx
    simp only [List.mem_cons] at hx
    rcases hx with rfl | hx
    · exact le_refl _
    · exact (List.pairwise_cons.mp htargetDesc).1 x hx
  apply cumulativeHeadSum_two_monotone_equalPrefix_of_survival
    d e sourceTail targetTail hd he hsBound htBound
  intro htSurvive
  have htSat := take_eq_replicate_of_survival d e
    (e :: targetTail) htargetDesc htBound htSurvive
  have hlen : d + 1 ≤ (e :: sourceTail).length := by
    have htLen : d + 1 ≤ (e :: targetTail).length := by
      obtain ⟨j, hj, -⟩ := List.mem_iff_getElem.mp htSurvive
      simp only [List.length_drop] at hj
      omega
    rw [hdom.1]
    exact htLen
  have hsCount := source_count_gt_of_degreePrefixDominates_of_target_saturated
    d e (e :: sourceTail) (e :: targetTail) hdom hsBound htSat hlen
  exact undecrementedMax_of_count_gt d e (e :: sourceTail) hsCount

end WrittenOnTheWallII.GraphConjecture61DescendingSurvival
