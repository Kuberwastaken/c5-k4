import GraphConjecture141GirthSevenExistence

/-!
# WOWII 141: extracting the distance-two witness
-/

namespace WrittenOnTheWallII.GraphConjecture141DistanceTwoExistence

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141GirthSevenExistence
open WrittenOnTheWallII.GraphConjecture141Extraction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- The one residual global property isolated by the girth proof: every
vertex has a nonneighbor distinct from itself. -/
def EveryVertexHasNonneighbor (G : SimpleGraph V) : Prop :=
  ∀ v, ∃ w, w ≠ v ∧ ¬G.Adj v w

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A cyclic graph with independent open neighborhoods has a nonneighbor at
every vertex.  Otherwise that vertex is universal and the graph is an
acyclic star. -/
lemma everyVertexHasNonneighbor_of_not_isAcyclic_of_locallyIndependent
    (G : SimpleGraph V) (hcyc : ¬G.IsAcyclic)
    (hlocal : LocallyIndependent G) :
    EveryVertexHasNonneighbor G := by
  intro v
  by_contra hnone
  push_neg at hnone
  apply hcyc
  apply isAcyclic_of_independent_parts_of_left_unique_neighbor
    (G := G) (G.neighborSet v) {v}
  · ext w
    simp only [Set.mem_union, Set.mem_univ, iff_true, Set.mem_singleton_iff]
    by_cases hwv : w = v
    · exact Or.inr hwv
    · exact Or.inl (hnone w hwv)
  · exact hlocal v
  · intro x hx y hy hxy hadj
    simp only [Set.mem_singleton_iff] at hx hy
    exact hxy (hx.trans hy.symm)
  · intro i hi x hx y hy _ _
    simpa only [Set.mem_singleton_iff] using hx.trans hy.symm

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Positive girth means a cycle exists under the repository's zero-for-
acyclic convention. -/
lemma not_isAcyclic_of_pos_girth (G : SimpleGraph V) (hgirth : 0 < G.girth) :
    ¬G.IsAcyclic := by
  intro hacyc
  have := hacyc.girth_eq_zero
  omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Consequently girth at least six supplies the global nonneighbor property
needed by the shortest-path extraction. -/
theorem everyVertexHasNonneighbor_of_six_le_girth
    (G : SimpleGraph V) (hgirth : 6 ≤ G.girth) :
    EveryVertexHasNonneighbor G := by
  apply everyVertexHasNonneighbor_of_not_isAcyclic_of_locallyIndependent G
  · apply not_isAcyclic_of_pos_girth G
    omega
  · exact locallyIndependent_of_six_le_girth G hgirth

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Connectedness turns a nonneighbor into the required first two steps of a
shortest path. -/
lemma exists_distanceTwoPath_of_connected_of_exists_nonneighbor
    (G : SimpleGraph V) (hconn : G.Connected) (v : V)
    (hnon : ∃ w, w ≠ v ∧ ¬G.Adj v w) :
    ∃ u x : V, G.Adj v u ∧ G.Adj u x ∧ x ≠ v ∧ ¬G.Adj v x := by
  obtain ⟨w, hwv, hvw⟩ := hnon
  obtain ⟨p, hpPath, hpLength⟩ := hconn.exists_path_of_dist v w
  have hlen : 2 ≤ p.length := by
    have hgt : 1 < G.dist v w :=
      hconn.one_lt_dist_of_ne_of_not_adj hwv.symm hvw
    omega
  let u := p.getVert 1
  let x := p.getVert 2
  refine ⟨u, x, ?_, ?_, ?_, ?_⟩
  · simpa [u, p.getVert_zero] using p.adj_getVert_succ (by omega : 0 < p.length)
  · simpa [u, x] using p.adj_getVert_succ (by omega : 1 < p.length)
  · intro hxv
    have hnodup := hpPath.support_nodup
    have h0mem : v = p.support[0]'(by simp [p.length_support]) := by
      simpa using p.getVert_eq_support_getElem (n := 0) (by omega : 0 ≤ p.length)
    have h2mem : x = p.support[2]'(by simp [p.length_support, hlen]) := by
      simpa [x] using
        p.getVert_eq_support_getElem (n := 2) (by omega : 2 ≤ p.length)
    have helem : p.support[0]'(by simp [p.length_support]) =
        p.support[2]'(by simp [p.length_support, hlen]) :=
      h0mem.symm.trans (hxv.symm.trans h2mem)
    have : (0 : Nat) = 2 := hnodup.getElem_inj_iff.mp helem
    omega
  · intro hvx
    let q : G.Walk v w := hvx.toWalk.append (p.drop 2)
    have hq : G.dist v w ≤ q.length := G.dist_le q
    have hdrop : (p.drop 2).length = p.length - 2 := by
      simp [Walk.drop_length]
    simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
      zero_add] at hq
    rw [hdrop, ← hpLength] at hq
    omega

omit [DecidableEq V] [Nonempty V] in
/-- Therefore the all-centers nonneighbor condition supplies the exact
maximum-center path property used by v0.11. -/
theorem maximumCenterHasDistanceTwoPath_of_connected_of_everyVertexHasNonneighbor
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hnon : EveryVertexHasNonneighbor G) :
    MaximumCenterHasDistanceTwoPath G := by
  intro v _hvmax
  exact exists_distanceTwoPath_of_connected_of_exists_nonneighbor
    G hconn v (hnon v)

/-- Exact WOWII 141 through girth seven under the remaining global
nonneighbor property. -/
theorem conjecture141_of_girth_six_or_seven_of_everyVertexHasNonneighbor
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected)
    (hgirthLower : 6 ≤ G.girth) (hgirthUpper : G.girth ≤ 7)
    (hnon : EveryVertexHasNonneighbor G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  apply conjecture141_of_girth_six_or_seven_of_maximumCenterHasDistanceTwoPath
    G hgirthLower hgirthUpper
  exact maximumCenterHasDistanceTwoPath_of_connected_of_everyVertexHasNonneighbor
    G hconn hnon

/-- **Unconditional girth-six/seven branch.** Connectedness and the girth
lower bound now construct the distance-two witness automatically. -/
theorem conjecture141_of_girth_six_or_seven
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected)
    (hgirthLower : 6 ≤ G.girth) (hgirthUpper : G.girth ≤ 7) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  exact conjecture141_of_girth_six_or_seven_of_everyVertexHasNonneighbor
    G hconn hgirthLower hgirthUpper
      (everyVertexHasNonneighbor_of_six_le_girth G hgirthLower)

/-- **Closed low-girth theorem.** WOWII 141 holds unconditionally for every
connected finite graph of girth at most seven. -/
theorem conjecture141_of_girth_le_seven
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hgirth : G.girth ≤ 7) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  by_cases hsmall : G.girth ≤ 5
  · exact conjecture141_of_girth_le_five G hsmall
  · apply conjecture141_of_girth_six_or_seven G hconn
    · omega
    · exact hgirth

end WrittenOnTheWallII.GraphConjecture141DistanceTwoExistence
