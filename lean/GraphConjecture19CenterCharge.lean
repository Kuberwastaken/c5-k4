import GraphConjecture19CenterOnlyResidue
import GraphConjecture19UnicyclicCharge

/-!
# WOWII 19/13: charging the center-endpoint residue
-/

namespace WrittenOnTheWallII.GraphConjecture19CenterCharge

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19EndpointMax
open WrittenOnTheWallII.GraphConjecture19TreeCharge
open WrittenOnTheWallII.GraphConjecture19MultiArm
open WrittenOnTheWallII.GraphConjecture19UnicyclicCharge

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Symmetric endpoint deletion: deleting the right endpoint of the added
edge leaves an induced graph contained in the spanning tree. -/
theorem induce_erase_right_endpoint_le_tree
    {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    G.induce (↑(Finset.univ.erase D.extraRight) : Set V) ≤
      D.tree.induce (↑(Finset.univ.erase D.extraRight) : Set V) := by
  intro a b hab
  rcases D.adj_iff.mp hab with htree | hextra
  · exact htree
  · rcases hextra with h12 | h21
    · have hb : (b : V) = D.extraRight := h12.2
      have hbMem : (b : V) ∈ Finset.univ.erase D.extraRight := b.property
      simp [hb] at hbMem
    · have ha : (a : V) = D.extraRight := h21.1
      have haMem : (a : V) ∈ Finset.univ.erase D.extraRight := a.property
      simp [ha] at haMem

/-- Deleting the right endpoint leaves an acyclic graph. -/
theorem induce_erase_right_endpoint_acyclic
    {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    (G.induce (↑(Finset.univ.erase D.extraRight) : Set V)).IsAcyclic := by
  apply IsAcyclic.anti (induce_erase_right_endpoint_le_tree D)
  exact D.tree_acyclic.induce _

/-- Hence either endpoint of the added edge may serve as the one-vertex odd
cycle transversal. -/
theorem induce_erase_right_endpoint_bipartite
    {G : SimpleGraph V} (D : TreePlusOneEdge G) :
    (G.induce (↑(Finset.univ.erase D.extraRight) : Set V)).IsBipartite :=
  (induce_erase_right_endpoint_acyclic D).isBipartite

/-- If a specified center is either endpoint of the added edge, deleting the
center leaves an induced bipartite graph. -/
theorem induce_erase_center_bipartite_of_endpoint
    {G : SimpleGraph V} (D : TreePlusOneEdge G) (c : V)
  (hc : D.extraLeft = c ∨ D.extraRight = c) :
    (G.induce (↑(Finset.univ.erase c) : Set V)).IsBipartite := by
  rcases hc with hLeft | hRight
  · subst c
    exact D.induce_erase_endpoint_bipartite
  · subst c
    exact induce_erase_right_endpoint_bipartite D

/-- The center-endpoint residue always supplies the exact order-`n-1`
induced-bipartite witness. -/
theorem card_sub_one_le_b_of_center_endpoint
    {G : SimpleGraph V} (D : TreePlusOneEdge G) (c : V)
    (hc : D.extraLeft = c ∨ D.extraRight = c) :
    (((Fintype.card V - 1 : ℕ) : ℝ)) ≤ b G := by
  exact card_sub_one_le_b_of_delete_vertex G c
    (induce_erase_center_bipartite_of_endpoint D c hc)

/-- Exact charge boundary for the center residue.  It proves WOWII 13 unless
the maximum local neighborhood independence is exactly the maximum degree. -/
theorem wowii13_or_localMax_eq_maxDegree_of_center_endpoint
    {G : SimpleGraph V} [Nonempty V] [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (c : V) (hconn : G.Connected)
    (hc : D.extraLeft = c ∨ D.extraRight = c) :
    ((G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G) ∨
      localMax G = G.maxDegree := by
  have hle := localMax_le_maxDegree G
  by_cases hEq : localMax G = G.maxDegree
  · exact Or.inr hEq
  · left
    apply wowii13_of_odd_unicyclic_certificate G c hconn
      (induce_erase_center_bipartite_of_endpoint D c hc)
    exact Or.inl (Nat.lt_of_le_of_ne hle hEq)

omit [DecidableEq V] in
/-- Equality in the remaining local charge is attained at a maximum-degree
vertex whose neighborhood independence number is the full maximum degree. -/
theorem exists_maxDegree_vertex_with_full_local_independence
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hEq : localMax G = G.maxDegree) :
    ∃ v : V,
      G.degree v = G.maxDegree ∧
      indepNeighborsCard G v = G.degree v := by
  obtain ⟨v, hv⟩ := exists_indepNeighborsCard_eq_localMax G
  have hlocalDegree := indepNeighborsCard_le_degree G v
  have hdegreeMax := G.degree_le_maxDegree v
  refine ⟨v, ?_, ?_⟩
  · omega
  · omega

/-- Structural form of the exact center-case obstruction. -/
theorem wowii13_or_exists_full_independent_maxNeighborhood_of_center_endpoint
    {G : SimpleGraph V} [Nonempty V] [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (c : V) (hconn : G.Connected)
    (hc : D.extraLeft = c ∨ D.extraRight = c) :
    ((G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G) ∨
      ∃ v : V,
        G.degree v = G.maxDegree ∧
        indepNeighborsCard G v = G.degree v := by
  rcases wowii13_or_localMax_eq_maxDegree_of_center_endpoint
      D c hconn hc with hwow | hEq
  · exact Or.inl hwow
  · exact Or.inr (exists_maxDegree_vertex_with_full_local_independence G hEq)

end WrittenOnTheWallII.GraphConjecture19CenterCharge
