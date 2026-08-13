import GraphConjecture19TreeCharge

/-!
# WOWII 19/13: diameter--maximum-degree counting
-/

namespace WrittenOnTheWallII.GraphConjecture19DiameterDegree

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Pure finite-set count for the case where the maximum-degree vertex lies
on the diametral path. -/
lemma diameter_degree_count_of_mem
    (P N : Finset V) (d Delta : ℕ)
    (hP : P.card = d + 1) (hN : N.card = Delta)
    (hinter : (P ∩ N).card ≤ 2) :
    d + Delta ≤ Fintype.card V + 1 := by
  have hunion : (P ∪ N).card ≤ Fintype.card V := (P ∪ N).card_le_univ
  rw [Finset.card_union, hP, hN] at hunion
  omega

/-- Pure finite-set count for the case where the maximum-degree vertex lies
off the diametral path.  Adding `c` recovers the unit lost to the possible
third path neighbor. -/
lemma diameter_degree_count_of_not_mem
    (P N : Finset V) (c : V) (d Delta : ℕ)
    (hP : P.card = d + 1) (hN : N.card = Delta)
    (hcP : c ∉ P) (hcN : c ∉ N)
    (hinter : (P ∩ N).card ≤ 3) :
    d + Delta ≤ Fintype.card V + 1 := by
  have hcUnion : c ∉ P ∪ N := by simp [hcP, hcN]
  have hunion : (insert c (P ∪ N)).card ≤ Fintype.card V :=
    (insert c (P ∪ N)).card_le_univ
  rw [card_insert_of_notMem hcUnion, Finset.card_union, hP, hN] at hunion
  omega

/-- The exact metric hinge in the classical proof. -/
def DiametralNeighborhoodIntersectionBound (G : SimpleGraph V)
    [DecidableRel G.Adj] : Prop :=
  ∀ {u v c : V} (p : G.Walk u v),
    p.IsPath → p.length = G.dist u v → p.length = G.diam →
    let P := p.support.toFinset
    let N := G.neighborFinset c
    (c ∈ P → (P ∩ N).card ≤ 2) ∧
    (c ∉ P → (P ∩ N).card ≤ 3)

/-- Once the two/three-neighbor metric hinge is available, maximal-degree and
diametral-path selection yield the classical order bound. -/
theorem diameter_add_maxDegree_le_card_add_one_of_intersection_bound
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hmetric : DiametralNeighborhoodIntersectionBound G) :
    G.diam + G.maxDegree ≤ Fintype.card V + 1 := by
  obtain ⟨c, hcdeg⟩ := G.exists_maximal_degree_vertex
  obtain ⟨u, v, huv⟩ := G.exists_dist_eq_diam
  obtain ⟨p, hpPath, hpDist⟩ := hconn.exists_path_of_dist u v
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
    simp
  have hm := hmetric (c := c) p hpPath hpDist (hpDist.trans huv)
  dsimp only at hm
  by_cases hcP : c ∈ P
  · exact diameter_degree_count_of_mem P N G.diam G.maxDegree
      hP hN (hm.1 hcP)
  · exact diameter_degree_count_of_not_mem P N c G.diam G.maxDegree
      hP hN hcP hcN (hm.2 hcP)

/-- The complete #13 tree conclusion conditional only on the single classical
path-neighborhood intersection hinge. -/
theorem wowii13_of_tree_of_intersection_bound
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hacyc : G.IsAcyclic)
    (hmetric : DiametralNeighborhoodIntersectionBound G) :
    (G.diam : ℝ) +
        (_root_.WrittenOnTheWallII.GraphConjecture19EndpointMax.localMax G : ℝ) - 1 ≤
      b G := by
  exact _root_.WrittenOnTheWallII.GraphConjecture19TreeCharge.wowii13_of_tree_of_degree_count
    G hacyc
      (diameter_add_maxDegree_le_card_add_one_of_intersection_bound
        G hconn hmetric)

end WrittenOnTheWallII.GraphConjecture19DiameterDegree
