import GraphConjecture183TwoDeletionTrunk

/-!
# WOWII 183: explicit odd-cycle deletion choices

This module supplies an explicit root-sensitive adjacent pair on every cycle
of order at least five and proves all local adjacency/domination facts.  The
remaining complement path connectivity/coloring facts are isolated in one
standard cycle-family proposition.
-/

namespace WrittenOnTheWallII.GraphConjecture183OddCyclePackage

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183TwoDeletionTrunk

/-- Root-sensitive adjacent deletion pair: choose either `{0,1}` or `{2,3}`.
For cycles of order at least five these pairs exist, are adjacent, and one pair
avoids every prescribed root. -/
def cycleDeleteFirst {n : ℕ} (h : 5 ≤ n) : Fin n := ⟨0, by omega⟩
def cycleDeleteSecond {n : ℕ} (h : 5 ≤ n) : Fin n := ⟨1, by omega⟩
def cycleDeleteThird {n : ℕ} (h : 5 ≤ n) : Fin n := ⟨2, by omega⟩
def cycleDeleteFourth {n : ℕ} (h : 5 ≤ n) : Fin n := ⟨3, by omega⟩

def rootSensitiveCyclePair {n : ℕ} (h : 5 ≤ n) (r : Fin n) : Fin n × Fin n :=
  if r = cycleDeleteFirst h ∨ r = cycleDeleteSecond h then
    (cycleDeleteThird h, cycleDeleteFourth h)
  else
    (cycleDeleteFirst h, cycleDeleteSecond h)

lemma rootSensitiveCyclePair_avoids_root {n : ℕ} (h : 5 ≤ n) (r : Fin n) :
    r ≠ (rootSensitiveCyclePair h r).1 ∧
      r ≠ (rootSensitiveCyclePair h r).2 := by
  unfold rootSensitiveCyclePair
  by_cases hr : r = cycleDeleteFirst h ∨ r = cycleDeleteSecond h
  · simp only [if_pos hr]
    rcases hr with hr | hr <;> subst r <;> constructor <;>
      intro heq <;> have := congrArg Fin.val heq <;> simp_all [cycleDeleteFirst,
        cycleDeleteSecond, cycleDeleteThird, cycleDeleteFourth]
  · simp only [if_neg hr]
    exact ⟨fun heq => hr (Or.inl heq), fun heq => hr (Or.inr heq)⟩

lemma rootSensitiveCyclePair_distinct {n : ℕ} (h : 5 ≤ n) (r : Fin n) :
    (rootSensitiveCyclePair h r).1 ≠ (rootSensitiveCyclePair h r).2 := by
  unfold rootSensitiveCyclePair
  split <;> intro heq <;> have := congrArg Fin.val heq <;>
    simp_all [cycleDeleteFirst, cycleDeleteSecond, cycleDeleteThird, cycleDeleteFourth]

