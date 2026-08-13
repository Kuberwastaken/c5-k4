import GraphConjecture141RadiusTwoAcyclic

/-!
# WOWII 141: instantiating the radius-two BFS certificate
-/

namespace WrittenOnTheWallII.GraphConjecture141RadiusTwoInstantiation

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141BfsGirthBound
open WrittenOnTheWallII.GraphConjecture141RadiusTwoAcyclic
open WrittenOnTheWallII.GraphConjecture141GirthSevenExistence
open WrittenOnTheWallII.GraphConjecture141EccentricityThree

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- First and second BFS layers around a root. -/
def firstLayer (G : SimpleGraph V) (v : V) : Set V := G.neighborSet v
def secondLayer (G : SimpleGraph V) (v : V) : Set V := {w | G.dist v w = 2}
def evenLayer (G : SimpleGraph V) (v : V) : Set V := {v} ∪ secondLayer G v

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- An edge inside the second layer closes a triangle or a 5-cycle through
shortest-path parents, contradicting girth at least eight. -/
lemma secondLayer_independent_of_eight_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 8 ≤ G.girth)
    (v : V) : G.IsIndepSet (secondLayer G v) := by
  intro x hx y hy hxy hxyAdj
  obtain ⟨a, hva, hax⟩ :=
    distance_two_has_neighbor_parent G hconn (show G.dist v x = 2 from hx)
  obtain ⟨b, hvb, hby⟩ :=
    distance_two_has_neighbor_parent G hconn (show G.dist v y = 2 from hy)
  by_cases hab : a = b
  · subst b
    let c : G.Walk a a := .cons hax (.cons hxyAdj (.cons hby.symm .nil))
    have hc : c.IsCycle := by
      have hxa : x ≠ a := hax.ne.symm
      have hya : y ≠ a := hby.ne.symm
      simp [c, Walk.isCycle_def, Walk.isTrail_def, hxy,
        hxa, hxa.symm, hya, hya.symm]
    have := G.girth_le_length hc
    simp only [c, Walk.length_cons, Walk.length_nil] at this
    omega
  · have hav : a ≠ v := hva.ne.symm
    have hbv : b ≠ v := hvb.ne.symm
    have hxv : x ≠ v := by
      intro h
      subst x
      have := show G.dist v v = 2 from hx
      simp at this
    have hyv : y ≠ v := by
      intro h
      subst y
      have := show G.dist v v = 2 from hy
      simp at this
    have hxb : x ≠ b := by
      intro h
      subst b
      have hd : G.dist v x = 2 := hx
      have hone : G.dist v x = 1 := dist_eq_one_iff_adj.mpr hvb
      omega
    have hay : a ≠ y := by
      intro h
      subst y
      have hd : G.dist v a = 2 := hy
      have hone : G.dist v a = 1 := dist_eq_one_iff_adj.mpr hva
      omega
    let c : G.Walk v v :=
      .cons hva (.cons hax (.cons hxyAdj (.cons hby.symm (.cons hvb.symm .nil))))
    have hc : c.IsCycle := by
      have hba : b ≠ a := Ne.symm hab
      have hvx' : v ≠ x := Ne.symm hxv
      have hvy' : v ≠ y := Ne.symm hyv
      have hbx : b ≠ x := Ne.symm hxb
      have hya : y ≠ a := Ne.symm hay
      have hyx : y ≠ x := Ne.symm hxy
      have haxne : a ≠ x := hax.ne
      have hyb : y ≠ b := hby.ne.symm
      simp [c, Walk.isCycle_def, Walk.isTrail_def, hab, hav, hbv,
        hxv, hvx', hyv, hvy', hxb, hay, hxy, haxne, hyb]
    have := G.girth_le_length hc
    simp only [c, Walk.length_cons, Walk.length_nil] at this
    omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- The even layer is independent: the root is nonadjacent to distance-two
vertices and the second layer is independent. -/
lemma evenLayer_independent_of_eight_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 8 ≤ G.girth)
    (v : V) : G.IsIndepSet (evenLayer G v) := by
  intro x hx y hy hxy hxyAdj
  rcases hx with hxv | hx2 <;> rcases hy with hyv | hy2
  · exact hxy (hxv.trans hyv.symm)
  · subst x
    have hd : G.dist v y = 2 := hy2
    have : G.dist v y = 1 := dist_eq_one_iff_adj.mpr hxyAdj
    omega
  · subst y
    have hd : G.dist v x = 2 := hx2
    have : G.dist v x = 1 := dist_eq_one_iff_adj.mpr hxyAdj.symm
    omega
  · exact secondLayer_independent_of_eight_le_girth G hconn hgirth v
      hx2 hy2 hxy hxyAdj

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- The BFS layers around a radius-two center satisfy the exceptional-root
forest certificate. -/
def radiusTwoForestCertificate
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 8 ≤ G.girth)
    (v : V) (hrad : RadiusTwoCenter G v) :
    RadiusTwoForestCertificate G where
  even := evenLayer G v
  odd := firstLayer G v
  root := v
  cover := by
    ext w
    simp only [evenLayer, firstLayer, secondLayer, Set.mem_union,
      Set.mem_singleton_iff, Set.mem_setOf_eq, Set.mem_univ, iff_true]
    rcases radiusTwoCenter_classification G hconn v hrad w with h | h | h
    · exact Or.inl (Or.inl h)
    · exact Or.inr h
    · exact Or.inl (Or.inr h)
  evenIndependent := evenLayer_independent_of_eight_le_girth
    G hconn hgirth v
  oddIndependent := by
    exact locallyIndependent_of_six_le_girth G (by omega) v
  root_even := Or.inl rfl
  other_even_unique := by
    intro i hi hiv x hx y hy hix hiy
    have hi2 : G.dist v i = 2 := by
      rcases hi with h | h
      · exact (hiv h).elim
      · exact h
    obtain ⟨u, hvu, hui⟩ := distance_two_has_neighbor_parent G hconn hi2
    have hxu := unique_neighbor_attachment_of_six_le_girth
      G (by omega) hvu hui hiv x hx hix
    have hyu := unique_neighbor_attachment_of_six_le_girth
      G (by omega) hvu hui hiv y hy hiy
    exact hxu.trans hyu.symm

omit [Fintype V] [Nonempty V] in
/-- A connected graph of girth at least eight cannot have a radius-two
center: its BFS layers certify that it is acyclic, contradicting positive
girth. -/
theorem not_radiusTwoCenter_of_connected_of_eight_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 8 ≤ G.girth)
    (v : V) : ¬RadiusTwoCenter G v := by
  intro hrad
  have hacyc := (radiusTwoForestCertificate G hconn hgirth v hrad).isAcyclic
  have hzero := hacyc.girth_eq_zero
  omega

omit [Fintype V] [Nonempty V] in
/-- **Closed BFS radius-girth consequence.** Every vertex of a connected
graph of girth at least eight has a vertex at distance at least three. -/
theorem everyVertexHasDistanceAtLeastThree_of_connected_of_eight_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 8 ≤ G.girth) :
    EveryVertexHasDistanceAtLeastThree G := by
  by_contra h
  obtain ⟨v, hv⟩ :=
    (not_everyVertexHasDistanceAtLeastThree_iff G).mp h
  exact not_radiusTwoCenter_of_connected_of_eight_le_girth
    G hconn hgirth v hv

end WrittenOnTheWallII.GraphConjecture141RadiusTwoInstantiation
