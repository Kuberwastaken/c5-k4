import GraphConjecture19CenterEqualityIncidence
import GraphConjecture19DistanceTwoRoute

/-!
# WOWII 19/13: center-attained off-path attachment classification
-/

namespace WrittenOnTheWallII.GraphConjecture19CenterAttachmentClassification

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19DistanceTwoRoute

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Saturation forces every vertex outside `P` into the center's open
neighborhood. -/
lemma off_path_mem_center_neighborhood
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (P : Finset V) (c z : V)
    (hsat : P ∪ G.neighborFinset c = Finset.univ)
    (hzOff : z ∉ P) :
    z ∈ G.neighborFinset c := by
  have hzCover : z ∈ P ∪ G.neighborFinset c := by
    rw [hsat]
    simp
  exact (Finset.mem_union.mp hzCover).resolve_left hzOff

omit [Fintype V] [DecidableEq V] in
/-- In the orientation `extraLeft = c`, the center edge to an off-path vertex
other than `extraRight` is a tree edge. -/
lemma tree_adj_center_offVertex_of_ne_extraRight
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    (c z : V) (hc : D.extraLeft = c)
    (hzRight : z ≠ D.extraRight) (hcz : G.Adj c z) :
    D.tree.Adj c z := by
  rcases D.adj_iff.mp hcz with htree | hextra
  · exact htree
  · rcases hextra with hforward | hbackward
    · exact (hzRight hforward.2).elim
    · exact (D.endpoints_ne (hc.trans hbackward.1)).elim

omit [Fintype V] [DecidableEq V] in
/-- If `extraRight` is off `P`, any edge from an off-path vertex to a
noncenter path vertex must be a tree edge. -/
lemma tree_adj_offVertex_pathVertex_of_center_orientation
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    (P : Finset V) (c z x : V)
    (hc : D.extraLeft = c) (hRightOff : D.extraRight ∉ P)
    (hxP : x ∈ P) (hxCenter : x ≠ c) (hzx : G.Adj z x) :
    D.tree.Adj z x := by
  rcases D.adj_iff.mp hzx with htree | hextra
  · exact htree
  · rcases hextra with hforward | hbackward
    · exact (hRightOff (hforward.2 ▸ hxP)).elim
    · exact (hxCenter (hbackward.2.trans hc)).elim

/-- Complete local attachment classification in the center-attained equality
branch.  Every off-path vertex is adjacent to `c`; except for the added-edge
endpoint this center edge lies in the tree; and every noncenter neighbor of an
off-path vertex lies on `P` via a tree edge. -/
theorem classify_off_path_attachments_center_left
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (P : Finset V) (c : V)
    (hc : D.extraLeft = c)
    (hRightOff : D.extraRight ∉ P)
    (hsat : P ∪ G.neighborFinset c = Finset.univ)
    (hcenter : G.IsIndepSet (G.neighborSet c)) :
    ∀ z ∈ Finset.univ \ P,
      G.Adj c z ∧
      (z ≠ D.extraRight → D.tree.Adj c z) ∧
      ∀ x : V, G.Adj z x → x ≠ c →
        x ∈ P ∧ D.tree.Adj z x := by
  intro z hz
  have hzOff : z ∉ P := (Finset.mem_sdiff.mp hz).2
  have hzN := off_path_mem_center_neighborhood P c z hsat hzOff
  have hcz : G.Adj c z := by simpa [mem_neighborFinset] using hzN
  refine ⟨hcz, ?_, ?_⟩
  · intro hzRight
    exact tree_adj_center_offVertex_of_ne_extraRight D c z hc hzRight hcz
  · intro x hzx hxCenter
    have hxCover : x ∈ P ∪ G.neighborFinset c := by
      rw [hsat]
      simp
    have hxP : x ∈ P := by
      rcases Finset.mem_union.mp hxCover with hxP | hxN
      · exact hxP
      · have hzSet : z ∈ G.neighborSet c := by
          simpa [mem_neighborFinset] using hzN
        have hxSet : x ∈ G.neighborSet c := by
          simpa [mem_neighborFinset] using hxN
        exact (hcenter hzSet hxSet hzx.ne hzx).elim
    exact ⟨hxP,
      tree_adj_offVertex_pathVertex_of_center_orientation
        D P c z x hc hRightOff hxP hxCenter hzx⟩

/-- The distinct full-independent maximum-neighborhood witness is itself
located by saturation: it lies on `P` or is adjacent to `c`. -/
theorem distinct_maxNeighborhood_witness_path_or_center_neighbor
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (P : Finset V) (c v : V)
    (hsat : P ∪ G.neighborFinset c = Finset.univ) :
    v ∈ P ∨ G.Adj c v := by
  have hv : v ∈ P ∪ G.neighborFinset c := by
    rw [hsat]
    simp
  rcases Finset.mem_union.mp hv with hvP | hvN
  · exact Or.inl hvP
  · exact Or.inr (by simpa [mem_neighborFinset] using hvN)

end WrittenOnTheWallII.GraphConjecture19CenterAttachmentClassification
