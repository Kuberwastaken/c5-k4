import GraphConjecture141RadiusGirth

/-!
# WOWII 141: radius-two BFS obstruction
-/

namespace WrittenOnTheWallII.GraphConjecture141BfsGirthBound

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141DistanceTwoExistence
open WrittenOnTheWallII.GraphConjecture141EccentricityThree

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- A vertex whose entire connected component lies within distance two. -/
def RadiusTwoCenter (G : SimpleGraph V) (v : V) : Prop :=
  ∀ w, G.dist v w ≤ 2

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Failure of the desired all-vertex distance-three property is exactly the
existence of a radius-two center. -/
lemma not_everyVertexHasDistanceAtLeastThree_iff
    (G : SimpleGraph V) :
    ¬EveryVertexHasDistanceAtLeastThree G ↔ ∃ v, RadiusTwoCenter G v := by
  constructor
  · intro h
    unfold EveryVertexHasDistanceAtLeastThree at h
    push_neg at h
    obtain ⟨v, hv⟩ := h
    refine ⟨v, ?_⟩
    intro w
    have := hv w
    omega
  · rintro ⟨v, hv⟩ hall
    unfold EveryVertexHasDistanceAtLeastThree at hall
    obtain ⟨w, hw⟩ := hall v
    have := hv w
    omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- In a connected graph, the vertices around a radius-two center split
exactly into the root, its open neighborhood, and distance-two vertices. -/
lemma radiusTwoCenter_classification
    (G : SimpleGraph V) (hconn : G.Connected) (v : V)
    (hrad : RadiusTwoCenter G v) (w : V) :
    w = v ∨ G.Adj v w ∨ G.dist v w = 2 := by
  by_cases hwv : w = v
  · exact Or.inl hwv
  right
  by_cases hadj : G.Adj v w
  · exact Or.inl hadj
  · right
    have hpos := hconn.pos_dist_of_ne (Ne.symm hwv)
    have hneone : G.dist v w ≠ 1 := fun h => hadj (dist_eq_one_iff_adj.mp h)
    have hle := hrad w
    omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- At positive girth at least six, a radius-two center has a genuine second
layer: otherwise it would be universal, contradicting the cyclic star
argument from v0.12. -/
lemma radiusTwoCenter_has_distance_two_of_six_le_girth
    (G : SimpleGraph V) (hconn : G.Connected)
    (hgirth : 6 ≤ G.girth) (v : V) (hrad : RadiusTwoCenter G v) :
    ∃ w, G.dist v w = 2 := by
  obtain ⟨w, hwv, hvw⟩ := everyVertexHasNonneighbor_of_six_le_girth G hgirth v
  refine ⟨w, ?_⟩
  rcases radiusTwoCenter_classification G hconn v hrad w with h | h | h
  · exact (hwv h).elim
  · exact (hvw h).elim
  · exact h

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Every second-layer vertex has a first-layer parent, extracted from a
shortest path. -/
lemma distance_two_has_neighbor_parent
    (G : SimpleGraph V) (hconn : G.Connected) {v w : V}
    (hdist : G.dist v w = 2) :
    ∃ u, G.Adj v u ∧ G.Adj u w := by
  obtain ⟨p, _hpPath, hpLength⟩ := hconn.exists_path_of_dist v w
  let u := p.getVert 1
  refine ⟨u, ?_, ?_⟩
  · simpa [u, p.getVert_zero, hpLength, hdist] using
      p.adj_getVert_succ (by omega : 0 < p.length)
  · have hend : p.getVert 2 = w := by
      have hp2 : p.length = 2 := hpLength.trans hdist
      rw [← hp2]
      exact p.getVert_length
    simpa [u, hend, hpLength, hdist] using
      p.adj_getVert_succ (by omega : 1 < p.length)

/-- The direct girth-eight theorem is reduced to excluding a connected
cyclic radius-two BFS layering.  This implication is deliberately exposed,
not postulated as an axiom. -/
def NoCyclicRadiusTwoLayer (G : SimpleGraph V) : Prop :=
  ∀ v, RadiusTwoCenter G v → G.IsAcyclic

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Once the radius-two BFS exclusion is available, girth at least eight
forces distance at least three from every vertex. -/
theorem everyVertexHasDistanceAtLeastThree_of_noCyclicRadiusTwoLayer
    (G : SimpleGraph V) (hgirth : 8 ≤ G.girth)
    (hBfs : NoCyclicRadiusTwoLayer G) :
    EveryVertexHasDistanceAtLeastThree G := by
  by_contra h
  obtain ⟨v, hv⟩ :=
    (not_everyVertexHasDistanceAtLeastThree_iff G).mp h
  have hacyc := hBfs v hv
  have hzero := hacyc.girth_eq_zero
  omega

end WrittenOnTheWallII.GraphConjecture141BfsGirthBound
