import GraphConjecture19TransversalChargeClasses

/-!
# WOWII 19/13: tree-charge reduction
-/

namespace WrittenOnTheWallII.GraphConjecture19TreeCharge

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19EndpointMax
open WrittenOnTheWallII.GraphConjecture19OddCycleTransversal
open WrittenOnTheWallII.GraphConjecture19TransversalChargeClasses

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [DecidableEq V] in
/-- Local neighborhood independence never exceeds degree. -/
theorem indepNeighborsCard_le_degree (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    indepNeighborsCard G v ≤ G.degree v := by
  classical
  let H := G.induce (G.neighborSet v)
  obtain ⟨S, hS⟩ := H.exists_isNIndepSet_indepNum
  calc
    indepNeighborsCard G v = S.card := hS.card_eq.symm
    _ ≤ Fintype.card (G.neighborSet v) := S.card_le_univ
    _ = G.degree v := G.card_neighborSet_eq_degree v

omit [DecidableEq V] in
/-- Consequently the maximum local independence is at most maximum degree. -/
theorem localMax_le_maxDegree
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj] :
    localMax G ≤ G.maxDegree := by
  obtain ⟨v, hv⟩ := exists_indepNeighborsCard_eq_localMax G
  rw [← hv]
  exact (indepNeighborsCard_le_degree G v).trans (G.degree_le_maxDegree v)

omit [DecidableEq V] in
/-- The classical order--diameter--maximum-degree count immediately implies
the local-independence order count needed by the transversal method. -/
theorem diameter_add_localMax_le_card_add_one_of_degree_count
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hdegree : G.diam + G.maxDegree ≤ Fintype.card V + 1) :
    G.diam + localMax G ≤ Fintype.card V + 1 := by
  have hlocal := localMax_le_maxDegree G
  omega

/-- Finite connected acyclic graphs satisfy WOWII 13 once supplied with the
standard diameter--maximum-degree order count.  All graph-invariant and
transversal bridges are discharged here. -/
theorem wowii13_of_tree_of_degree_count
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hacyc : G.IsAcyclic)
    (hdegree : G.diam + G.maxDegree ≤ Fintype.card V + 1) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  have hbip : G.IsBipartite := hacyc.isBipartite
  have hcount := diameter_add_localMax_le_card_add_one_of_degree_count G hdegree
  exact wowii13_of_minimum_transversal_charge G
    (transversal_charge_of_bipartite_of_order_count G hbip hcount)

end WrittenOnTheWallII.GraphConjecture19TreeCharge
