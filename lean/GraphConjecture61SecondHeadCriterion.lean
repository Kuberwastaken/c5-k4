import FormalConjecturesUtil

/-!
# WOWII 61: exact second-head endpoint criterion

For a descending positive-head list, the successor head equals the original
second entry exactly when a copy of that maximum survives beyond the decrement
boundary.  Otherwise it equals one less.
-/

namespace WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion

open SimpleGraph

def headDegree : List ℕ → ℕ
  | [] => 0
  | d :: _ => d

def cumulativeHeadSum : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => headDegree s + cumulativeHeadSum k (havelHakimiStep s)

def UndecrementedMax (d e : ℕ) (rest : List ℕ) : Prop :=
  e ∈ rest.drop d

/-- More than `d` copies of the maximum guarantee that one survives beyond
the decrement boundary. -/
theorem undecrementedMax_of_count_gt
    (d e : ℕ) (rest : List ℕ) (hcount : d < rest.count e) :
    UndecrementedMax d e rest := by
  have hsplit := congrArg (fun l : List ℕ ↦ l.count e)
    (List.take_append_drop d rest)
  simp only [List.count_append] at hsplit
  have hc : (rest.take d).count e ≤ (rest.take d).length :=
    List.count_le_length
  have htake : (rest.take d).count e ≤ d :=
    hc.trans (List.length_take_le _ _)
  have hdrop : 0 < (rest.drop d).count e := by omega
  simpa using (List.count_pos_iff.1 hdrop)

theorem mem_havelHakimiStep_origin
    {d : ℕ} {rest : List ℕ} {y : ℕ}
    (hy : y ∈ havelHakimiStep (d :: rest)) :
    (∃ x ∈ rest.take d, y = x - 1) ∨ y ∈ rest.drop d := by
  let a := rest.take d
  let b := rest.drop d
  have hp := List.mergeSort_perm (a.map (· - 1) ++ b) (· ≥ ·)
  have hm : y ∈ a.map (· - 1) ++ b := by
    apply (hp.mem_iff).1
    simpa [havelHakimiStep, a, b, List.splitAt_eq] using hy
  rw [List.mem_append] at hm
  rcases hm with hm | hm
  · rw [List.mem_map] at hm
    obtain ⟨x, hx, rfl⟩ := hm
    exact Or.inl ⟨x, hx, rfl⟩
  · exact Or.inr hm

theorem successor_nonempty (d e : ℕ) (tail : List ℕ) :
    havelHakimiStep (d :: e :: tail) ≠ [] := by
  intro hnil
  have hlen := havelHakimiStep_length_cons d (e :: tail)
  rw [hnil] at hlen
  simp at hlen

theorem successor_head_mem (d e : ℕ) (tail : List ℕ) :
    headDegree (havelHakimiStep (d :: e :: tail)) ∈
      havelHakimiStep (d :: e :: tail) := by
  have hne := successor_nonempty d e tail
  cases h : havelHakimiStep (d :: e :: tail) with
  | nil => exact (hne h).elim
  | cons y ys => simp [headDegree]

theorem successor_head_dominates
    (d e : ℕ) (tail : List ℕ) {y : ℕ}
    (hy : y ∈ havelHakimiStep (d :: e :: tail)) :
    y ≤ headDegree (havelHakimiStep (d :: e :: tail)) := by
  have hne := successor_nonempty d e tail
  cases h : havelHakimiStep (d :: e :: tail) with
  | nil => exact (hne h).elim
  | cons z zs =>
      change y ≤ z
      rw [h] at hy
      have hp := List.pairwise_mergeSort' (fun a b : ℕ ↦ a ≥ b)
        (((e :: tail).take d).map (· - 1) ++ (e :: tail).drop d)
      have hmerge :
          ((((e :: tail).take d).map (· - 1) ++ (e :: tail).drop d).mergeSort
            (· ≥ ·)) = z :: zs := by
        rw [← h]
        simp [havelHakimiStep, List.splitAt_eq]
      rw [hmerge] at hp
      simp at hy
      rcases hy with rfl | hy
      · exact le_refl _
      · exact (List.pairwise_cons.1 hp).1 y hy

/-- Exact upper bound inherited from a descending original tail. -/
theorem successor_head_le_second
    (d e : ℕ) (tail : List ℕ)
    (hbound : ∀ x ∈ e :: tail, x ≤ e) :
    headDegree (havelHakimiStep (d :: e :: tail)) ≤ e := by
  have hh := successor_head_mem d e tail
  rcases mem_havelHakimiStep_origin hh with ⟨x, hx, heq⟩ | hx
  · rw [heq]
    exact (Nat.sub_le x 1).trans (hbound x (List.mem_of_mem_take hx))
  · exact hbound _ (List.mem_of_mem_drop hx)

