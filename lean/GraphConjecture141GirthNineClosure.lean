import GraphConjecture141RadiusTwoInstantiation

/-!
# WOWII 141: closing girth eight and nine
-/

namespace WrittenOnTheWallII.GraphConjecture141GirthNineClosure

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141GirthSeven
open WrittenOnTheWallII.GraphConjecture141GirthSevenExistence
open WrittenOnTheWallII.GraphConjecture141EccentricityThree
open WrittenOnTheWallII.GraphConjecture141DistanceTwoExistence
open WrittenOnTheWallII.GraphConjecture141RadiusGirth
open WrittenOnTheWallII.GraphConjecture141RadiusTwoInstantiation

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

omit [DecidableEq V] [Nonempty V] in
/-- In a chordless three-edge prefix `v-u-x-y`, girth at least eight forces
`y` to have no neighbor in `N(v)`: such an edge makes a triangle or 5-cycle. -/
lemma third_vertex_not_adj_neighborSet
    (G : SimpleGraph V) [DecidableRel G.Adj] (hgirth : 8 ≤ G.girth)
    {v u x y : V}
    (hvu : G.Adj v u) (hux : G.Adj u x) (hxy : G.Adj x y)
    (hvu_ne : v ≠ u) (hvx_ne : v ≠ x) (hvy_ne : v ≠ y)
    (hux_ne : u ≠ x) (huy_ne : u ≠ y) (hxy_ne : x ≠ y)
    (hvx : ¬G.Adj v x) (_hvy : ¬G.Adj v y) (huy : ¬G.Adj u y) :
    ∀ a ∈ G.neighborFinset v, ¬G.Adj y a := by
  intro a ha hya
  have hva : G.Adj v a := by simpa [G.mem_neighborFinset] using ha
  have hav : a ≠ v := hva.ne.symm
  have hay : a ≠ y := hya.ne.symm
  have hau : a ≠ u := by
    intro h
    subst a
    exact huy hya.symm
  have hax : a ≠ x := by
    intro h
    subst a
    exact hvx hva
  let c : G.Walk v v :=
    .cons hvu (.cons hux (.cons hxy (.cons hya (.cons hva.symm .nil))))
  have hc : c.IsCycle := by
    have huv : u ≠ v := hvu_ne.symm
    have hxv : x ≠ v := hvx_ne.symm
    have hyv : y ≠ v := hvy_ne.symm
    have hxu : x ≠ u := hux_ne.symm
    have hyu : y ≠ u := huy_ne.symm
    have hyx : y ≠ x := hxy_ne.symm
    have hua : u ≠ a := hau.symm
    have hxa : x ≠ a := hax.symm
    have hya' : y ≠ a := hay.symm
    simp [c, Walk.isCycle_def, Walk.isTrail_def, hvu_ne, huv, hvx_ne,
      hxv, hvy_ne, hyv, hux_ne, huy_ne, hxy_ne,
      hav, hua, hxa, hya']
  have := G.girth_le_length hc
  simp only [c, Walk.length_cons, Walk.length_nil] at this
  omega

/-- A chordless three-edge prefix at a maximum center constructs the complete
second-leaf certificate. -/
def secondLeafDataOfPrefix
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirth : 8 ≤ G.girth)
    (v u x y : V)
    (hvmax : indepNeighborsCard G v = Finset.univ.sup (indepNeighborsCard G))
    (hvu : G.Adj v u) (hux : G.Adj u x) (hxy : G.Adj x y)
    (hvu_ne : v ≠ u) (hvx_ne : v ≠ x) (hvy_ne : v ≠ y)
    (hux_ne : u ≠ x) (huy_ne : u ≠ y) (hxy_ne : x ≠ y)
    (hvx : ¬G.Adj v x) (hvy : ¬G.Adj v y) (huy : ¬G.Adj u y) :
    SecondLeafData G := by
  let A := G.neighborFinset v
  let D : DistanceTwoLeafData G := {
    center := v
    localSet := A
    extra := x
    attachment := u
    localIndependent := by
      simpa [A, ← coe_neighborFinset] using
        locallyIndependent_of_six_le_girth G (by omega) v
    localSubset := Finset.Subset.rfl
    localCard := by
      change (G.neighborFinset v).card = indepNeighborsCard G v
      rw [G.card_neighborFinset_eq_degree]
      exact (indepNeighborsCard_eq_degree_of_independent_neighborhood
        G v (locallyIndependent_of_six_le_girth G (by omega) v)).symm
    centerMaximal := hvmax
    attachment_mem := by simpa [A, G.mem_neighborFinset] using hvu
    extra_not_mem := by
      simp only [Finset.mem_insert, not_or]
      refine ⟨hvx_ne.symm, ?_⟩
      intro hxA
      exact hvx (by simpa [A, G.mem_neighborFinset] using hxA)
    center_extra_nonadj := hvx
    extra_unique_local := by
      intro a ha
      constructor
      · intro hxa
        apply unique_neighbor_attachment_of_six_le_girth
          G (by omega) hvu hux hvx_ne.symm a
        · simpa [A, G.mem_neighborFinset] using ha
        · exact hxa
      · intro hau'
        subst a
        exact hux.symm
  }
  exact {
    base := D
    second := y
    second_not_mem := by
      simp only [Finset.mem_insert, not_or]
      refine ⟨hxy_ne.symm, hvy_ne.symm, ?_⟩
      intro hyA
      exact hvy (by
        change y ∈ G.neighborFinset v at hyA
        simpa [G.mem_neighborFinset] using hyA)
    second_unique_base := by
      intro z hz
      have hzCases : z = x ∨ z = v ∨ z ∈ A := by simpa [D] using hz
      constructor
      · intro hyz
        rcases hzCases with rfl | rfl | hzA
        · rfl
        · exact (hvy hyz.symm).elim
        · exact (third_vertex_not_adj_neighborSet G hgirth hvu hux hxy
            hvu_ne hvx_ne hvy_ne hux_ne huy_ne hxy_ne hvx hvy huy
            z (by simpa [A] using hzA) hyz).elim
      · intro hzx
        subst z
        exact hxy.symm
  }

