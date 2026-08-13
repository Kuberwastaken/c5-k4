import GraphConjecture141CyclePeak

/-!
# WOWII 141: unconditional closure through girth eleven

The radius-three exclusion supplies a chordless four-edge prefix at a maximum
local-independence center.  Its first three edges give the existing two-tail
certificate; the fourth endpoint is a unique third leaf.
-/

namespace WrittenOnTheWallII.GraphConjecture141GirthElevenClosure

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141DistanceFour
open WrittenOnTheWallII.GraphConjecture141CyclePeak
open WrittenOnTheWallII.GraphConjecture141GirthEleven
open WrittenOnTheWallII.GraphConjecture141GirthNineClosure
open WrittenOnTheWallII.GraphConjecture141GirthSevenExistence

universe u
variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

omit [Fintype V] [Nonempty V] in
/-- The cardinality field of a four-edge prefix records that its five listed
vertices have no repetition. -/
lemma fourEdgePrefix_vertices_nodup (G : SimpleGraph V) (P : FourEdgePrefix G) :
    [P.v, P.u, P.x, P.y, P.z].Nodup := by
  exact (Multiset.toFinset_card_eq_card_iff_nodup (m :=
    (↑([P.v, P.u, P.x, P.y, P.z] : List V) : Multiset V))).mp (by
      simpa using P.pairwise)

omit [Fintype V] [Nonempty V] in
lemma fourEdgePrefix_vertices_pairwise (G : SimpleGraph V) (P : FourEdgePrefix G) :
    P.v ≠ P.u ∧ P.v ≠ P.x ∧ P.v ≠ P.y ∧ P.v ≠ P.z ∧
    P.u ≠ P.x ∧ P.u ≠ P.y ∧ P.u ≠ P.z ∧
    P.x ≠ P.y ∧ P.x ≠ P.z ∧ P.y ≠ P.z := by
  have hp := fourEdgePrefix_vertices_nodup G P
  simp at hp
  rcases hp with ⟨⟨hvu, hvx, hvy, hvz⟩, ⟨hux, huy, huz⟩,
    ⟨hxy, hxz⟩, hyz⟩
  exact ⟨hvu, hvx, hvy, hvz, hux, huy, huz, hxy, hxz, hyz⟩

omit [Nonempty V] in
/-- At girth at least ten, the fourth endpoint of a chordless four-edge prefix
has no edge back into the open neighborhood of its initial vertex. -/
lemma fourth_vertex_not_adj_neighborSet
    (G : SimpleGraph V) [DecidableRel G.Adj] (hgirth : 10 ≤ G.girth)
    (P : FourEdgePrefix G) :
    ∀ a ∈ G.neighborFinset P.v, ¬G.Adj P.z a := by
  intro a ha hza
  have hva : G.Adj P.v a := by simpa [G.mem_neighborFinset] using ha
  obtain ⟨hvu', hvx', hvy', hvz', hux', huy', huz', hxy', hxz', hyz'⟩ :=
    fourEdgePrefix_vertices_pairwise G P
  have hav : a ≠ P.v := hva.ne.symm
  have hau : a ≠ P.u := by
    intro h
    subst a
    exact P.uz_nonadj hza.symm
  have hax : a ≠ P.x := by
    intro h
    subst a
    exact P.xz_nonadj hza.symm
  have hay : a ≠ P.y := by
    intro h
    subst a
    exact P.vy_nonadj hva
  have haz : a ≠ P.z := hza.ne.symm
  have hua : P.u ≠ a := hau.symm
  have hxa : P.x ≠ a := hax.symm
  have hya : P.y ≠ a := hay.symm
  have hza_ne : P.z ≠ a := haz.symm
  have huv : P.u ≠ P.v := hvu'.symm
  have hxv : P.x ≠ P.v := hvx'.symm
  have hyv : P.y ≠ P.v := hvy'.symm
  have hzv : P.z ≠ P.v := hvz'.symm
  have hxu : P.x ≠ P.u := hux'.symm
  have hyu : P.y ≠ P.u := huy'.symm
  have hzu : P.z ≠ P.u := huz'.symm
  have hyx : P.y ≠ P.x := hxy'.symm
  have hzx : P.z ≠ P.x := hxz'.symm
  have hzy : P.z ≠ P.y := hyz'.symm
  let c : G.Walk P.v P.v :=
    .cons P.vu (.cons P.ux (.cons P.xy (.cons P.yz
      (.cons hza (.cons hva.symm .nil)))))
  have hc : c.IsCycle := by
    simp_all [c, Walk.isCycle_def, Walk.isTrail_def]
  have hshort := G.girth_le_length hc
  simp only [c, Walk.length_cons, Walk.length_nil] at hshort
  omega

