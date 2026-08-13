import GraphConjecture40CactusFeedbackUnit

/-!
# WOWII 40: cut-vertex include/exclude states

Unconditional additivity across a cut vertex is false unless one records
whether the optimizing induced forest contains that vertex.  This file
defines the two finite optimization states, proves attainment, and proves the
correct universal max-of-states formula for maximum induced-forest order.
-/

namespace WrittenOnTheWallII.GraphConjecture40CutVertexSum

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

noncomputable def forestOrderIncluding (G : SimpleGraph V) (c : V) : ℕ :=
  sSup {n | ∃ S : Finset V,
    (G.induce (S : Set V)).IsAcyclic ∧ c ∈ S ∧ S.card = n}

noncomputable def forestOrderExcluding (G : SimpleGraph V) (c : V) : ℕ :=
  sSup {n | ∃ S : Finset V,
    (G.induce (S : Set V)).IsAcyclic ∧ c ∉ S ∧ S.card = n}

lemma exists_forestOrderIncluding_witness (G : SimpleGraph V) (c : V) :
    ∃ S : Finset V, (G.induce (S : Set V)).IsAcyclic ∧ c ∈ S ∧
      S.card = forestOrderIncluding G c := by
  let A : Set ℕ := {n | ∃ S : Finset V,
    (G.induce (S : Set V)).IsAcyclic ∧ c ∈ S ∧ S.card = n}
  have hne : A.Nonempty := by
    refine ⟨1, {c}, ?_, by simp, by simp⟩
    exact GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ∅ c (by simp)
  have hbdd : BddAbove A := ⟨Fintype.card V, fun n hn ↦ by
    obtain ⟨S, -, -, rfl⟩ := hn
    exact S.card_le_univ⟩
  obtain ⟨S, hS, hc, hcard⟩ := Nat.sSup_mem hne hbdd
  exact ⟨S, hS, hc, by simpa [forestOrderIncluding, A] using hcard⟩

omit [DecidableEq V] in
lemma exists_forestOrderExcluding_witness (G : SimpleGraph V) (c : V) :
    ∃ S : Finset V, (G.induce (S : Set V)).IsAcyclic ∧ c ∉ S ∧
      S.card = forestOrderExcluding G c := by
  let A : Set ℕ := {n | ∃ S : Finset V,
    (G.induce (S : Set V)).IsAcyclic ∧ c ∉ S ∧ S.card = n}
  have hne : A.Nonempty := by
    refine ⟨0, ∅, ?_, by simp, rfl⟩
    intro v
    have hv : False := by simpa using v.property
    exact hv.elim
  have hbdd : BddAbove A := ⟨Fintype.card V, fun n hn ↦ by
    obtain ⟨S, -, -, rfl⟩ := hn
    exact S.card_le_univ⟩
  obtain ⟨S, hS, hc, hcard⟩ := Nat.sSup_mem hne hbdd
  exact ⟨S, hS, hc, by simpa [forestOrderExcluding, A] using hcard⟩

omit [DecidableEq V] in
/-- Every explicit induced forest containing the cut is bounded by the
including state. -/
lemma card_le_forestOrderIncluding (G : SimpleGraph V) (c : V) (S : Finset V)
    (hS : (G.induce (S : Set V)).IsAcyclic) (hc : c ∈ S) :
    S.card ≤ forestOrderIncluding G c := by
  unfold forestOrderIncluding
  apply le_csSup
  · exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨T, -, -, rfl⟩ := hn
      exact T.card_le_univ⟩
  · exact ⟨S, hS, hc, rfl⟩

omit [DecidableEq V] in
/-- Every explicit induced forest excluding the cut is bounded by the
excluding state. -/
lemma card_le_forestOrderExcluding (G : SimpleGraph V) (c : V) (S : Finset V)
    (hS : (G.induce (S : Set V)).IsAcyclic) (hc : c ∉ S) :
    S.card ≤ forestOrderExcluding G c := by
  unfold forestOrderExcluding
  apply le_csSup
  · exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨T, -, -, rfl⟩ := hn
      exact T.card_le_univ⟩
  · exact ⟨S, hS, hc, rfl⟩

/-- Correct universal cut-state formula. -/
theorem largestInducedForestSize_eq_max_states (G : SimpleGraph V) (c : V) :
    G.largestInducedForestSize =
      max (forestOrderIncluding G c) (forestOrderExcluding G c) := by
  apply le_antisymm
  · obtain ⟨S, hS, hcard⟩ :=
      GraphConjecture40CactusFeedbackUnit.exists_largestInducedForestSize_witness G
    rw [← hcard]
    by_cases hc : c ∈ S
    · exact le_trans (card_le_forestOrderIncluding G c S hS hc) (le_max_left _ _)
    · exact le_trans (card_le_forestOrderExcluding G c S hS hc) (le_max_right _ _)
  · apply max_le
    · obtain ⟨S, hS, -, hcard⟩ := exists_forestOrderIncluding_witness G c
      rw [← hcard]
      exact GraphConjecture40Baseline.card_le_largestInducedForestSize G S hS
    · obtain ⟨S, hS, -, hcard⟩ := exists_forestOrderExcluding_witness G c
      rw [← hcard]
      exact GraphConjecture40Baseline.card_le_largestInducedForestSize G S hS

/-- Statewise comparison is sufficient for equality of maximum induced-
forest orders. This is the corrected exchange interface for composing a leaf
cluster with a remainder. -/
theorem largestInducedForestSize_eq_of_statewise
    (G H : SimpleGraph V) (c : V)
    (hinc : forestOrderIncluding G c = forestOrderIncluding H c)
    (hexc : forestOrderExcluding G c = forestOrderExcluding H c) :
    G.largestInducedForestSize = H.largestInducedForestSize := by
  rw [largestInducedForestSize_eq_max_states G c,
    largestInducedForestSize_eq_max_states H c, hinc, hexc]

/-- It is enough to compare both states in each direction; this form is
convenient for separate extension and restriction arguments at a separator. -/
theorem largestInducedForestSize_eq_of_statewise_bounds
    (G H : SimpleGraph V) (c : V)
    (hincGH : forestOrderIncluding G c ≤ forestOrderIncluding H c)
    (hincHG : forestOrderIncluding H c ≤ forestOrderIncluding G c)
    (hexcGH : forestOrderExcluding G c ≤ forestOrderExcluding H c)
    (hexcHG : forestOrderExcluding H c ≤ forestOrderExcluding G c) :
    G.largestInducedForestSize = H.largestInducedForestSize :=
  largestInducedForestSize_eq_of_statewise G H c
    (le_antisymm hincGH hincHG) (le_antisymm hexcGH hexcHG)

end WrittenOnTheWallII.GraphConjecture40CutVertexSum
