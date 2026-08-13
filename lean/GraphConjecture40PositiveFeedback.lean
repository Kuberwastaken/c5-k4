import GraphConjecture40PathCoverAPI

/-!
# WOWII 40: a positive-feedback bipartite class

An explicit path on at least four vertices, together with singleton paths on
its complement, gives a path cover with at most `n - 3` members. Combined
with `tau = 1` and bipartiteness, this closes the first positive-feedback
slice of the deficiency inequality.
-/

namespace WrittenOnTheWallII.GraphConjecture40PositiveFeedback

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

def pathSupportCover (S : Finset V) : Finset (Finset V) :=
  insert S ((Finset.univ \ S).image fun x ↦ {x})

/-- A non-singleton path support, together with singleton paths outside it,
is a path cover. -/
lemma pathSupportCover_isPathCover
    (G : SimpleGraph V) {a b : V} (p : G.Walk a b)
    (hp : p.IsPath) (hcard : 2 ≤ p.support.toFinset.card) :
    IsPathCover G (pathSupportCover p.support.toFinset) := by
  let S := p.support.toFinset
  have hS_not_singleton : ∀ x : V, S ≠ {x} := by
    intro x hx
    have := congrArg Finset.card hx
    simp [S] at this
    omega
  refine ⟨?_, ?_, ?_⟩
  · intro s₁ hs₁ s₂ hs₂ hne
    simp only [pathSupportCover, mem_insert, mem_image, mem_sdiff,
      mem_univ, true_and] at hs₁ hs₂
    rcases hs₁ with rfl | ⟨x, hxS, rfl⟩
    · rcases hs₂ with hsame | ⟨y, hyS, rfl⟩
      · exact (hne hsame.symm).elim
      · rw [Finset.disjoint_singleton_right]
        exact hyS
    · rcases hs₂ with hsame | ⟨y, hyS, rfl⟩
      · have hxS' : x ∉ S := hxS
        subst s₂
        rw [Finset.disjoint_singleton_left]
        exact hxS'
      · simpa using hne
  · intro x _
    by_cases hx : x ∈ S
    · apply mem_biUnion.mpr
      refine ⟨S, ?_, hx⟩
      change S ∈ pathSupportCover S
      exact mem_insert_self _ _
    · apply mem_biUnion.mpr
      refine ⟨{x}, ?_, by simp⟩
      change {x} ∈ pathSupportCover S
      apply mem_insert_of_mem
      apply mem_image.mpr
      exact ⟨x, by simp [hx], rfl⟩
  · intro s hs
    simp only [pathSupportCover, mem_insert, mem_image, mem_sdiff,
      mem_univ, true_and] at hs
    rcases hs with hS | ⟨x, -, rfl⟩
    · exact ⟨a, b, p, hp, hS⟩
    · exact ⟨x, x, .nil, Walk.IsPath.nil, by simp⟩

/-- Cardinality of the path-support-plus-singletons cover. -/
lemma pathSupportCover_card (S : Finset V) (hcard : 2 ≤ S.card) :
    (pathSupportCover S).card + S.card = Fintype.card V + 1 := by
  have hle : S.card ≤ Fintype.card V := S.card_le_univ
  have hS_not_image : S ∉
      (Finset.univ \ S).image (fun x : V ↦ ({x} : Finset V)) := by
    intro h
    simp only [mem_image, mem_sdiff, mem_univ, true_and] at h
    obtain ⟨x, -, hx⟩ := h
    have hc := congrArg Finset.card hx
    simp at hc
    omega
  unfold pathSupportCover
  rw [card_insert_of_notMem hS_not_image, card_image_of_injective]
  · rw [card_sdiff_of_subset (Finset.subset_univ S), card_univ]
    omega
  · intro x y h
    simpa using h

/-- A path with at least four vertices pays three units of spanning
linear-forest rank: `pathCoverNumber G + 3 <= n`. -/
theorem pathCoverNumber_add_three_le_card_of_long_path
    (G : SimpleGraph V) {a b : V} (p : G.Walk a b)
    (hp : p.IsPath) (hcard : 4 ≤ p.support.toFinset.card) :
    pathCoverNumber G + 3 ≤ Fintype.card V := by
  have hcover := pathSupportCover_isPathCover G p hp (by omega)
  have hle :=
    GraphConjecture40PathCoverAPI.pathCoverNumber_le_card_of_isPathCover
      G _ hcover
  have hc := pathSupportCover_card (V := V) p.support.toFinset (by omega)
  omega

/-- The first positive-feedback bipartite slice of WOWII 40. Here `f=n-1`
is exactly `tau=1`, bipartiteness gives `o=0`, and a four-vertex path gives
`ell>=3`. -/
theorem conjecture40_of_bipartite_of_feedbackDeletion_eq_one_of_long_path
    (G : SimpleGraph V)
    (hG : G.IsBipartite)
    (htau : GraphConjecture40Deficiency.feedbackDeletion G = 1)
    {a z : V} (p : G.Walk a z) (hp : p.IsPath)
    (hcard : 4 ≤ p.support.toFinset.card) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hp3 := pathCoverNumber_add_three_le_card_of_long_path G p hp hcard
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

end WrittenOnTheWallII.GraphConjecture40PositiveFeedback
