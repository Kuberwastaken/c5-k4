import GraphConjecture19CenterNontriangleContradiction

/-!
# WOWII 19/13: structure when the geodesic traverses the added edge
-/

namespace WrittenOnTheWallII.GraphConjecture19ConsecutiveEdgeStructure

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19EndpointMax
open WrittenOnTheWallII.GraphConjecture19TreeCharge
open WrittenOnTheWallII.GraphConjecture19UnicyclicCharge

universe u

variable {V : Type u}

/-- If the added-edge endpoints occur at indices `i,i+1`, that geodesic step
is exactly the added edge. -/
theorem consecutive_step_is_added_edge
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {a b : V} (p : G.Walk a b) {i : ℕ}
    (hi : i < p.length)
    (hiLeft : p.getVert i = D.extraLeft)
    (hiRight : p.getVert (i + 1) = D.extraRight) :
    G.Adj (p.getVert i) (p.getVert (i + 1)) ∧
      ¬D.tree.Adj (p.getVert i) (p.getVert (i + 1)) := by
  constructor
  · exact p.adj_getVert_succ hi
  · simpa [hiLeft, hiRight] using D.extra_not_tree

/-- Every other geodesic step lies in the spanning tree.  Thus deleting the
single consecutive added-edge step splits the geodesic into two tree arms. -/
theorem tree_adj_getVert_succ_of_ne_added_index
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {a b : V} (p : G.Walk a b) (hp : p.IsPath)
    {i j : ℕ}
    (hi : i < p.length) (hj : j < p.length) (hji : j ≠ i)
    (hiLeft : p.getVert i = D.extraLeft)
    (hiRight : p.getVert (i + 1) = D.extraRight) :
    D.tree.Adj (p.getVert j) (p.getVert (j + 1)) := by
  have hadj := p.adj_getVert_succ hj
  rcases D.adj_iff.mp hadj with htree | hextra
  · exact htree
  · rcases hextra with hforward | hbackward
    · have hjiEq : j = i := hp.getVert_injOn
        (by simp; omega) (by simp; omega)
        (hforward.1.trans hiLeft.symm)
      exact (hji hjiEq).elim
    · have hzero : j = i + 1 := hp.getVert_injOn
        (by simp; omega) (by simp; omega)
        (hbackward.1.trans hiRight.symm)
      have hsuccEq : j + 1 = i := hp.getVert_injOn
        (by simp; omega) (by simp; omega)
        (hbackward.2.trans hiLeft.symm)
      omega

/-- The prefix through the left endpoint and the suffix from the right
endpoint are paths all of whose edges lie in the spanning tree. -/
theorem consecutive_geodesic_tree_arms
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {a b : V} (p : G.Walk a b) (hp : p.IsPath)
    {i : ℕ} (hi : i < p.length)
    (hiLeft : p.getVert i = D.extraLeft)
    (hiRight : p.getVert (i + 1) = D.extraRight) :
    (∀ j : ℕ, j < i →
      D.tree.Adj (p.getVert j) (p.getVert (j + 1))) ∧
    (∀ j : ℕ, i + 1 ≤ j → j < p.length →
      D.tree.Adj (p.getVert j) (p.getVert (j + 1))) := by
  constructor
  · intro j hj
    exact tree_adj_getVert_succ_of_ne_added_index D p hp hi
      (by omega) (by omega) hiLeft hiRight
  · intro j hjLower hjUpper
    exact tree_adj_getVert_succ_of_ne_added_index D p hp hi
      hjUpper (by omega) hiLeft hiRight

/-- In particular the orientation-reversed consecutive placement has the same
tree-arm conclusion. -/
theorem consecutive_geodesic_tree_arms_reverse
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {a b : V} (p : G.Walk a b) (hp : p.IsPath)
    {i : ℕ} (hi : i < p.length)
    (hiRight : p.getVert i = D.extraRight)
    (hiLeft : p.getVert (i + 1) = D.extraLeft) :
    (∀ j : ℕ, j < i →
      D.tree.Adj (p.getVert j) (p.getVert (j + 1))) ∧
    (∀ j : ℕ, i + 1 ≤ j → j < p.length →
      D.tree.Adj (p.getVert j) (p.getVert (j + 1))) := by
  have hrev := consecutive_geodesic_tree_arms
    { tree := D.tree
      tree_connected := D.tree_connected
      tree_acyclic := D.tree_acyclic
      extraLeft := D.extraRight
      extraRight := D.extraLeft
      endpoints_ne := D.endpoints_ne.symm
      extra_not_tree := by simpa [adj_comm] using D.extra_not_tree
      adj_iff := by
        intro x y
        rw [D.adj_iff]
        aesop }
    p hp hi hiRight hiLeft
  exact hrev

/-- Exact charge boundary for the consecutive-edge geometry (indeed for every
tree-plus-one-edge graph): endpoint deletion proves WOWII 13 unless local
neighborhood independence reaches the full maximum degree. -/
theorem wowii13_or_localMax_eq_maxDegree_of_treePlusOneEdge
    [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} [Nonempty V] [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (hconn : G.Connected) :
    ((G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G) ∨
      localMax G = G.maxDegree := by
  have hle := localMax_le_maxDegree G
  by_cases hEq : localMax G = G.maxDegree
  · exact Or.inr hEq
  · left
    apply wowii13_of_odd_unicyclic_certificate G D.extraLeft hconn
      D.induce_erase_endpoint_bipartite
    exact Or.inl (Nat.lt_of_le_of_ne hle hEq)

end WrittenOnTheWallII.GraphConjecture19ConsecutiveEdgeStructure
