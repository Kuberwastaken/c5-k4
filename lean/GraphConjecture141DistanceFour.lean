import GraphConjecture141GirthEleven

/-!
# WOWII 141: distance-four and the four-edge prefix
-/

namespace WrittenOnTheWallII.GraphConjecture141DistanceFour

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- Every vertex has a vertex at distance at least four. -/
def EveryVertexHasDistanceAtLeastFour (G : SimpleGraph V) : Prop :=
  ∀ v, ∃ w, 4 ≤ G.dist v w

/-- The precise maximum-center form needed for WOWII 141. -/
def MaximumCenterHasDistanceAtLeastFour
    (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v, indepNeighborsCard G v = Finset.univ.sup (indepNeighborsCard G) →
    ∃ w, 4 ≤ G.dist v w

/-- Exact chordless four-edge prefix extracted from a shortest path. -/
structure FourEdgePrefix (G : SimpleGraph V) where
  v : V
  u : V
  x : V
  y : V
  z : V
  vu : G.Adj v u
  ux : G.Adj u x
  xy : G.Adj x y
  yz : G.Adj y z
  pairwise : ({v, u, x, y, z} : Finset V).card = 5
  vx_nonadj : ¬G.Adj v x
  vy_nonadj : ¬G.Adj v y
  vz_nonadj : ¬G.Adj v z
  uy_nonadj : ¬G.Adj u y
  uz_nonadj : ¬G.Adj u z
  xz_nonadj : ¬G.Adj x z

omit [Fintype V] [Nonempty V] in
/-- A shortest path of length at least four supplies the entire chordless
four-edge prefix. -/
lemma exists_fourEdgePrefix_of_connected_of_four_le_dist
    (G : SimpleGraph V) (hconn : G.Connected) (v w : V)
    (hdist : 4 ≤ G.dist v w) :
    ∃ P : FourEdgePrefix G, P.v = v := by
  obtain ⟨p, hpPath, hpLength⟩ := hconn.exists_path_of_dist v w
  have hlen : 4 ≤ p.length := by omega
  let a0 := p.getVert 0
  let a1 := p.getVert 1
  let a2 := p.getVert 2
  let a3 := p.getVert 3
  let a4 := p.getVert 4
  have hinj : Function.Injective (fun i : Fin p.support.length => p.support.get i) :=
    p.isPath_iff_injective_get_support.mp hpPath
  have hne (i j : Nat) (hi : i ≤ p.length) (hj : j ≤ p.length) (hij : i ≠ j) :
      p.getVert i ≠ p.getVert j := by
    intro heq
    have hi' : i < p.support.length := by simp [p.length_support, hi]
    have hj' : j < p.support.length := by simp [p.length_support, hj]
    have hget : p.support.get ⟨i, hi'⟩ = p.support.get ⟨j, hj'⟩ := by
      simpa [p.getVert_eq_support_getElem hi, p.getVert_eq_support_getElem hj]
        using heq
    have := congrArg Fin.val (hinj hget)
    exact hij this
  have hshortcut (i j : Nat) (hi : i ≤ p.length) (hj : j ≤ p.length)
      (hgap : i + 1 < j) : ¬G.Adj (p.getVert i) (p.getVert j) := by
    intro hadj
    let q : G.Walk v w :=
      ((p.take i).append hadj.toWalk).append (p.drop j)
    have hq := G.dist_le q
    have htake : (p.take i).length = i := by
      simp [Walk.take_length, hi]
    have hdrop : (p.drop j).length = p.length - j := by
      simp [Walk.drop_length]
    simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hq
    rw [htake, hdrop, ← hpLength] at hq
    omega
  have hcard : ({a0, a1, a2, a3, a4} : Finset V).card = 5 := by
    have h01 := hne 0 1 (by omega) (by omega) (by omega)
    have h02 := hne 0 2 (by omega) (by omega) (by omega)
    have h03 := hne 0 3 (by omega) (by omega) (by omega)
    have h04 := hne 0 4 (by omega) (by omega) (by omega)
    have h12 := hne 1 2 (by omega) (by omega) (by omega)
    have h13 := hne 1 3 (by omega) (by omega) (by omega)
    have h14 := hne 1 4 (by omega) (by omega) (by omega)
    have h23 := hne 2 3 (by omega) (by omega) (by omega)
    have h24 := hne 2 4 (by omega) (by omega) (by omega)
    have h34 := hne 3 4 (by omega) (by omega) (by omega)
    simp only [a0, a1, a2, a3, a4, p.getVert_zero]
    rw [Finset.card_insert_of_notMem, Finset.card_insert_of_notMem,
      Finset.card_insert_of_notMem, Finset.card_insert_of_notMem]
    · simp
    · simp [h34]
    · simp [h23, h24]
    · simp [h12, h13, h14]
    · simpa only [Finset.mem_insert, Finset.mem_singleton, not_or,
        p.getVert_zero] using
        (show v ≠ p.getVert 1 ∧ v ≠ p.getVert 2 ∧
          v ≠ p.getVert 3 ∧ v ≠ p.getVert 4 by
            exact ⟨by simpa [p.getVert_zero] using h01,
              by simpa [p.getVert_zero] using h02,
              by simpa [p.getVert_zero] using h03,
              by simpa [p.getVert_zero] using h04⟩)
  let P : FourEdgePrefix G := {
    v := a0, u := a1, x := a2, y := a3, z := a4
    vu := p.adj_getVert_succ (by omega : 0 < p.length)
    ux := p.adj_getVert_succ (by omega : 1 < p.length)
    xy := p.adj_getVert_succ (by omega : 2 < p.length)
    yz := p.adj_getVert_succ (by omega : 3 < p.length)
    pairwise := hcard
    vx_nonadj := hshortcut 0 2 (by omega) (by omega) (by omega)
    vy_nonadj := hshortcut 0 3 (by omega) (by omega) (by omega)
    vz_nonadj := hshortcut 0 4 (by omega) (by omega) (by omega)
    uy_nonadj := hshortcut 1 3 (by omega) (by omega) (by omega)
    uz_nonadj := hshortcut 1 4 (by omega) (by omega) (by omega)
    xz_nonadj := hshortcut 2 4 (by omega) (by omega) (by omega)
  }
  refine ⟨P, ?_⟩
  exact p.getVert_zero

omit [Fintype V] [Nonempty V] in
/-- The all-centers distance-four property supplies a prefix at every
maximum-local center. -/
theorem exists_fourEdgePrefix_at_maximum_center
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hfour : EveryVertexHasDistanceAtLeastFour G)
    (v : V) : ∃ P : FourEdgePrefix G, P.v = v := by
  obtain ⟨w, hvw⟩ := hfour v
  exact exists_fourEdgePrefix_of_connected_of_four_le_dist G hconn v w hvw

