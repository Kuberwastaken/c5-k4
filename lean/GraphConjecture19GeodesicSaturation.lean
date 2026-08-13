import GraphConjecture19ExtremalSaturation
import GraphConjecture19MetricIntersection

/-!
# WOWII 19/13: actual geodesic saturation classification
-/

namespace WrittenOnTheWallII.GraphConjecture19GeodesicSaturation

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19MetricIntersection
open WrittenOnTheWallII.GraphConjecture19ExtremalSaturation

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- At equality in the diameter--maximum-degree order bound, an actual
diametral geodesic and an actual maximum-degree open neighborhood realize one
of the two saturated configurations.  The endpoints of the added edge are
classified in the same conclusion. -/
theorem extremal_diametral_geodesic_classification
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) (hconn : G.Connected)
    (heq : G.diam + G.maxDegree = Fintype.card V + 1) :
    ∃ (c u v : V) (p : G.Walk u v),
      G.maxDegree = G.degree c ∧
      G.dist u v = G.diam ∧
      p.IsPath ∧
      p.length = G.dist u v ∧
      (let P := p.support.toFinset
       let N := G.neighborFinset c
       (c ∈ P ∧
          (P ∩ N).card = 2 ∧
          P ∪ N = Finset.univ ∧
          (D.extraLeft ∈ P ∨ D.extraLeft ∈ N) ∧
          (D.extraRight ∈ P ∨ D.extraRight ∈ N)) ∨
       (c ∉ P ∧
          (P ∩ N).card = 3 ∧
          insert c (P ∪ N) = Finset.univ ∧
          (D.extraLeft = c ∨ D.extraLeft ∈ P ∨ D.extraLeft ∈ N) ∧
          (D.extraRight = c ∨ D.extraRight ∈ P ∨ D.extraRight ∈ N))) := by
  obtain ⟨c, hcdeg⟩ := G.exists_maximal_degree_vertex
  obtain ⟨u, v, huv⟩ := G.exists_dist_eq_diam
  obtain ⟨p, hpPath, hpDist⟩ := hconn.exists_path_of_dist u v
  refine ⟨c, u, v, p, hcdeg, huv, hpPath, hpDist, ?_⟩
  let P : Finset V := p.support.toFinset
  let N : Finset V := G.neighborFinset c
  have hP : P.card = G.diam + 1 := by
    dsimp [P]
    rw [List.toFinset_card_of_nodup hpPath.support_nodup,
      p.length_support, hpDist, huv]
  have hN : N.card = G.maxDegree := by
    dsimp [N]
    exact hcdeg.symm
  have hcN : c ∉ N := by
    dsimp [N]
    exact G.notMem_neighborFinset_self c
  have hmetric := diametralNeighborhoodIntersectionBound G
    (c := c) p hpPath hpDist (hpDist.trans huv)
  change (c ∈ P → (P ∩ N).card ≤ 2) ∧
    (c ∉ P → (P ∩ N).card ≤ 3) at hmetric
  by_cases hcP : c ∈ P
  · have hsat := on_path_extremal_saturation P N G.diam G.maxDegree
      hP hN (hmetric.1 hcP) heq
    have hend := fundamental_endpoints_classified_of_on_path_saturation
      D P N hsat.2
    exact Or.inl ⟨hcP, hsat.1, hsat.2, hend.1, hend.2⟩
  · have hsat := off_path_extremal_saturation P N c G.diam G.maxDegree
      hP hN hcP hcN (hmetric.2 hcP) heq
    have hend := fundamental_endpoints_classified_of_off_path_saturation
      D P N c hsat.2
    exact Or.inr ⟨hcP, hsat.1, hsat.2, hend.1, hend.2⟩

end WrittenOnTheWallII.GraphConjecture19GeodesicSaturation
