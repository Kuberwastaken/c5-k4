import FormalConjecturesUtil

/-!
# WOWII 61: tight second-head bounds

For a descending list `d :: e :: tail` with positive head, the first head of
its Havel--Hakimi successor lies between `e - 1` and `e`.  These tight bounds
prove two-step cumulative-head monotonicity whenever the source strictly
dominates the target at the top-two prefix.
-/

namespace WrittenOnTheWallII.GraphConjecture61SecondHead

open SimpleGraph

def headDegree : List ℕ → ℕ
  | [] => 0
  | d :: _ => d

def cumulativeHeadSum : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => headDegree s + cumulativeHeadSum k (havelHakimiStep s)

theorem mem_havelHakimiStep_le
    {d bound : ℕ} {rest : List ℕ}
    (hbound : ∀ x ∈ rest, x ≤ bound)
    {y : ℕ} (hy : y ∈ havelHakimiStep (d :: rest)) : y ≤ bound := by
  let a := rest.take d
  let b := rest.drop d
  have hperm := List.mergeSort_perm (a.map (· - 1) ++ b) (· ≥ ·)
  have hy' : y ∈ a.map (· - 1) ++ b := by
    have hm : y ∈ (a.map (· - 1) ++ b).mergeSort (· ≥ ·) := by
      simpa [havelHakimiStep, a, b, List.splitAt_eq] using hy
    exact (hperm.mem_iff).1 hm
  rw [List.mem_append] at hy'
  rcases hy' with hyA | hyB
  · rw [List.mem_map] at hyA
    obtain ⟨x, hx, rfl⟩ := hyA
    exact (Nat.sub_le x 1).trans (hbound x (List.mem_of_mem_take hx))
  · exact hbound y (List.mem_of_mem_drop hyB)

theorem havelHakimiStep_ne_nil (d e : ℕ) (tail : List ℕ) :
    havelHakimiStep (d :: e :: tail) ≠ [] := by
  intro hnil
  have hlen := havelHakimiStep_length_cons d (e :: tail)
  rw [hnil] at hlen
  simp at hlen

/-- Universal upper half of the exact two-valued interval. -/
theorem secondHead_le
    (d e : ℕ) (tail : List ℕ)
    (hdescending : ∀ x ∈ e :: tail, x ≤ e) :
    headDegree (havelHakimiStep (d :: e :: tail)) ≤ e := by
  have hne := havelHakimiStep_ne_nil d e tail
  cases hstep : havelHakimiStep (d :: e :: tail) with
  | nil => exact (hne hstep).elim
  | cons y ys =>
      change y ≤ e
      apply mem_havelHakimiStep_le hdescending
      rw [hstep]
      simp

/-- If the removed head is positive, the original second entry is decremented
and survives as `e-1`, so the sorted successor head is at least `e-1`. -/
theorem secondHead_lower
    (d e : ℕ) (tail : List ℕ) (hd : 0 < d) :
    e - 1 ≤ headDegree (havelHakimiStep (d :: e :: tail)) := by
  let a := (e :: tail).take d
  let b := (e :: tail).drop d
  have heA : e ∈ a := by
    cases d with
    | zero => omega
    | succ d => simp [a]
  have heMap : e - 1 ∈ a.map (· - 1) := by
    exact List.mem_map.2 ⟨e, heA, rfl⟩
  have heStep : e - 1 ∈ havelHakimiStep (d :: e :: tail) := by
    have hp := List.mergeSort_perm (a.map (· - 1) ++ b) (· ≥ ·)
    have : e - 1 ∈ a.map (· - 1) ++ b := by simp [heMap]
    have hm := (hp.mem_iff).2 this
    simpa [havelHakimiStep, a, b, List.splitAt_eq] using hm
  have hne := havelHakimiStep_ne_nil d e tail
  cases hstep : havelHakimiStep (d :: e :: tail) with
  | nil => exact (hne hstep).elim
  | cons y ys =>
      change e - 1 ≤ y
      rw [hstep] at heStep
      have hpair := List.pairwise_mergeSort' (fun a b : ℕ ↦ a ≥ b)
        (a.map (· - 1) ++ b)
      have hy : ∀ z ∈ ys, z ≤ y := by
        have hmerge : (a.map (· - 1) ++ b).mergeSort (· ≥ ·) = y :: ys := by
          rw [← hstep]
          simp [havelHakimiStep, a, b, List.splitAt_eq]
        rw [hmerge] at hpair
        exact (List.pairwise_cons.1 hpair).1
      simp at heStep
      rcases heStep with he | he
      · omega
      · exact hy (e - 1) he

/-- Tight interval: the second canonical head is either `e-1` or `e`. -/
theorem secondHead_tight_bounds
    (d e : ℕ) (tail : List ℕ) (hd : 0 < d)
    (hdescending : ∀ x ∈ e :: tail, x ≤ e) :
    e - 1 ≤ headDegree (havelHakimiStep (d :: e :: tail)) ∧
      headDegree (havelHakimiStep (d :: e :: tail)) ≤ e :=
  ⟨secondHead_lower d e tail hd, secondHead_le d e tail hdescending⟩

/-- Nontrivial pairwise theorem: strict source dominance at prefix two pays
for the possible one-unit depression of the source's second canonical head. -/
theorem cumulativeHeadSum_two_monotone_of_strictTopTwo
    (ds es dt et : ℕ) (rs rt : List ℕ)
    (hds : 0 < ds)
    (htDescending : ∀ x ∈ et :: rt, x ≤ et)
    (hstrict : dt + et < ds + es) :
    cumulativeHeadSum 2 (dt :: et :: rt) ≤
      cumulativeHeadSum 2 (ds :: es :: rs) := by
  change dt + headDegree (havelHakimiStep (dt :: et :: rt)) ≤
    ds + headDegree (havelHakimiStep (ds :: es :: rs))
  have htUpper := secondHead_le dt et rt htDescending
  have hsLower := secondHead_lower ds es rs hds
  omega

/-- Both ends of the interval occur on graphical controls. -/
theorem tight_interval_controls :
    headDegree (havelHakimiStep [2, 2, 2, 2]) = 2 ∧
    headDegree (havelHakimiStep [2, 2, 2, 1, 1]) = 1 := by
  constructor
  · have h := secondHead_tight_bounds 2 2 [2, 2] (by omega) (by
      intro x hx
      simp at hx
      omega)
    have hstep : havelHakimiStep [2, 2, 2, 2] = [2, 1, 1] := by
      change ([1, 1, 2] : List ℕ).mergeSort (· ≥ ·) = [2, 1, 1]
      have hp : List.Perm ([1, 1, 2] : List ℕ) [2, 1, 1] := by decide
      have hperm : List.Perm
          (([1, 1, 2] : List ℕ).mergeSort (· ≥ ·)) [2, 1, 1] :=
        (List.mergeSort_perm _ _).trans hp
      exact hperm.eq_of_pairwise'
        (List.pairwise_mergeSort' (fun a b : ℕ ↦ a ≥ b) _) (by decide)
    rw [hstep]
    rfl
  · have hstep : havelHakimiStep [2, 2, 2, 1, 1] = [1, 1, 1, 1] := by
      change ([1, 1, 1, 1] : List ℕ).mergeSort (· ≥ ·) = [1, 1, 1, 1]
      exact List.mergeSort_eq_self (r := fun a b : ℕ ↦ a ≥ b) (by decide)
    rw [hstep]
    rfl

end WrittenOnTheWallII.GraphConjecture61SecondHead
