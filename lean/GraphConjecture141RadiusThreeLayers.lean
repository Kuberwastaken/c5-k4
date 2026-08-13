import GraphConjecture141EqualLayerClosure

/-!
# WOWII 141: independence of the first four BFS layers

The equal-layer cycle constructor now turns an edge inside any layer of index
at most three into a simple cycle of length at most seven.  Girth at least
eight therefore makes every such layer independent.  This closes the
same-layer half of the radius-three forest certificate.
-/

namespace WrittenOnTheWallII.GraphConjecture141RadiusThreeLayers

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture141RadiusThreeAcyclic
open WrittenOnTheWallII.GraphConjecture141EqualLayerClosure

universe u
variable {V : Type u} [DecidableEq V]

/-- Every BFS layer through radius three is independent when the graph has
girth at least eight. -/
theorem bfsLayer_independent_of_eight_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 8 ≤ G.girth)
    (r : V) (k : ℕ) (hk : k ≤ 3) :
    G.IsIndepSet (bfsLayer G r k) := by
  intro x hx y hy hxy hadj
  obtain ⟨p, _hpPath, hpDist⟩ := hconn.exists_path_of_dist r x
  obtain ⟨q, _hqPath, hqDist⟩ := hconn.exists_path_of_dist r y
  have hpLen : p.length = k := hpDist.trans hx
  have hqLen : q.length = k := hqDist.trans hy
  have hlen : p.length = q.length := hpLen.trans hqLen.symm
  have hpThree : p.length ≤ 3 := by omega
  obtain ⟨c, hc, hcLen⟩ := cycle_length_le_seven_of_equal_layer_three
    p q hpDist hqDist hlen hpThree hxy hadj.symm
  have hgirthLe := G.girth_le_length hc
  omega

/-- Radius-three specialization in the exact four-layer form used by
`RadiusThreeForestCertificate`: ranks `0,1,2,3` have no horizontal edge. -/
theorem radiusThree_layers_independent
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 8 ≤ G.girth)
    (r : V) :
    G.IsIndepSet (bfsLayer G r 0) ∧
      G.IsIndepSet (bfsLayer G r 1) ∧
      G.IsIndepSet (bfsLayer G r 2) ∧
      G.IsIndepSet (bfsLayer G r 3) := by
  exact ⟨bfsLayer_independent_of_eight_le_girth G hconn hgirth r 0 (by omega),
    bfsLayer_independent_of_eight_le_girth G hconn hgirth r 1 (by omega),
    bfsLayer_independent_of_eight_le_girth G hconn hgirth r 2 (by omega),
    bfsLayer_independent_of_eight_le_girth G hconn hgirth r 3 (by omega)⟩

end WrittenOnTheWallII.GraphConjecture141RadiusThreeLayers