/-- A four-edge prefix based at a maximum local-independence center constructs
the complete third-leaf certificate. -/
noncomputable def thirdLeafDataOfFourEdgePrefix
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirth : 10 ≤ G.girth) (P : FourEdgePrefix G)
    (hvmax : indepNeighborsCard G P.v =
      Finset.univ.sup (indepNeighborsCard G)) :
    ThirdLeafData G := by
  obtain ⟨-, hvx, hvy, hvz, -, huy, -, hxy, hxz, hyz⟩ :=
    fourEdgePrefix_vertices_pairwise G P
  let D := secondLeafDataOfPrefix G (by omega) P.v P.u P.x P.y hvmax
    P.vu P.ux P.xy P.vu.ne hvx hvy P.ux.ne huy P.xy.ne
    P.vx_nonadj P.vy_nonadj P.uy_nonadj
  refine {
    base := D.toTwoVertexTailSplice G
    third := P.z
    third_not_mem := ?_
    third_unique_base := ?_
  }
  · change P.z ∉ insert P.y
      (insert P.x (insert P.v (G.neighborFinset P.v)))
    simp only [Finset.mem_insert, not_or]
    refine ⟨?_, ?_, ?_, ?_⟩
    · exact hyz.symm
    · exact hxz.symm
    · exact hvz.symm
    · intro hzN
      exact P.vz_nonadj (by simpa [G.mem_neighborFinset] using hzN)
  · intro q hq
    change q ∈ insert P.y
      (insert P.x (insert P.v (G.neighborFinset P.v))) at hq
    change G.Adj P.z q ↔ q = P.y
    simp only [Finset.mem_insert] at hq
    rcases hq with rfl | rfl | rfl | hqN
    · exact ⟨fun _ => rfl, fun _ => P.yz.symm⟩
    · exact ⟨fun h => (P.xz_nonadj h.symm).elim, fun h => (hxy h).elim⟩
    · exact ⟨fun h => (P.vz_nonadj h.symm).elim, fun h => (hvy h).elim⟩
    · constructor
      · intro hzq
        exact (fourth_vertex_not_adj_neighborSet G hgirth P q hqN hzq).elim
      · intro hqy
        subst q
        exact P.yz.symm

/-- **Unconditional girth-ten/eleven closure.** -/
theorem conjecture141_of_girth_ten_or_eleven
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected)
    (hgirthLower : 10 ≤ G.girth) (hgirthUpper : G.girth ≤ 11) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  obtain ⟨v, hvmax⟩ := exists_maximum_local_center G
  have hfour := everyVertexHasDistanceAtLeastFour_of_connected_of_ten_le_girth
    G hconn hgirthLower
  obtain ⟨P, hpv⟩ := exists_fourEdgePrefix_at_maximum_center G hconn hfour v
  have hPmax : indepNeighborsCard G P.v =
      Finset.univ.sup (indepNeighborsCard G) := by
    simpa [hpv] using hvmax
  let D := thirdLeafDataOfFourEdgePrefix G hgirthLower P hPmax
  exact conjecture141_of_girth_ten_or_eleven_of_thirdLeafData
    G hgirthLower hgirthUpper D

/-- **WOWII 141 is closed unconditionally through girth eleven.** -/
theorem conjecture141_of_girth_le_eleven
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hgirth : G.girth ≤ 11) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  by_cases hnine : G.girth ≤ 9
  · exact conjecture141_of_girth_le_nine G hconn hnine
  · exact conjecture141_of_girth_ten_or_eleven G hconn (by omega) hgirth

end WrittenOnTheWallII.GraphConjecture141GirthElevenClosure