/-- **Unconditional girth-eight/nine closure.** -/
theorem conjecture141_of_girth_eight_or_nine
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected)
    (hgirthLower : 8 ≤ G.girth) (hgirthUpper : G.girth ≤ 9) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  obtain ⟨v, hvmax⟩ := exists_maximum_local_center G
  have hevery := everyVertexHasDistanceAtLeastThree_of_connected_of_eight_le_girth
    G hconn hgirthLower
  obtain ⟨w, hvw⟩ := hevery v
  obtain ⟨u, x, y, hvu, hux, hxy, hvu_ne, hvx_ne, hvy_ne,
    hux_ne, huy_ne, hxy_ne, hvx, hvy, huy⟩ :=
      exists_threeEdgePrefix_of_connected_of_three_le_dist G hconn v w hvw
  let D := secondLeafDataOfPrefix G hgirthLower v u x y hvmax hvu hux hxy
    hvu_ne hvx_ne hvy_ne hux_ne huy_ne hxy_ne hvx hvy huy
  exact conjecture141_of_girth_eight_or_nine_of_secondLeafData
    G hgirthLower hgirthUpper D

/-- **WOWII 141 is closed unconditionally through girth nine.** -/
theorem conjecture141_of_girth_le_nine
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hgirth : G.girth ≤ 9) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  by_cases hseven : G.girth ≤ 7
  · exact conjecture141_of_girth_le_seven G hconn hseven
  · apply conjecture141_of_girth_eight_or_nine G hconn
    · omega
    · exact hgirth

end WrittenOnTheWallII.GraphConjecture141GirthNineClosure
