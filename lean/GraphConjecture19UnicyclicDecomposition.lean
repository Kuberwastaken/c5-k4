import FormalConjecturesUtil

/-!
# WOWII 19/13: a conventional tree-plus-one-edge unicyclic decomposition
-/

namespace WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- A portable conventional presentation of a connected unicyclic graph: a
spanning tree plus one edge not present in that tree. -/
structure TreePlusOneEdge (G : SimpleGraph V) where
  tree : SimpleGraph V
  tree_connected : tree.Connected
  tree_acyclic : tree.IsAcyclic
  extraLeft : V
  extraRight : V
  endpoints_ne : extraLeft ≠ extraRight
  extra_not_tree : ¬tree.Adj extraLeft extraRight
  adj_iff : ∀ {a b : V}, G.Adj a b ↔
    tree.Adj a b ∨
      (a = extraLeft ∧ b = extraRight) ∨
      (a = extraRight ∧ b = extraLeft)

/-- The conventional class predicate: `G` admits a spanning-tree-plus-one-edge
presentation. -/
def IsUnicyclic (G : SimpleGraph V) : Prop := Nonempty (TreePlusOneEdge G)

omit [Fintype V] [DecidableEq V] in
/-- A tree-plus-one-edge presentation is connected because it contains the
spanning tree. -/
theorem TreePlusOneEdge.connected {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    G.Connected := by
  apply D.tree_connected.mono
  intro a b hab
  exact D.adj_iff.mpr (Or.inl hab)

/-- Deleting the first endpoint of the added edge leaves a graph contained in
the spanning tree on the same remaining vertex set. -/
theorem TreePlusOneEdge.induce_erase_endpoint_le_tree
    {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    G.induce (↑(Finset.univ.erase D.extraLeft) : Set V) ≤
      D.tree.induce (↑(Finset.univ.erase D.extraLeft) : Set V) := by
  intro a b hab
  rcases D.adj_iff.mp hab with htree | hextra
  · exact htree
  · rcases hextra with h12 | h21
    · have ha : (a : V) = D.extraLeft := h12.1
      have haMem : (a : V) ∈ Finset.univ.erase D.extraLeft := a.property
      simp [ha] at haMem
    · have hb : (b : V) = D.extraLeft := h21.2
      have hbMem : (b : V) ∈ Finset.univ.erase D.extraLeft := b.property
      simp [hb] at hbMem

/-- The endpoint-deleted induced graph is acyclic. -/
theorem TreePlusOneEdge.induce_erase_endpoint_acyclic
    {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    (G.induce (↑(Finset.univ.erase D.extraLeft) : Set V)).IsAcyclic := by
  apply IsAcyclic.anti D.induce_erase_endpoint_le_tree
  exact D.tree_acyclic.induce _

/-- Hence deleting an endpoint of the unique added edge leaves an induced
bipartite graph. -/
theorem TreePlusOneEdge.induce_erase_endpoint_bipartite
    {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    (G.induce (↑(Finset.univ.erase D.extraLeft) : Set V)).IsBipartite :=
  D.induce_erase_endpoint_acyclic.isBipartite

/-- The conventional class predicate has a genuine one-vertex-deletion
existence theorem, ready to feed any downstream transversal-charge API. -/
theorem IsUnicyclic.exists_delete_vertex_bipartite
    {G : SimpleGraph V} (hG : IsUnicyclic G) :
    ∃ z : V, (G.induce (↑(Finset.univ.erase z) : Set V)).IsBipartite := by
  let D := Classical.choice hG
  exact ⟨D.extraLeft, D.induce_erase_endpoint_bipartite⟩

omit [Fintype V] [DecidableEq V] in
/-- The conventional class predicate also entails connectedness. -/
theorem IsUnicyclic.connected {G : SimpleGraph V} (hG : IsUnicyclic G) :
    G.Connected := by
  exact (Classical.choice hG).connected

end WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
