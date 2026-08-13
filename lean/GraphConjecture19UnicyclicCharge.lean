import GraphConjecture19MetricIntersection
import GraphConjecture19OddCycleTransversal

/-!
# WOWII 19/13: unicyclic and one-transversal charge classes
-/

namespace WrittenOnTheWallII.GraphConjecture19UnicyclicCharge

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19EndpointMax
open WrittenOnTheWallII.GraphConjecture19TreeCharge
open WrittenOnTheWallII.GraphConjecture19MetricIntersection
open WrittenOnTheWallII.GraphConjecture19OddCycleTransversal
open WrittenOnTheWallII.GraphConjecture19TransversalChargeClasses

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- If the maximum local independence is strictly below maximum degree, the
universal diameter--degree count gains the unit needed by a one-vertex odd
cycle transversal. -/
theorem diameter_add_localMax_le_card_of_lt_maxDegree
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hlocal : localMax G < G.maxDegree) :
    G.diam + localMax G ≤ Fintype.card V := by
  have hdeg := diameter_add_maxDegree_le_card_add_one G hconn
  omega

/-- General one-transversal class, first route: strict local-independence
discount from maximum degree. -/
theorem transversal_charge_of_delete_vertex_of_localMax_lt_maxDegree
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj] (z : V)
    (hconn : G.Connected)
    (hz : (G.induce (↑(Finset.univ.erase z) : Set V)).IsBipartite)
    (hlocal : localMax G < G.maxDegree) :
    oddCycleTransversalNumber G + G.diam + localMax G ≤
      Fintype.card V + 1 := by
  have htau := oddCycleTransversalNumber_le_one_of_delete_vertex G z hz
  have hcount := diameter_add_localMax_le_card_of_lt_maxDegree G hconn hlocal
  omega

/-- General one-transversal class, second route: a directly sharpened
diameter--maximum-degree count. -/
theorem transversal_charge_of_delete_vertex_of_degree_count
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj] (z : V)
    (hz : (G.induce (↑(Finset.univ.erase z) : Set V)).IsBipartite)
    (hdegree : G.diam + G.maxDegree ≤ Fintype.card V) :
    oddCycleTransversalNumber G + G.diam + localMax G ≤
      Fintype.card V + 1 := by
  have htau := oddCycleTransversalNumber_le_one_of_delete_vertex G z hz
  have hlocal := localMax_le_maxDegree G
  omega

/-- The exact two-route certificate satisfied by all odd-unicyclic controls:
delete one cycle vertex, then either local independence loses a degree unit or
the diameter--degree count itself has one unit of slack. -/
theorem wowii13_of_odd_unicyclic_certificate
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj] (z : V)
    (hconn : G.Connected)
    (hz : (G.induce (↑(Finset.univ.erase z) : Set V)).IsBipartite)
    (hroute : localMax G < G.maxDegree ∨
      G.diam + G.maxDegree ≤ Fintype.card V) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  apply wowii13_of_minimum_transversal_charge G
  rcases hroute with hlocal | hdegree
  · exact transversal_charge_of_delete_vertex_of_localMax_lt_maxDegree
      G z hconn hz hlocal
  · exact transversal_charge_of_delete_vertex_of_degree_count
      G z hz hdegree

/-- Even-unicyclic and, more generally, connected bipartite graphs satisfy the
charge unconditionally by the classical diameter--degree theorem. -/
theorem wowii13_of_connected_bipartite
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hbip : G.IsBipartite) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  have hdegree := diameter_add_maxDegree_le_card_add_one G hconn
  have hcount := diameter_add_localMax_le_card_add_one_of_degree_count G hdegree
  exact wowii13_of_minimum_transversal_charge G
    (transversal_charge_of_bipartite_of_order_count G hbip hcount)

end WrittenOnTheWallII.GraphConjecture19UnicyclicCharge
