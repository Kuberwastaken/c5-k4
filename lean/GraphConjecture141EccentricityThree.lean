import GraphConjecture141GirthNine

/-!
# WOWII 141: the eccentricity-three bridge
-/

namespace WrittenOnTheWallII.GraphConjecture141EccentricityThree

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141GirthNine

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- Every vertex has some vertex at graph distance at least three. -/
def EveryVertexHasDistanceAtLeastThree (G : SimpleGraph V) : Prop :=
  ∀ v, ∃ w, 3 ≤ G.dist v w

/-- Only the centers attaining maximum local independence need the distance
three property for WOWII 141. -/
def MaximumCenterHasDistanceAtLeastThree
    (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v, indepNeighborsCard G v = Finset.univ.sup (indepNeighborsCard G) →
    ∃ w, 3 ≤ G.dist v w

/-- Exact simple three-edge prefix required by the two-tail construction. -/
def MaximumCenterHasThreeEdgePrefix
    (G : SimpleGraph V) [DecidableRel G.Adj] : Prop :=
  ∀ v, indepNeighborsCard G v = Finset.univ.sup (indepNeighborsCard G) →
    ∃ u x y : V,
      G.Adj v u ∧ G.Adj u x ∧ G.Adj x y ∧
      v ≠ u ∧ v ≠ x ∧ v ≠ y ∧ u ≠ x ∧ u ≠ y ∧ x ≠ y ∧
      ¬G.Adj v x ∧ ¬G.Adj v y ∧ ¬G.Adj u y

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A shortest path of length at least three supplies a chordless three-edge
prefix.  The nonedges follow from replacing two or three initial edges by a
shortcut. -/
lemma exists_threeEdgePrefix_of_connected_of_three_le_dist
    (G : SimpleGraph V) (hconn : G.Connected) (v w : V)
    (hdist : 3 ≤ G.dist v w) :
    ∃ u x y : V,
      G.Adj v u ∧ G.Adj u x ∧ G.Adj x y ∧
      v ≠ u ∧ v ≠ x ∧ v ≠ y ∧ u ≠ x ∧ u ≠ y ∧ x ≠ y ∧
      ¬G.Adj v x ∧ ¬G.Adj v y ∧ ¬G.Adj u y := by
  obtain ⟨p, hpPath, hpLength⟩ := hconn.exists_path_of_dist v w
  have hlen : 3 ≤ p.length := by omega
  let u := p.getVert 1
  let x := p.getVert 2
  let y := p.getVert 3
  have hvu : G.Adj v u := by
    simpa [u, p.getVert_zero] using
      p.adj_getVert_succ (by omega : 0 < p.length)
  have hux : G.Adj u x := by
    simpa [u, x] using p.adj_getVert_succ (by omega : 1 < p.length)
  have hxy : G.Adj x y := by
    simpa [x, y] using p.adj_getVert_succ (by omega : 2 < p.length)
  have hinj : Function.Injective (fun i : Fin p.support.length => p.support.get i) :=
    (p.isPath_iff_injective_get_support.mp hpPath)
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
  have hvu_ne : v ≠ u := by
    simpa [u, p.getVert_zero] using hne 0 1 (by omega) (by omega) (by omega)
  have hvx_ne : v ≠ x := by
    simpa [x, p.getVert_zero] using hne 0 2 (by omega) (by omega) (by omega)
  have hvy_ne : v ≠ y := by
    simpa [y, p.getVert_zero] using hne 0 3 (by omega) (by omega) (by omega)
  have hux_ne : u ≠ x := by
    simpa [u, x] using hne 1 2 (by omega) (by omega) (by omega)
  have huy_ne : u ≠ y := by
    simpa [u, y] using hne 1 3 (by omega) (by omega) (by omega)
  have hxy_ne : x ≠ y := by
    simpa [x, y] using hne 2 3 (by omega) (by omega) (by omega)
  refine ⟨u, x, y, hvu, hux, hxy, hvu_ne, hvx_ne, hvy_ne,
    hux_ne, huy_ne, hxy_ne, ?_, ?_, ?_⟩
  · intro hvx
    let q : G.Walk v w := hvx.toWalk.append (p.drop 2)
    have hq := G.dist_le q
    simp [q, Walk.drop_length, ← hpLength] at hq
    omega
  · intro hvy
    let q : G.Walk v w := hvy.toWalk.append (p.drop 3)
    have hq := G.dist_le q
    simp [q, Walk.drop_length, ← hpLength] at hq
    omega
  · intro huy
    let q : G.Walk v w := hvu.toWalk.append (huy.toWalk.append (p.drop 3))
    have hq := G.dist_le q
    simp [q, Walk.drop_length, ← hpLength] at hq
    omega

omit [DecidableEq V] [Nonempty V] in
/-- Eccentricity at least three at maximum centers supplies the exact
shortest-path prefix. -/
theorem maximumCenterHasThreeEdgePrefix_of_connected
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hecc : MaximumCenterHasDistanceAtLeastThree G) :
    MaximumCenterHasThreeEdgePrefix G := by
  intro v hvmax
  obtain ⟨w, hvw⟩ := hecc v hvmax
  exact exists_threeEdgePrefix_of_connected_of_three_le_dist G hconn v w hvw

omit [DecidableEq V] [Nonempty V] in
/-- The all-centers version implies the maximum-center version. -/
theorem maximumCenterHasDistanceAtLeastThree_of_everyVertex
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (h : EveryVertexHasDistanceAtLeastThree G) :
    MaximumCenterHasDistanceAtLeastThree G := by
  intro v _
  exact h v

omit [Nonempty V] in
/-- Strongest currently certified girth-eight/nine class: an explicit
two-tail splice closes WOWII 141.  The eccentricity lemma above supplies the
only unresolved global path-existence half of constructing that splice. -/
theorem conjecture141_of_girth_eight_or_nine_of_eccentricity_and_tail
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 8 ≤ G.girth) (hgirthUpper : G.girth ≤ 9)
    (_hecc : MaximumCenterHasDistanceAtLeastThree G)
    (W : TwoVertexTailSplice G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  exact conjecture141_of_girth_eight_or_nine_of_twoVertexTailSplice
    G hgirthLower hgirthUpper W

end WrittenOnTheWallII.GraphConjecture141EccentricityThree
