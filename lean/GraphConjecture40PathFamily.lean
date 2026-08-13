import GraphConjecture40LinearForest

/-!
# WOWII 40: disjoint path families

This file replaces the single path of v0.12 by a finite family of pairwise
disjoint path supports. Adding singleton paths on the uncovered vertices
turns such a family into a spanning path cover, with exact rank
`covered vertices - path components`.
-/

namespace WrittenOnTheWallII.GraphConjecture40PathFamily

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- A finite family whose members are nonempty, pairwise disjoint supports of
paths in `G`. -/
def IsPathSupportFamily (G : SimpleGraph V) (P : Finset (Finset V)) : Prop :=
  (∀ s₁ ∈ P, ∀ s₂ ∈ P, s₁ ≠ s₂ → Disjoint s₁ s₂) ∧
  (∀ s ∈ P, ∃ (a z : V) (p : G.Walk a z),
    p.IsPath ∧ s = p.support.toFinset)

def coveredVertices (P : Finset (Finset V)) : Finset V :=
  P.biUnion id

def spanningCompletion (P : Finset (Finset V)) : Finset (Finset V) :=
  P ∪ ((Finset.univ \ coveredVertices P).image fun x ↦ {x})

omit [Fintype V] in
lemma mem_coveredVertices_iff {P : Finset (Finset V)} {x : V} :
    x ∈ coveredVertices P ↔ ∃ s ∈ P, x ∈ s := by
  simp [coveredVertices]

/-- Completing a disjoint path-support family by uncovered singletons gives
an actual repository `IsPathCover`. -/
theorem spanningCompletion_isPathCover
    (G : SimpleGraph V) (P : Finset (Finset V))
    (hP : IsPathSupportFamily G P) :
    IsPathCover G (spanningCompletion P) := by
  rcases hP with ⟨hdisj, hpaths⟩
  refine ⟨?_, ?_, ?_⟩
  · intro s₁ hs₁ s₂ hs₂ hne
    simp only [spanningCompletion, mem_union, mem_image, mem_sdiff,
      mem_univ, true_and] at hs₁ hs₂
    rcases hs₁ with hs₁P | ⟨x, hxU, rfl⟩
    · rcases hs₂ with hs₂P | ⟨y, hyU, rfl⟩
      · exact hdisj s₁ hs₁P s₂ hs₂P hne
      · rw [Finset.disjoint_singleton_right]
        intro hy
        exact hyU (mem_coveredVertices_iff.mpr ⟨s₁, hs₁P, hy⟩)
    · rcases hs₂ with hs₂P | ⟨y, hyU, rfl⟩
      · rw [Finset.disjoint_singleton_left]
        intro hx
        exact hxU (mem_coveredVertices_iff.mpr ⟨s₂, hs₂P, hx⟩)
      · simpa using hne
  · intro x _
    by_cases hx : x ∈ coveredVertices P
    · obtain ⟨s, hsP, hxs⟩ := mem_coveredVertices_iff.mp hx
      exact mem_biUnion.mpr ⟨s, mem_union_left _ hsP, hxs⟩
    · exact mem_biUnion.mpr ⟨{x}, mem_union_right _ (mem_image.mpr
        ⟨x, by simp [hx], rfl⟩), by simp⟩
  · intro s hs
    simp only [spanningCompletion, mem_union, mem_image, mem_sdiff,
      mem_univ, true_and] at hs
    rcases hs with hsP | ⟨x, -, rfl⟩
    · exact hpaths s hsP
    · exact ⟨x, x, .nil, Walk.IsPath.nil, by simp⟩

/-- No member of a path-support family is one of the newly added uncovered
singletons. -/
lemma disjoint_completion_singletons
    (P : Finset (Finset V)) :
    Disjoint P ((Finset.univ \ coveredVertices P).image fun x ↦ {x}) := by
  rw [Finset.disjoint_left]
  intro s hsP hsI
  simp only [mem_image, mem_sdiff, mem_univ, true_and] at hsI
  obtain ⟨x, hxU, rfl⟩ := hsI
  exact hxU (mem_coveredVertices_iff.mpr ⟨{x}, hsP, by simp⟩)

/-- Exact cardinality of the spanning completion. -/
theorem spanningCompletion_card_add_covered
    (P : Finset (Finset V)) :
    (spanningCompletion P).card + (coveredVertices P).card =
      Fintype.card V + P.card := by
  have hd := disjoint_completion_singletons P
  unfold spanningCompletion
  rw [card_union_of_disjoint hd, card_image_of_injective]
  · rw [card_sdiff_of_subset (Finset.subset_univ _), card_univ]
    have hc : (coveredVertices P).card ≤ Fintype.card V :=
      (coveredVertices P).card_le_univ
    omega
  · intro x y h
    simpa using h

/-- A disjoint path family with rank at least `r` gives
`pathCoverNumber + r <= n`. Here rank is certified without subtraction by
`P.card + r <= coveredVertices.card`. -/
theorem pathCoverNumber_add_le_card_of_pathFamily
    (G : SimpleGraph V) (P : Finset (Finset V))
    (hP : IsPathSupportFamily G P) {r : ℕ}
    (hrank : P.card + r ≤ (coveredVertices P).card) :
    pathCoverNumber G + r ≤ Fintype.card V := by
  have hcover := spanningCompletion_isPathCover G P hP
  have hle :=
    GraphConjecture40PathCoverAPI.pathCoverNumber_le_card_of_isPathCover
      G _ hcover
  have hc := spanningCompletion_card_add_covered P
  omega

/-- Generic path-family sufficient condition for the bipartite deficiency
base, at arbitrary feedback-deletion coordinate. -/
theorem conjecture40_of_bipartite_of_pathFamily_rank
    (G : SimpleGraph V) (hG : G.IsBipartite)
    {k : ℕ}
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = k)
    (P : Finset (Finset V)) (hP : IsPathSupportFamily G P)
    (hrank : P.card + (2 * k + 1) ≤ (coveredVertices P).card) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hprank := pathCoverNumber_add_le_card_of_pathFamily
    G P hP hrank
  have hB : G.largestInducedBipartiteSubgraphSize = Fintype.card V := by
    apply le_antisymm
      (GraphConjecture40Deficiency.largestInducedBipartiteSubgraphSize_le_card G)
    simpa using
      GraphConjecture40Baseline.card_le_largestInducedBipartiteSubgraphSize
        G (Finset.univ : Finset V) (by
          rw [induce_isBipartite_iff_exists_coloring]
          obtain ⟨c⟩ := hG
          exact ⟨fun x ↦ c x, by
            intro u _ v _ huv
            exact c.valid huv⟩)
  apply GraphConjecture40Deficiency.conjecture40_of_deficiency_bound G
    (GraphConjecture40PathCoverAPI.pathCoverNumber_le_card G)
  unfold GraphConjecture40Deficiency.feedbackDeletion at htau
  unfold GraphConjecture40Deficiency.feedbackDeletion
    GraphConjecture40Deficiency.oddDeletion
    GraphConjecture40Deficiency.linearForestRank
  rw [hB]
  omega

end WrittenOnTheWallII.GraphConjecture40PathFamily
