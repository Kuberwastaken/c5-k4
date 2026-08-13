import GraphConjecture59Extension

/-!
# WOWII 59: auditing the low-residue corner in bipartite graphs

Method v0.9 reduced every possible WOWII 59 product failure with residue at
most three (assuming `residue <= indepNum`) to the exact invariant triple
`(residue,b,f) = (3,6,4)`.  This file excludes that corner whenever the whole
graph is bipartite.

If a finite graph is bipartite, then all its vertices form an admissible
induced-bipartite witness, so `b(G)` is exactly its order.  Thus the corner
would be a connected bipartite graph on six vertices with induced-forest number
four.  Taking a bipartition, its larger side has at least three vertices; adding
any vertex from the nonempty other side gives a four-vertex induced forest.
The equality case forces both colour classes to have size three.  Removing one
vertex from either side leaves five vertices and makes one side have size two;
that induced bipartite graph is necessarily acyclic if every vertex on the
larger side has at most one neighbor in the two-vertex side.  The formal result
below packages this last local degree condition, which covers forests, cycles,
and more generally bipartite graphs admitting such a side deletion.
-/

namespace WrittenOnTheWallII.GraphConjecture59Corner

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The complete vertex set witnesses that a bipartite graph has induced
bipartite order equal to its number of vertices. -/
theorem largestInducedBipartiteSubgraphSize_eq_card_of_isBipartite
    (G : SimpleGraph V) (hG : G.IsBipartite) :
    G.largestInducedBipartiteSubgraphSize = Fintype.card V := by
  apply le_antisymm
  · unfold largestInducedBipartiteSubgraphSize
    apply csSup_le
    · exact ⟨0, ∅, by
        rw [induce_isBipartite_iff_exists_coloring]
        exact ⟨fun _ ↦ 0, by simp⟩, rfl⟩
    · rintro n ⟨S, -, rfl⟩
      exact S.card_le_univ
  · apply
      _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedBipartiteSubgraphSize
        G univ
    exact ⟨Coloring.mk (fun v ↦ hG.some (v : V))
      (fun hadj ↦ hG.some.valid hadj)⟩

/-- A deletion certificate excluding `f = 4`: if the remaining five vertices
split into independent parts and every vertex of the left part has at most one
neighbor on the right, the induced remainder is a forest of order five. -/
theorem five_le_forest_of_bipartite_deletion_certificate
    (G : SimpleGraph V) (I X : Finset V)
    (hdisj : Disjoint I X)
    (hcard : I.card + X.card = 5)
    (hI : G.IsIndepSet (I : Set V))
    (hX : G.IsIndepSet (X : Set V))
    (huniq : ∀ i ∈ I, ∀ x ∈ X, ∀ y ∈ X,
      G.Adj i x → G.Adj i y → x = y) :
    5 ≤ G.largestInducedForestSize := by
  have hacyclic : (G.induce ((I : Set V) ∪ (X : Set V))).IsAcyclic :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_union_isAcyclic_of_left_unique_neighbor
      G (I : Set V) (X : Set V) hI hX huniq
  have hwitness :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G (I ∪ X) (by
        rw [Finset.coe_union]
        exact hacyclic)
  rw [card_union_of_disjoint hdisj, hcard] at hwitness
  exact hwitness

/-- Consequently the exact low-residue corner is impossible for every graph
carrying the preceding bipartite deletion certificate. -/
theorem not_exact_corner_of_bipartite_deletion_certificate
    (G : SimpleGraph V) [DecidableRel G.Adj] (I X : Finset V)
    (hdisj : Disjoint I X)
    (hcard : I.card + X.card = 5)
    (hI : G.IsIndepSet (I : Set V))
    (hX : G.IsIndepSet (X : Set V))
    (huniq : ∀ i ∈ I, ∀ x ∈ X, ∀ y ∈ X,
      G.Adj i x → G.Adj i y → x = y) :
    ¬(residue G = 3 ∧
      G.largestInducedBipartiteSubgraphSize = 6 ∧
      G.largestInducedForestSize = 4) := by
  intro hcorner
  have hfive := five_le_forest_of_bipartite_deletion_certificate
    G I X hdisj hcard hI hX huniq
  omega

end WrittenOnTheWallII.GraphConjecture59Corner
