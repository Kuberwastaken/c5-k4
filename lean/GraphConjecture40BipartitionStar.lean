import GraphConjecture40Baseline

/-!
# WOWII 40: the bipartition-star obstruction

For two nonempty disjoint independent vertex classes, the larger class
together with one vertex of the opposite class induces a forest.  This is the
structural obstruction met by the cross-petal search: a balanced bipartite
graph always has an induced forest of at least half its order plus one.
-/

namespace WrittenOnTheWallII.GraphConjecture40BipartitionStar

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40Baseline

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- The larger of two nonempty disjoint independent classes, together with
one vertex from the other class, is an explicit induced forest of order
`max A.card B.card + 1`.  No connectivity or covering hypothesis is needed. -/
theorem exists_inducedForest_card_max_add_one
    (G : SimpleGraph V) (A B : Finset V)
    (hA : G.IsIndepSet (A : Set V))
    (hB : G.IsIndepSet (B : Set V))
    (hAB : Disjoint A B) (hAne : A.Nonempty) (hBne : B.Nonempty) :
    ∃ S : Finset V,
      (G.induce (S : Set V)).IsAcyclic ∧
      S.card = max A.card B.card + 1 := by
  rcases le_total A.card B.card with hle | hle
  · obtain ⟨v, hvA⟩ := hAne
    have hvB : v ∉ B := by
      exact fun hvB ↦ Finset.disjoint_left.mp hAB hvA hvB
    refine ⟨insert v B, induce_insert_isAcyclic_of_indep G B v hB, ?_⟩
    rw [card_insert_of_notMem hvB, max_eq_right hle]
  · obtain ⟨v, hvB⟩ := hBne
    have hvA : v ∉ A := by
      exact fun hvA ↦ Finset.disjoint_left.mp hAB hvA hvB
    refine ⟨insert v A, induce_insert_isAcyclic_of_indep G A v hA, ?_⟩
    rw [card_insert_of_notMem hvA, max_eq_left hle]

/-- In invariant form, two nonempty disjoint independent classes force the
maximum induced-forest order to exceed their larger cardinality. -/
theorem max_card_add_one_le_largestInducedForestSize
    (G : SimpleGraph V) (A B : Finset V)
    (hA : G.IsIndepSet (A : Set V))
    (hB : G.IsIndepSet (B : Set V))
    (hAB : Disjoint A B) (hAne : A.Nonempty) (hBne : B.Nonempty) :
    max A.card B.card + 1 ≤ G.largestInducedForestSize := by
  obtain ⟨S, hforest, hcard⟩ :=
    exists_inducedForest_card_max_add_one G A B hA hB hAB hAne hBne
  rw [← hcard]
  exact card_le_largestInducedForestSize G S hforest

/-- A balanced bipartition of the full finite vertex set gives the familiar
half-order-plus-one induced-forest lower bound. -/
theorem balanced_part_card_add_one_le_largestInducedForestSize
    (G : SimpleGraph V) (A B : Finset V)
    (hA : G.IsIndepSet (A : Set V))
    (hB : G.IsIndepSet (B : Set V))
    (hAB : Disjoint A B) (hAne : A.Nonempty) (hBne : B.Nonempty)
    (hbalanced : A.card = B.card) :
    A.card + 1 ≤ G.largestInducedForestSize := by
  have h := max_card_add_one_le_largestInducedForestSize
    G A B hA hB hAB hAne hBne
  simpa [hbalanced] using h

/-- Exact WOWII #40 arithmetic for a balanced full bipartition when the
bipartite invariant is the full order and the path-cover number is one.

The hypotheses expose the two invariant equalities used by the computational
obstruction rather than silently deriving them from incompatible APIs. -/
theorem conjecture40_of_balanced_full_bipartition
    (G : SimpleGraph V) (A B : Finset V)
    (hA : G.IsIndepSet (A : Set V))
    (hB : G.IsIndepSet (B : Set V))
    (hAB : Disjoint A B) (hAne : A.Nonempty) (hBne : B.Nonempty)
    (hcover : A ∪ B = Finset.univ)
    (hbalanced : A.card = B.card)
    (hb : b G = Fintype.card V)
    (hp : pathCoverNumber G = 1) :
    ⌈(((pathCoverNumber G : ℝ) + b G + 1) / 2)⌉ ≤
      G.largestInducedForestSize := by
  have hforest : A.card + 1 ≤ G.largestInducedForestSize :=
    balanced_part_card_add_one_le_largestInducedForestSize
      G A B hA hB hAB hAne hBne hbalanced
  have hcard : Fintype.card V = A.card + B.card := by
    rw [← card_univ, ← hcover, card_union_of_disjoint hAB]
  have horder : Fintype.card V = 2 * A.card := by
    omega
  have hforestR :
      ((A.card + 1 : ℕ) : ℝ) ≤ (G.largestInducedForestSize : ℝ) := by
    exact_mod_cast hforest
  rw [Int.ceil_le, hp, hb]
  rw [horder]
  convert hforestR using 1
  all_goals push_cast
  all_goals ring

end WrittenOnTheWallII.GraphConjecture40BipartitionStar
