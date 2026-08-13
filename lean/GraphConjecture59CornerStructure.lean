import GraphConjecture59Corner

/-!
# WOWII 59: structure of the exact low-residue corner

This file records two exact consequences of a hypothetical
`(residue,b,f) = (3,6,4)` graph.

First, every one-vertex deletion from a six-vertex maximum induced bipartite
witness remains bipartite but must contain a cycle.  Thus the corner requires a
six-vertex bipartite graph all of whose five-vertex cards are cyclic.

Second, the two dense degree profiles surviving the complete six-vertex
bipartite micro-audit, namely those of `K3,3` and `K3,3` minus one edge, both
have Havel--Hakimi residue exactly two.  Hence neither profile can occur as the
whole degree profile of a residue-three graph.
-/

namespace WrittenOnTheWallII.GraphConjecture59CornerStructure

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- A local name for the descending degree list used definitionally by
`residue`. -/
noncomputable def descendingDegreeSequence
    (G : SimpleGraph V) [DecidableRel G.Adj] : List ℕ :=
  (Finset.univ.val.map fun v ↦ G.degree v).sort (· ≥ ·)

omit [Fintype V] in
/-- An induced-bipartite witness remains bipartite after restricting its
vertex set. -/
theorem induced_bipartite_mono
    (G : SimpleGraph V) {T S : Finset V} (hTS : T ⊆ S)
    (hS : (G.induce (S : Set V)).IsBipartite) :
    (G.induce (T : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring] at hS ⊢
  obtain ⟨c, hc⟩ := hS
  exact ⟨c, fun x hx y hy hxy ↦ hc x (hTS hx) y (hTS hy) hxy⟩

/-- If the maximum induced forest has order four, deleting any vertex from a
six-set cannot leave an induced forest. -/
theorem single_deletion_not_acyclic_of_six_of_forest_eq_four
    (G : SimpleGraph V) (S : Finset V)
    (hSsix : S.card = 6)
    (hf : G.largestInducedForestSize = 4)
    {v : V} (hv : v ∈ S) :
    ¬(G.induce ((S.erase v : Finset V) : Set V)).IsAcyclic := by
  intro hacyclic
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G (S.erase v) hacyclic
  rw [card_erase_of_mem hv, hSsix, hf] at hbound
  omega

/-- Exact obstruction forced on a maximum six-vertex bipartite witness by
`f(G)=4`: every one-vertex card is bipartite and cyclic. -/
theorem every_single_deletion_bipartite_and_cyclic
    (G : SimpleGraph V) (S : Finset V)
    (hSbip : (G.induce (S : Set V)).IsBipartite)
    (hSsix : S.card = 6)
    (hf : G.largestInducedForestSize = 4)
    {v : V} (hv : v ∈ S) :
    (G.induce ((S.erase v : Finset V) : Set V)).IsBipartite ∧
      ¬(G.induce ((S.erase v : Finset V) : Set V)).IsAcyclic := by
  refine ⟨induced_bipartite_mono G (erase_subset v S) hSbip, ?_⟩
  exact single_deletion_not_acyclic_of_six_of_forest_eq_four
    G S hSsix hf hv

omit [DecidableEq V] in
/-- The cubic six-vertex profile of `K3,3` has residue two. -/
theorem residue_eq_two_of_cubic_six_profile
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hdeg : descendingDegreeSequence G = [3, 3, 3, 3, 3, 3]) :
    residue G = 2 := by
  unfold descendingDegreeSequence at hdeg
  unfold residue
  rw [hdeg]
  native_decide

omit [DecidableEq V] in
/-- The six-vertex degree profile of `K3,3` minus one edge also has residue
two. -/
theorem residue_eq_two_of_almost_cubic_six_profile
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hdeg : descendingDegreeSequence G = [3, 3, 3, 3, 2, 2]) :
    residue G = 2 := by
  unfold descendingDegreeSequence at hdeg
  unfold residue
  rw [hdeg]
  native_decide

omit [DecidableEq V] in
/-- Neither dense `K3,3`-like six-vertex profile can realize residue three. -/
theorem dense_six_profiles_exclude_residue_three
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hdeg : descendingDegreeSequence G = [3, 3, 3, 3, 3, 3] ∨
      descendingDegreeSequence G = [3, 3, 3, 3, 2, 2]) :
    residue G ≠ 3 := by
  rcases hdeg with hdeg | hdeg
  · rw [residue_eq_two_of_cubic_six_profile G hdeg]
    decide
  · rw [residue_eq_two_of_almost_cubic_six_profile G hdeg]
    decide

end WrittenOnTheWallII.GraphConjecture59CornerStructure
