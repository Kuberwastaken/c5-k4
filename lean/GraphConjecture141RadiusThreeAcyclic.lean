import GraphConjecture141DistanceFour

/-!
# WOWII 141: radius-three BFS certificate
-/

namespace WrittenOnTheWallII.GraphConjecture141RadiusThreeAcyclic

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141DistanceFour

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- The four BFS layers around a root, represented by exact distance. -/
def bfsLayer (G : SimpleGraph V) (r : V) (k : ℕ) : Set V :=
  {v | G.dist r v = k}

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A radius-three center gives an exact four-layer cover. -/
lemma radiusThreeCenter_layer_classification
    (G : SimpleGraph V) (_hconn : G.Connected) (r : V)
    (hrad : RadiusThreeCenter G r) (v : V) :
    v ∈ bfsLayer G r 0 ∨ v ∈ bfsLayer G r 1 ∨
      v ∈ bfsLayer G r 2 ∨ v ∈ bfsLayer G r 3 := by
  have hle := hrad v
  rcases Nat.eq_zero_or_pos (G.dist r v) with h0 | hpos
  · exact Or.inl h0
  · have hcases : G.dist r v = 1 ∨ G.dist r v = 2 ∨ G.dist r v = 3 := by
      omega
    rcases hcases with h1 | h2 | h3
    · exact Or.inr (Or.inl h1)
    · exact Or.inr (Or.inr (Or.inl h2))
    · exact Or.inr (Or.inr (Or.inr h3))

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Every positive-layer vertex has a neighbor one layer closer to the root,
extracted from a shortest path. -/
lemma positive_layer_has_parent
    (G : SimpleGraph V) (hconn : G.Connected) (r v : V) (k : ℕ)
    (hk : G.dist r v = k + 1) :
    ∃ p, G.Adj p v ∧ G.dist r p = k := by
  obtain ⟨w, _hwPath, hwLength⟩ := hconn.exists_path_of_dist r v
  let p := w.getVert k
  refine ⟨p, ?_, ?_⟩
  · have hlen : w.length = k + 1 := hwLength.trans hk
    have hadj := w.adj_getVert_succ (by omega : k < w.length)
    have hend : w.getVert (k + 1) = v := by
      rw [← hlen]
      exact w.getVert_length
    simpa [p, hend] using hadj
  · have hle : G.dist r p ≤ k := by
      let q := w.take k
      have hq : G.dist r p ≤ q.length := by
        simpa [q, p, w.getVert_zero] using G.dist_le q
      have hklen : k ≤ w.length := by rw [hwLength, hk]; omega
      simpa [q, Walk.take_length, hklen] using hq
    have hlower : k + 1 ≤ G.dist r p + 1 := by
      have hadj : G.Adj p v := by
        have hlen : w.length = k + 1 := hwLength.trans hk
        have ha := w.adj_getVert_succ (by omega : k < w.length)
        have hend : w.getVert (k + 1) = v := by
          rw [← hlen]
          exact w.getVert_length
        simpa [p, hend] using ha
      rcases hadj.diff_dist_adj (u := r) with h | h | h <;> omega
    omega

/-- A rank certificate sufficient for acyclicity.  The `cyclePeak` field is
the exact remaining combinatorial fact needed from the four BFS layers: every
cycle has a non-root maximum-layer vertex whose two cycle neighbors both lie
one layer lower. -/
structure RadiusThreeForestCertificate (G : SimpleGraph V) where
  root : V
  rank : V → ℕ
  rootRank : rank root = 0
  uniqueParent : ∀ v, v ≠ root → ∀ x y,
    G.Adj v x → G.Adj v y → rank x + 1 = rank v →
      rank y + 1 = rank v → x = y
  cyclePeak : ∀ v (c : G.Walk v v), c.IsCycle →
    ∃ i x y,
      i ≠ root ∧ G.Adj i x ∧ G.Adj i y ∧ x ≠ y ∧
      rank x + 1 = rank i ∧ rank y + 1 = rank i

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- The radius-three rank certificate rules out every cycle. -/
theorem RadiusThreeForestCertificate.isAcyclic
    {G : SimpleGraph V} (C : RadiusThreeForestCertificate G) :
    G.IsAcyclic := by
  intro v c hc
  obtain ⟨i, x, y, hir, hix, hiy, hxy, hxrank, hyrank⟩ :=
    C.cyclePeak v c hc
  exact hxy (C.uniqueParent i hir x y hix hiy hxrank hyrank)

/-- Exact remaining BFS instantiation interface for girth ten. -/
def RadiusThreeBfsPeakProperty (G : SimpleGraph V) : Prop :=
  ∀ r, RadiusThreeCenter G r →
    ∃ C : RadiusThreeForestCertificate G,
      C.root = r ∧ C.rank = G.dist r

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Once the peak property is proved from girth, the global distance-four
theorem follows immediately. -/
theorem everyVertexHasDistanceAtLeastFour_of_radiusThreeBfsPeak
    (G : SimpleGraph V) (hgirth : 10 ≤ G.girth)
    (hpeak : RadiusThreeBfsPeakProperty G) :
    EveryVertexHasDistanceAtLeastFour G := by
  apply everyVertexHasDistanceAtLeastFour_of_noCyclicRadiusThreeLayer
    G hgirth
  intro r hrad
  obtain ⟨C, -, -⟩ := hpeak r hrad
  exact C.isAcyclic

end WrittenOnTheWallII.GraphConjecture141RadiusThreeAcyclic