/-- Exact upper-endpoint criterion. -/
theorem successor_head_eq_second_iff
    (d e : ℕ) (tail : List ℕ) (he : 0 < e)
    (hbound : ∀ x ∈ e :: tail, x ≤ e) :
    headDegree (havelHakimiStep (d :: e :: tail)) = e ↔
      UndecrementedMax d e (e :: tail) := by
  constructor
  · intro heq
    have hh := successor_head_mem d e tail
    rw [heq] at hh
    rcases mem_havelHakimiStep_origin hh with ⟨x, hx, hxe⟩ | hx
    · have hxBound := hbound x (List.mem_of_mem_take hx)
      omega
    · exact hx
  · intro hsurvive
    have heMem : e ∈ havelHakimiStep (d :: e :: tail) := by
      let a := (e :: tail).take d
      let b := (e :: tail).drop d
      have hp := List.mergeSort_perm (a.map (· - 1) ++ b) (· ≥ ·)
      have hm : e ∈ (a.map (· - 1) ++ b).mergeSort (· ≥ ·) := by
        exact (hp.mem_iff).2 (by
          rw [List.mem_append]
          exact Or.inr hsurvive)
      simpa [havelHakimiStep, a, b, List.splitAt_eq] using hm
    apply Nat.le_antisymm (successor_head_le_second d e tail hbound)
    exact successor_head_dominates d e tail heMem

/-- Exact lower-endpoint criterion for positive `e`. -/
theorem successor_head_eq_pred_iff
    (d e : ℕ) (tail : List ℕ) (hd : 0 < d) (he : 0 < e)
    (hbound : ∀ x ∈ e :: tail, x ≤ e) :
    headDegree (havelHakimiStep (d :: e :: tail)) = e - 1 ↔
      ¬ UndecrementedMax d e (e :: tail) := by
  have hlower : e - 1 ≤ headDegree (havelHakimiStep (d :: e :: tail)) := by
    have heTake : e ∈ (e :: tail).take d := by
      cases d with
      | zero => omega
      | succ d => simp
    have heStep : e - 1 ∈ havelHakimiStep (d :: e :: tail) := by
      let a := (e :: tail).take d
      let b := (e :: tail).drop d
      have hp := List.mergeSort_perm (a.map (· - 1) ++ b) (· ≥ ·)
      have hm : e - 1 ∈ (a.map (· - 1) ++ b).mergeSort (· ≥ ·) := by
        exact (hp.mem_iff).2 (by
          rw [List.mem_append]
          exact Or.inl (List.mem_map.2 ⟨e, heTake, rfl⟩))
      simpa [havelHakimiStep, a, b, List.splitAt_eq] using hm
    exact successor_head_dominates d e tail heStep
  have hupper := successor_head_le_second d e tail hbound
  constructor
  · intro heq hsurvive
    have hu := (successor_head_eq_second_iff d e tail he hbound).2 hsurvive
    omega
  · intro hnot
    by_contra hne
    have : headDegree (havelHakimiStep (d :: e :: tail)) = e := by omega
    exact hnot ((successor_head_eq_second_iff d e tail he hbound).1 this)

/-- Corrected equal-prefix theorem: when source and target have the same first
two entries, it suffices that every surviving target maximum is matched by a
surviving source maximum. -/
theorem cumulativeHeadSum_two_monotone_equalPrefix_of_survival
    (d e : ℕ) (sourceTail targetTail : List ℕ) (hd : 0 < d) (he : 0 < e)
    (hsBound : ∀ x ∈ e :: sourceTail, x ≤ e)
    (htBound : ∀ x ∈ e :: targetTail, x ≤ e)
    (hsurvive : UndecrementedMax d e (e :: targetTail) →
      UndecrementedMax d e (e :: sourceTail)) :
    cumulativeHeadSum 2 (d :: e :: targetTail) ≤
      cumulativeHeadSum 2 (d :: e :: sourceTail) := by
  change d + headDegree (havelHakimiStep (d :: e :: targetTail)) ≤
    d + headDegree (havelHakimiStep (d :: e :: sourceTail))
  by_cases ht : UndecrementedMax d e (e :: targetTail)
  · rw [(successor_head_eq_second_iff d e targetTail he htBound).2 ht]
    rw [(successor_head_eq_second_iff d e sourceTail he hsBound).2 (hsurvive ht)]
  · have htHead : headDegree (havelHakimiStep (d :: e :: targetTail)) ≤ e - 1 := by
      have hu := successor_head_le_second d e targetTail htBound
      by_contra h
      have heq : headDegree (havelHakimiStep (d :: e :: targetTail)) = e := by omega
      exact ht ((successor_head_eq_second_iff d e targetTail he htBound).1 heq)
    have hsLower : e - 1 ≤
        headDegree (havelHakimiStep (d :: e :: sourceTail)) := by
      by_cases hs : UndecrementedMax d e (e :: sourceTail)
      · have := (successor_head_eq_second_iff d e sourceTail he hsBound).2 hs
        omega
      · rw [(successor_head_eq_pred_iff d e sourceTail hd he hsBound).2 hs]
    omega

end WrittenOnTheWallII.GraphConjecture61SecondHeadCriterion
