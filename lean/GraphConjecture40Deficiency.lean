import GraphConjecture40Baseline

/-!
# WOWII 40: exact deficiency coordinates

This file introduces the three complementary coordinates used in the paper
proof of Conjecture 40 and verifies, over `Nat`, that the upstream inequality
is exactly `linearForestRank + oddDeletion >= 2 * feedbackDeletion + 1`.

The names are deliberately local: at this rung they are complements of the
three repository invariants.  Identifying `linearForestRank` with a maximum
spanning linear forest is the next graph-theoretic API bridge.
-/

namespace WrittenOnTheWallII.GraphConjecture40Deficiency

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

noncomputable def feedbackDeletion (G : SimpleGraph V) : ℕ :=
  Fintype.card V - G.largestInducedForestSize

noncomputable def oddDeletion (G : SimpleGraph V) : ℕ :=
  Fintype.card V - G.largestInducedBipartiteSubgraphSize

noncomputable def linearForestRank (G : SimpleGraph V) : ℕ :=
  Fintype.card V - pathCoverNumber G

omit [DecidableEq V] in
/-- No induced forest has more vertices than the ambient finite graph. -/
lemma largestInducedForestSize_le_card (G : SimpleGraph V) :
    G.largestInducedForestSize ≤ Fintype.card V := by
  unfold largestInducedForestSize
  apply csSup_le
  · refine ⟨0, ∅, ?_, rfl⟩
    intro v
    have hv : False := by simpa using v.property
    exact hv.elim
  · rintro n ⟨S, -, rfl⟩
    exact S.card_le_univ

/-- No induced bipartite subgraph has more vertices than the ambient graph. -/
lemma largestInducedBipartiteSubgraphSize_le_card (G : SimpleGraph V) :
    G.largestInducedBipartiteSubgraphSize ≤ Fintype.card V := by
  unfold largestInducedBipartiteSubgraphSize
  apply csSup_le
  · refine ⟨0, ∅, ?_, rfl⟩
    rw [induce_isBipartite_iff_exists_coloring]
    exact ⟨fun _ ↦ 0, by simp⟩
  · rintro n ⟨S, -, rfl⟩
    exact S.card_le_univ

/-- Exact natural-number normalization of WOWII 40 in complementary
coordinates. The path-cover upper bound is stated explicitly because the
current repository API defines that invariant by `sInf` but exposes no
singleton-cover comparison theorem. -/
theorem integer_bound_iff_deficiency_bound
    (G : SimpleGraph V)
    (hp : pathCoverNumber G ≤ Fintype.card V) :
    pathCoverNumber G + G.largestInducedBipartiteSubgraphSize + 1 ≤
        2 * G.largestInducedForestSize ↔
      2 * feedbackDeletion G + 1 ≤
        linearForestRank G + oddDeletion G := by
  have hf := largestInducedForestSize_le_card G
  have hb := largestInducedBipartiteSubgraphSize_le_card G
  unfold feedbackDeletion oddDeletion linearForestRank
  omega

/-- The deficiency inequality implies Conjecture 40 in its exact upstream
real/ceiling presentation. -/
theorem conjecture40_of_deficiency_bound
    (G : SimpleGraph V)
    (hp : pathCoverNumber G ≤ Fintype.card V)
    (hdef : 2 * feedbackDeletion G + 1 ≤
      linearForestRank G + oddDeletion G) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hint := (integer_bound_iff_deficiency_bound G hp).mpr hdef
  have hintR :
      (pathCoverNumber G : ℝ) + b G + 1 ≤
        2 * (G.largestInducedForestSize : ℝ) := by
    unfold b
    exact_mod_cast hint
  rw [Int.ceil_le]
  norm_num
  linarith

omit [DecidableEq V] in
/-- An acyclic graph has forest invariant equal to its full order. -/
lemma largestInducedForestSize_eq_card_of_isAcyclic
    (G : SimpleGraph V) (hG : G.IsAcyclic) :
    G.largestInducedForestSize = Fintype.card V := by
  apply le_antisymm (largestInducedForestSize_le_card G)
  simpa using
    GraphConjecture40Baseline.card_le_largestInducedForestSize
      G (Finset.univ : Finset V)
        (by simpa using hG.induce ((Finset.univ : Finset V) : Set V))

/-- An acyclic graph also has bipartite invariant equal to its full order. -/
lemma largestInducedBipartiteSubgraphSize_eq_card_of_isAcyclic
    (G : SimpleGraph V) (hG : G.IsAcyclic) :
    G.largestInducedBipartiteSubgraphSize = Fintype.card V := by
  apply le_antisymm (largestInducedBipartiteSubgraphSize_le_card G)
  simpa using
    GraphConjecture40Baseline.card_le_largestInducedBipartiteSubgraphSize
      G (Finset.univ : Finset V)
        (by simpa using
          (hG.induce ((Finset.univ : Finset V) : Set V)).isBipartite)

/-- The zero-feedback-deletion base case. Acyclicity supplies `tau=o=0`;
one edge in a spanning linear forest is represented at this API layer by the
equivalent strict path-cover order bound. -/
theorem conjecture40_of_isAcyclic_of_pathCoverNumber_lt_card
    (G : SimpleGraph V) (hG : G.IsAcyclic)
    (hp : pathCoverNumber G < Fintype.card V) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hf := largestInducedForestSize_eq_card_of_isAcyclic G hG
  have hb := largestInducedBipartiteSubgraphSize_eq_card_of_isAcyclic G hG
  have hp' : pathCoverNumber G ≤ Fintype.card V := hp.le
  apply conjecture40_of_deficiency_bound G hp'
  unfold feedbackDeletion oddDeletion linearForestRank
  rw [hf, hb]
  omega

end WrittenOnTheWallII.GraphConjecture40Deficiency
