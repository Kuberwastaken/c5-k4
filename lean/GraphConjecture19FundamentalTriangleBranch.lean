import GraphConjecture19GeodesicSaturation

/-!
# WOWII 19/13: the common-neighbor fundamental-triangle branch
-/

namespace WrittenOnTheWallII.GraphConjecture19FundamentalTriangleBranch

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19FundamentalCycle
open WrittenOnTheWallII.GraphConjecture19ExtremalSaturation

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- A common neighbor of the endpoints of the added edge is joined to the
left endpoint already in the spanning tree. -/
lemma tree_adj_extraLeft_of_common_neighbor
    {G : SimpleGraph V} (D : TreePlusOneEdge G) {c : V}
    (hcLeft : G.Adj c D.extraLeft) (hcRight : G.Adj c D.extraRight) :
    D.tree.Adj c D.extraLeft := by
  rcases D.adj_iff.mp hcLeft with htree | hextra
  · exact htree
  · rcases hextra with hforward | hbackward
    · exact (D.endpoints_ne hforward.2).elim
    · exact (hcRight.ne hbackward.1).elim

omit [Fintype V] [DecidableEq V] in
/-- A common neighbor of the endpoints of the added edge is joined to the
right endpoint already in the spanning tree. -/
lemma tree_adj_extraRight_of_common_neighbor
    {G : SimpleGraph V} (D : TreePlusOneEdge G) {c : V}
    (hcLeft : G.Adj c D.extraLeft) (hcRight : G.Adj c D.extraRight) :
    D.tree.Adj c D.extraRight := by
  rcases D.adj_iff.mp hcRight with htree | hextra
  · exact htree
  · rcases hextra with hforward | hbackward
    · exact (hcLeft.ne hforward.1).elim
    · exact (D.endpoints_ne hbackward.2.symm).elim

omit [Fintype V] [DecidableEq V] in
/-- If the added-edge endpoints have a common neighbor in the full graph,
then the unique spanning-tree path between them has length two.  Consequently
the fundamental cycle obtained by restoring the added edge is a triangle. -/
theorem fundamentalPath_length_eq_two_of_common_neighbor
    {G : SimpleGraph V} (D : TreePlusOneEdge G) {c : V}
    (hcLeft : G.Adj c D.extraLeft) (hcRight : G.Adj c D.extraRight)
    (p : D.tree.Walk D.extraRight D.extraLeft) (hp : p.IsPath) :
    p.length = 2 := by
  have hcL : D.tree.Adj c D.extraLeft :=
    tree_adj_extraLeft_of_common_neighbor D hcLeft hcRight
  have hcR : D.tree.Adj c D.extraRight :=
    tree_adj_extraRight_of_common_neighbor D hcLeft hcRight
  let q : D.tree.Walk D.extraRight D.extraLeft :=
    hcR.symm.toWalk.append hcL.toWalk
  have hqLength : q.length = 2 := by
    simp [q]
  have hupper : D.tree.dist D.extraRight D.extraLeft ≤ 2 := by
    simpa [hqLength] using D.tree.dist_le q
  have hlower : 1 < D.tree.dist D.extraRight D.extraLeft := by
    apply D.tree_connected.one_lt_dist_of_ne_of_not_adj
    · exact D.endpoints_ne.symm
    · simpa [adj_comm] using D.extra_not_tree
  have hdist : D.tree.dist D.extraRight D.extraLeft = 2 := by omega
  obtain ⟨shortest, hshortestPath, hshortestLength⟩ :=
    D.tree_connected.exists_path_of_dist D.extraRight D.extraLeft
  have hpEq : p = shortest :=
    WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.fundamentalPath_unique
      D p shortest hp hshortestPath
  rw [hpEq, hshortestLength, hdist]

omit [DecidableEq V] in
/-- In any decomposition whose fundamental tree path has length at least four
(equivalently, whose fundamental cycle has length at least five), the added
edge endpoints cannot both lie in one open neighborhood.  This excludes the
both-in-`N` subcase of either extremal saturation branch. -/
theorem not_both_fundamental_endpoints_mem_neighborhood_of_four_le
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (c : V)
    (hlong : ∀ (p : D.tree.Walk D.extraRight D.extraLeft),
      p.IsPath → 4 ≤ p.length) :
    ¬(D.extraLeft ∈ G.neighborFinset c ∧
      D.extraRight ∈ G.neighborFinset c) := by
  rintro ⟨hLeft, hRight⟩
  obtain ⟨p, hp, _hunique⟩ :=
    WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.existsUnique_fundamentalPath
      D
  have hpTwo := fundamentalPath_length_eq_two_of_common_neighbor D
    (by simpa [mem_neighborFinset] using hLeft)
    (by simpa [mem_neighborFinset] using hRight) p hp
  have := hlong p hp
  omega

/-- Apply the preceding cycle-incidence exclusion directly to an on-path
saturated classification: for a nontriangular fundamental odd cycle, at
least one added-edge endpoint must be carried by the diametral path itself. -/
theorem endpoint_mem_path_of_on_path_saturation_of_four_le
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (P : Finset V) (c : V)
    (hsat : P ∪ G.neighborFinset c = Finset.univ)
    (hlong : ∀ (p : D.tree.Walk D.extraRight D.extraLeft),
      p.IsPath → 4 ≤ p.length) :
    D.extraLeft ∈ P ∨ D.extraRight ∈ P := by
  have hend := fundamental_endpoints_classified_of_on_path_saturation
    D P (G.neighborFinset c) hsat
  rcases hend.1 with hLeftP | hLeftN
  · exact Or.inl hLeftP
  rcases hend.2 with hRightP | hRightN
  · exact Or.inr hRightP
  exact (not_both_fundamental_endpoints_mem_neighborhood_of_four_le
    D c hlong ⟨hLeftN, hRightN⟩).elim

end WrittenOnTheWallII.GraphConjecture19FundamentalTriangleBranch
