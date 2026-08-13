import GraphConjecture19UnicyclicDecomposition

/-!
# WOWII 19/13: fundamental path of a tree-plus-one-edge graph
-/

namespace WrittenOnTheWallII.GraphConjecture19FundamentalCycle

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- The spanning tree has a unique simple path between the added edge's
endpoints. -/
theorem TreePlusOneEdge.existsUnique_fundamentalPath
    {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    ∃! p : D.tree.Walk D.extraRight D.extraLeft, p.IsPath := by
  exact (⟨D.tree_connected, D.tree_acyclic⟩ : D.tree.IsTree).existsUnique_path
    D.extraRight D.extraLeft

omit [Fintype V] [DecidableEq V] in
/-- The added edge does not occur on any spanning-tree walk. -/
theorem TreePlusOneEdge.extraEdge_not_mem_treeWalk
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {a b : V} (p : D.tree.Walk a b) :
    s(D.extraLeft, D.extraRight) ∉ p.edges := by
  intro he
  exact D.extra_not_tree (p.adj_of_mem_edges he)

omit [Fintype V] [DecidableEq V] in
/-- The spanning tree is a subgraph of the unicyclic graph. -/
theorem TreePlusOneEdge.tree_le
    {G : SimpleGraph V} (D : TreePlusOneEdge G) : D.tree ≤ G := by
  intro a b hab
  exact D.adj_iff.mpr (Or.inl hab)

omit [Fintype V] [DecidableEq V] in
/-- The added edge is genuinely present in the full graph. -/
theorem TreePlusOneEdge.extra_adj
    {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    G.Adj D.extraLeft D.extraRight := by
  exact D.adj_iff.mpr (Or.inr (Or.inl ⟨rfl, rfl⟩))

omit [Fintype V] [DecidableEq V] in
/-- A canonical finite fundamental-path support exists, is nodup, contains
both added-edge endpoints, and has one more vertex than path edges. -/
theorem TreePlusOneEdge.exists_fundamentalSupport
    {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    ∃ (p : D.tree.Walk D.extraRight D.extraLeft),
      p.IsPath ∧
      p.support.Nodup ∧
      D.extraRight ∈ p.support ∧
      D.extraLeft ∈ p.support ∧
      p.support.length = p.length + 1 ∧
      s(D.extraLeft, D.extraRight) ∉ p.edges := by
  obtain ⟨p, hp, _huniq⟩ := existsUnique_fundamentalPath D
  exact ⟨p, hp, hp.support_nodup, p.start_mem_support, p.end_mem_support,
    p.length_support, extraEdge_not_mem_treeWalk D p⟩

omit [Fintype V] [DecidableEq V] in
/-- Any other simple tree path between the added-edge endpoints is the
fundamental path.  This is the uniqueness bridge needed by later cycle-core
surplus arguments. -/
theorem TreePlusOneEdge.fundamentalPath_unique
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    (p q : D.tree.Walk D.extraRight D.extraLeft)
    (hp : p.IsPath) (hq : q.IsPath) : p = q := by
  exact Subtype.mk.inj (D.tree_acyclic.path_unique ⟨p, hp⟩ ⟨q, hq⟩)

end WrittenOnTheWallII.GraphConjecture19FundamentalCycle
