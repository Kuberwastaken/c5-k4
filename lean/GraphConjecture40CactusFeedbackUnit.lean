import GraphConjecture40FeedbackRecursion

/-!
# WOWII 40: an apex-forest cactus feedback unit

If deleting a selected cut vertex makes the graph acyclic but the full graph
is cyclic, then both maximum induced forests have exactly `n-1` vertices.
This proves the forest equality required by v0.19 from structural hypotheses
alone and identifies the selected vertex as one exact feedback unit.
-/

namespace WrittenOnTheWallII.GraphConjecture40CactusFeedbackUnit

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [DecidableEq V] in
/-- The finite `sSup` defining maximum induced-forest order is attained. -/
lemma exists_largestInducedForestSize_witness (G : SimpleGraph V) :
    ∃ S : Finset V,
      (G.induce (S : Set V)).IsAcyclic ∧
      S.card = G.largestInducedForestSize := by
  let A : Set ℕ :=
    {n | ∃ S : Finset V, (G.induce (S : Set V)).IsAcyclic ∧ S.card = n}
  have hAne : A.Nonempty := by
    refine ⟨0, ∅, ?_, rfl⟩
    intro v
    have hv : False := by simpa using v.property
    exact hv.elim
  have hAbdd : BddAbove A := by
    exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨S, -, rfl⟩ := hn
      exact S.card_le_univ⟩
  have hmem : sSup A ∈ A := Nat.sSup_mem hAne hAbdd
  obtain ⟨S, hS, hcard⟩ := hmem
  exact ⟨S, hS, by simpa [largestInducedForestSize, A] using hcard⟩

omit [DecidableEq V] in
/-- A cyclic finite graph loses at least one vertex in every induced forest. -/
theorem largestInducedForestSize_lt_card_of_not_isAcyclic
    (G : SimpleGraph V) (hcyclic : ¬G.IsAcyclic) :
    G.largestInducedForestSize < Fintype.card V := by
  have hle := GraphConjecture40Deficiency.largestInducedForestSize_le_card G
  apply lt_of_le_of_ne hle
  intro heq
  obtain ⟨S, hS, hcard⟩ := exists_largestInducedForestSize_witness G
  have hSuniv : S = Finset.univ := by
    apply Finset.eq_univ_of_card
    simp [hcard, heq]
  apply hcyclic
  subst S
  have hInd : (G.induce Set.univ).IsAcyclic := by
    rw [← Finset.coe_univ]
    exact hS
  exact (SimpleGraph.induceUnivIso G).isAcyclic_iff.mp hInd

/-- Structural forest equality for an apex-forest feedback unit. -/
theorem forest_eq_of_deleteVertex_isAcyclic_of_not_isAcyclic
    (G : SimpleGraph V) (v : V)
    (hdelete :
      (GraphConjecture40FeedbackRecursion.deleteVertex G v).IsAcyclic)
    (hcyclic : ¬G.IsAcyclic) :
    G.largestInducedForestSize =
      (GraphConjecture40FeedbackRecursion.deleteVertex G v).largestInducedForestSize := by
  have hdel :=
    GraphConjecture40Deficiency.largestInducedForestSize_eq_card_of_isAcyclic
      (GraphConjecture40FeedbackRecursion.deleteVertex G v) hdelete
  have hlt := largestInducedForestSize_lt_card_of_not_isAcyclic G hcyclic
  have hn := GraphConjecture40FeedbackRecursion.card_deleteVertex (V := V) v
  have hlower :
      (GraphConjecture40FeedbackRecursion.deleteVertex G v).largestInducedForestSize ≤
        G.largestInducedForestSize := by
    rw [hdel]
    let S : Finset V := Finset.univ.erase v
    have hScard : S.card =
        Fintype.card {x : V // x ≠ v} := by
      rw [Finset.card_erase_of_mem (Finset.mem_univ v), card_univ]
      omega
    apply le_trans (le_of_eq hScard.symm)
    apply GraphConjecture40Baseline.card_le_largestInducedForestSize G S
    have hset : (S : Set V) = {x | x ≠ v} := by
      ext x
      simp [S]
    rw [hset]
    exact hdelete
  rw [hdel]
  omega

/-- The selected apex is exactly one feedback unit and the remainder has
feedback coordinate zero. -/
theorem feedbackDeletion_eq_one_of_apex_forest
    (G : SimpleGraph V) (v : V)
    (hdelete :
      (GraphConjecture40FeedbackRecursion.deleteVertex G v).IsAcyclic)
    (hcyclic : ¬G.IsAcyclic) :
    GraphConjecture40Deficiency.feedbackDeletion G = 1 := by
  have heq := forest_eq_of_deleteVertex_isAcyclic_of_not_isAcyclic
    G v hdelete hcyclic
  have hsucc :=
    GraphConjecture40FeedbackRecursion.feedbackDeletion_eq_succ_of_forest_eq
      G v heq
  have hzero : GraphConjecture40Deficiency.feedbackDeletion
      (GraphConjecture40FeedbackRecursion.deleteVertex G v) = 0 := by
    unfold GraphConjecture40Deficiency.feedbackDeletion
    rw [GraphConjecture40Deficiency.largestInducedForestSize_eq_card_of_isAcyclic
      _ hdelete]
    omega
  omega

/-- Terminal cactus-feedback recursion: the structural apex-forest hypotheses
discharge the `hforest` premise of v0.19 automatically. -/
theorem conjecture40_of_apex_forest_leaf_step
    (G : SimpleGraph V) (hG : G.IsBipartite)
    (v : V)
    (hdelete :
      (GraphConjecture40FeedbackRecursion.deleteVertex G v).IsAcyclic)
    (hcyclic : ¬G.IsAcyclic)
    (P : Finset (Finset V))
    (hP : GraphConjecture40PathFamily.IsPathSupportFamily G P)
    (hrank : P.card + 1 ≤
      (GraphConjecture40PathFamily.coveredVertices P).card)
    (L : GraphConjecture40LeafBlockStep.LeafBlockStep G P) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hforest := forest_eq_of_deleteVertex_isAcyclic_of_not_isAcyclic
    G v hdelete hcyclic
  have hrem : GraphConjecture40Deficiency.feedbackDeletion
      (GraphConjecture40FeedbackRecursion.deleteVertex G v) = 0 := by
    unfold GraphConjecture40Deficiency.feedbackDeletion
    rw [GraphConjecture40Deficiency.largestInducedForestSize_eq_card_of_isAcyclic
      _ hdelete]
    omega
  exact GraphConjecture40FeedbackRecursion.conjecture40_of_independent_feedback_leaf
    G hG v hrem hforest P hP hrank L

end WrittenOnTheWallII.GraphConjecture40CactusFeedbackUnit
