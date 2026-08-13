import FormalConjecturesUtil

/-!
# WOWII 61: a two-step degree-prefix functional

The first two canonical Havel--Hakimi heads are always bounded by the sum of
the first two entries of a descending degree sequence.  Equality is not
universal; the five-vertex path gives the first obstruction.
-/

namespace WrittenOnTheWallII.GraphConjecture61PrefixFunctional

open SimpleGraph

def headDegree : List ℕ → ℕ
  | [] => 0
  | d :: _ => d

def cumulativeHeadSum : ℕ → List ℕ → ℕ
  | 0, _ => 0
  | k + 1, s => headDegree s + cumulativeHeadSum k (havelHakimiStep s)

/-- Every entry produced by a Havel--Hakimi step is bounded by an upper bound
for all entries in the original tail.  This requires no graphicality. -/
theorem mem_havelHakimiStep_le
    {d bound : ℕ} {rest : List ℕ}
    (hbound : ∀ x ∈ rest, x ≤ bound)
    {y : ℕ} (hy : y ∈ havelHakimiStep (d :: rest)) :
    y ≤ bound := by
  let a := rest.take d
  let b := rest.drop d
  have hperm := List.mergeSort_perm (a.map (· - 1) ++ b) (· ≥ ·)
  have hy' : y ∈ a.map (· - 1) ++ b := by
    have : y ∈ (a.map (· - 1) ++ b).mergeSort (· ≥ ·) := by
      simpa [havelHakimiStep, a, b, List.splitAt_eq] using hy
    exact (hperm.mem_iff).1 this
  rw [List.mem_append] at hy'
  rcases hy' with hyA | hyB
  · rw [List.mem_map] at hyA
    obtain ⟨x, hx, rfl⟩ := hyA
    have hxRest : x ∈ rest := List.mem_of_mem_take hx
    exact (Nat.sub_le x 1).trans (hbound x hxRest)
  · have hyRest : y ∈ rest := List.mem_of_mem_drop hyB
    exact hbound y hyRest

/-- If the original tail is nonempty, so is its canonical successor. -/
theorem havelHakimiStep_ne_nil_of_rest_ne_nil
    (d : ℕ) {rest : List ℕ} (hrest : rest ≠ []) :
    havelHakimiStep (d :: rest) ≠ [] := by
  cases rest with
  | nil => exact (hrest rfl).elim
  | cons x xs =>
      intro hnil
      have hlen := havelHakimiStep_length_cons d (x :: xs)
      rw [hnil] at hlen
      simp at hlen

/-- The second canonical head cannot exceed the original second entry of a
descending list. -/
theorem secondCanonicalHead_le_secondEntry
    (d e : ℕ) (tail : List ℕ)
    (hdescending : ∀ x ∈ e :: tail, x ≤ e) :
    headDegree (havelHakimiStep (d :: e :: tail)) ≤ e := by
  have hne := havelHakimiStep_ne_nil_of_rest_ne_nil d (by simp : e :: tail ≠ [])
  cases hstep : havelHakimiStep (d :: e :: tail) with
  | nil => exact (hne hstep).elim
  | cons y ys =>
      change y ≤ e
      apply mem_havelHakimiStep_le hdescending
      rw [hstep]
      simp

/-- Nontrivial universal two-step prefix bound: on every descending list with
at least two entries, the first two eliminated heads sum to at most the first
two original degrees. -/
theorem cumulativeHeadSum_two_le_topTwoPrefix
    (d e : ℕ) (tail : List ℕ)
    (hdescending : ∀ x ∈ e :: tail, x ≤ e) :
    cumulativeHeadSum 2 (d :: e :: tail) ≤
      ((d :: e :: tail).take 2).sum := by
  change d + headDegree (havelHakimiStep (d :: e :: tail)) ≤ d + e
  exact Nat.add_le_add_left
    (secondCanonicalHead_le_secondEntry d e tail hdescending) d

/-- The path degree sequence is descending, so it satisfies the universal
two-step prefix upper bound. -/
theorem pathFive_twoStep_prefix_bound :
    cumulativeHeadSum 2 [2, 2, 2, 1, 1] ≤
      (([2, 2, 2, 1, 1] : List ℕ).take 2).sum := by
  apply cumulativeHeadSum_two_le_topTwoPrefix 2 2 [2, 1, 1]
  intro x hx
  simp at hx
  omega

/-- Exact canonical value on the path sequence. -/
theorem pathFive_cumulativeHeadSum_two :
    cumulativeHeadSum 2 [2, 2, 2, 1, 1] = 3 := by
  have hstep : havelHakimiStep [2, 2, 2, 1, 1] = [1, 1, 1, 1] := by
    change ([1, 1, 1, 1] : List ℕ).mergeSort (· ≥ ·) = [1, 1, 1, 1]
    exact List.mergeSort_eq_self (r := fun a b : ℕ ↦ a ≥ b) (by decide)
  change 2 + headDegree (havelHakimiStep [2, 2, 2, 1, 1]) = 3
  rw [hstep]
  rfl

/-- Therefore the tempting equality with the top-two prefix sum is false: the
prefix sum is four but the two canonical heads sum to three. -/
theorem topTwoPrefix_identity_false :
    cumulativeHeadSum 2 [2, 2, 2, 1, 1] <
      (([2, 2, 2, 1, 1] : List ℕ).take 2).sum := by
  rw [pathFive_cumulativeHeadSum_two]
  norm_num

/-- On the all-equal four-cycle degree shape, the upper bound is tight. -/
theorem twoRegularFour_tight :
    cumulativeHeadSum 2 [2, 2, 2, 2] =
      (([2, 2, 2, 2] : List ℕ).take 2).sum := by
  have hstep : havelHakimiStep [2, 2, 2, 2] = [2, 1, 1] := by
    change ([1, 1, 2] : List ℕ).mergeSort (· ≥ ·) = [2, 1, 1]
    have hp : List.Perm ([1, 1, 2] : List ℕ) [2, 1, 1] := by decide
    have hperm : List.Perm
        (([1, 1, 2] : List ℕ).mergeSort (· ≥ ·)) [2, 1, 1] :=
      (List.mergeSort_perm _ _).trans hp
    apply hperm.eq_of_pairwise' (r := fun a b : ℕ ↦ a ≥ b)
    · exact List.pairwise_mergeSort' (fun a b : ℕ ↦ a ≥ b) _
    · decide
  change 2 + headDegree (havelHakimiStep [2, 2, 2, 2]) = 4
  rw [hstep]
  rfl

end WrittenOnTheWallII.GraphConjecture61PrefixFunctional