lemma rootSensitiveCyclePair_adj {n : ℕ} (h : 5 ≤ n) (r : Fin n) :
    (cycleGraph n).Adj (rootSensitiveCyclePair h r).1
      (rootSensitiveCyclePair h r).2 := by
  rw [cycleGraph_adj']
  unfold rootSensitiveCyclePair
  split <;> simp [cycleDeleteFirst, cycleDeleteSecond, cycleDeleteThird,
    cycleDeleteFourth, Fin.sub_val_of_le]

/-- Both deleted vertices have explicit retained neighbors. -/
lemma rootSensitiveCyclePair_retained_neighbors {n : ℕ} (h : 5 ≤ n)
    (r : Fin n) :
    (∃ z ∉ ({(rootSensitiveCyclePair h r).1,
        (rootSensitiveCyclePair h r).2} : Set (Fin n)),
      (cycleGraph n).Adj (rootSensitiveCyclePair h r).1 z) ∧
    (∃ z ∉ ({(rootSensitiveCyclePair h r).1,
        (rootSensitiveCyclePair h r).2} : Set (Fin n)),
      (cycleGraph n).Adj (rootSensitiveCyclePair h r).2 z) := by
  unfold rootSensitiveCyclePair
  split
  · refine ⟨⟨cycleDeleteSecond h, ?_, ?_⟩,
      ⟨⟨4, by omega⟩, ?_, ?_⟩⟩
    · simp [cycleDeleteSecond, cycleDeleteThird, cycleDeleteFourth]
    · rw [cycleGraph_adj']; left
      rw [Fin.sub_val_of_le]
      · simp [cycleDeleteSecond, cycleDeleteThird]
      · simp [cycleDeleteSecond, cycleDeleteThird]
    · simp [cycleDeleteThird, cycleDeleteFourth]
    · rw [cycleGraph_adj']; right
      rw [Fin.sub_val_of_le]
      · simp [cycleDeleteFourth]
      · simp [cycleDeleteFourth]
  · refine ⟨⟨⟨n - 1, by omega⟩, ?_, ?_⟩,
      ⟨cycleDeleteThird h, ?_, ?_⟩⟩
    · simp only [Set.mem_insert_iff, Set.mem_singleton_iff, not_or]
      constructor <;> intro heq <;> have hv := congrArg Fin.val heq <;>
        simp [cycleDeleteFirst, cycleDeleteSecond] at hv <;> omega
    · rw [cycleGraph_adj']; left
      change ((⟨0, by omega⟩ : Fin n) - ⟨n - 1, by omega⟩).val = 1
      rw [Fin.val_sub]
      have hnsub : n - (n - 1) = 1 := by omega
      rw [hnsub]
      have hn1 : 1 < n := by omega
      simpa using Nat.mod_eq_of_lt hn1
    · simp [cycleDeleteFirst, cycleDeleteSecond, cycleDeleteThird]
    · rw [cycleGraph_adj']; right
      rw [Fin.sub_val_of_le]
      · simp [cycleDeleteSecond, cycleDeleteThird]
      · simp [cycleDeleteSecond, cycleDeleteThird]

/-- Standard remaining cycle API fact: deleting the chosen adjacent pair leaves
a connected bipartite path. -/
def CyclePairComplementPathProperty : Prop :=
  ∀ (n : ℕ) (h : 5 ≤ n) (r : Fin n),
    ((cycleGraph n).induce ({(rootSensitiveCyclePair h r).1,
      (rootSensitiveCyclePair h r).2} : Set (Fin n))ᶜ).Connected ∧
    ((cycleGraph n).induce ({(rootSensitiveCyclePair h r).1,
      (rootSensitiveCyclePair h r).2} : Set (Fin n))ᶜ).IsBipartite

/-- With the standard complement-path fact, the explicit pair satisfies the
full v0.21 structural predicate. -/
theorem rootSensitiveCyclePair_isGoodTwoDeletion
    (hpath : CyclePairComplementPathProperty)
    {n : ℕ} (h : 5 ≤ n) (r : Fin n) :
    IsGoodTwoDeletion (cycleGraph n) (rootSensitiveCyclePair h r).1
      (rootSensitiveCyclePair h r).2 := by
  refine ⟨rootSensitiveCyclePair_distinct h r,
    rootSensitiveCyclePair_adj h r, (hpath n h r).1, (hpath n h r).2, ?_⟩
  exact rootSensitiveCyclePair_retained_neighbors h r

/-- Triangle exception: no two-vertex complement can dominate `K3`, because
the complement is a singleton but the branch budget would still pay an
external attachment.  Numerically, the two-deletion threshold itself fails. -/
theorem triangle_twoDeletion_threshold_impossible (t b : ℕ)
    (ht : t + 2 ≤ 3) (hb : 3 ≤ b + 1) (_hbmax : b ≤ 2) :
    t + 1 ≤ b := by
  exact twoDeletion_budget t b 3 ht hb

end WrittenOnTheWallII.GraphConjecture183OddCyclePackage