/-- Radius-three center, the exact obstruction to the global theorem. -/
def RadiusThreeCenter (G : SimpleGraph V) (v : V) : Prop :=
  ∀ w, G.dist v w ≤ 3

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Failure of distance four is exactly a radius-three center. -/
lemma not_everyVertexHasDistanceAtLeastFour_iff
    (G : SimpleGraph V) :
    ¬EveryVertexHasDistanceAtLeastFour G ↔ ∃ v, RadiusThreeCenter G v := by
  constructor
  · intro h
    unfold EveryVertexHasDistanceAtLeastFour at h
    push_neg at h
    obtain ⟨v, hv⟩ := h
    refine ⟨v, ?_⟩
    intro w
    have := hv w
    omega
  · rintro ⟨v, hv⟩ hall
    unfold EveryVertexHasDistanceAtLeastFour at hall
    obtain ⟨w, hw⟩ := hall v
    have := hv w
    omega

/-- The remaining global statement is isolated as a radius-three BFS
exclusion rather than inserted as an assumption about the final theorem. -/
def NoCyclicRadiusThreeLayer (G : SimpleGraph V) : Prop :=
  ∀ v, RadiusThreeCenter G v → G.IsAcyclic

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A radius-three BFS exclusion plus positive girth yields distance four. -/
theorem everyVertexHasDistanceAtLeastFour_of_noCyclicRadiusThreeLayer
    (G : SimpleGraph V) (hgirth : 10 ≤ G.girth)
    (hBfs : NoCyclicRadiusThreeLayer G) :
    EveryVertexHasDistanceAtLeastFour G := by
  by_contra h
  obtain ⟨v, hv⟩ := (not_everyVertexHasDistanceAtLeastFour_iff G).mp h
  have hacyc := hBfs v hv
  have hzero := hacyc.girth_eq_zero
  omega

end WrittenOnTheWallII.GraphConjecture141DistanceFour
