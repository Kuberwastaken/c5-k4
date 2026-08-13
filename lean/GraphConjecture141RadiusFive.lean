import GraphConjecture141GirthThirteenClosure

/-!
# WOWII 141: scalable radius-five exclusion

The canonical geodesic-splice estimates scale one further rank.  Horizontal
edges through BFS rank five close within length eleven, and two preceding
parents close within length ten.  At girth twelve this gives the same forest
certificate and therefore a distance-six witness from every root.
-/

namespace WrittenOnTheWallII.GraphConjecture141RadiusFive

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141RadiusThreeAcyclic
open WrittenOnTheWallII.GraphConjecture141EqualLayerClosure
open WrittenOnTheWallII.GraphConjecture141UniqueParent

universe u
variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- A root whose entire connected component lies within distance five. -/
def RadiusFiveCenter (G : SimpleGraph V) (r : V) : Prop :=
  ∀ v, G.dist r v ≤ 5

/-- The distance-six witness needed by the next tail extension. -/
def EveryVertexHasDistanceAtLeastSix (G : SimpleGraph V) : Prop :=
  ∀ r, ∃ v, 6 ≤ G.dist r v

omit [Fintype V] [DecidableEq V] [Nonempty V] in
lemma not_everyVertexHasDistanceAtLeastSix_iff (G : SimpleGraph V) :
    ¬EveryVertexHasDistanceAtLeastSix G ↔ ∃ r, RadiusFiveCenter G r := by
  constructor
  · intro h
    unfold EveryVertexHasDistanceAtLeastSix at h
    push_neg at h
    obtain ⟨r, hr⟩ := h
    exact ⟨r, fun v => by have := hr v; omega⟩
  · rintro ⟨r, hr⟩ hall
    obtain ⟨v, hv⟩ := hall r
    have := hr v
    omega

omit [Fintype V] [Nonempty V] in
/-- Equal-rank geodesics through rank five and a horizontal edge close to a
cycle of length at most eleven. -/
theorem bfsLayer_independent_of_twelve_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 12 ≤ G.girth)
    (r : V) (k : ℕ) (hk : k ≤ 5) :
    G.IsIndepSet (bfsLayer G r k) := by
  intro x hx y hy hxy hadj
  obtain ⟨p, _hpPath, hpDist⟩ := hconn.exists_path_of_dist r x
  obtain ⟨q, _hqPath, hqDist⟩ := hconn.exists_path_of_dist r y
  have hpLen : p.length = k := hpDist.trans hx
  have hqLen : q.length = k := hqDist.trans hy
  have hlen : p.length = q.length := hpLen.trans hqLen.symm
  obtain ⟨c, hc, hcLen⟩ := bounded_cycle_of_equal_geodesic_endpoint_edge
    p q hpDist hqDist hlen hxy hadj.symm
  have hgirthLe := G.girth_le_length hc
  omega

omit [Fintype V] [Nonempty V] in
/-- Through rank five, two preceding-layer parents create a cycle of length
at most ten and therefore coincide at girth at least twelve. -/
theorem uniqueParent_of_twelve_le_girth_rank_five
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 12 ≤ G.girth)
    (r v x y : V) (_hvroot : v ≠ r)
    (hvRank : G.dist r v ≤ 5)
    (hvx : G.Adj v x) (hvy : G.Adj v y)
    (hxrank : G.dist r x + 1 = G.dist r v)
    (hyrank : G.dist r y + 1 = G.dist r v) : x = y := by
  by_contra hxy
  obtain ⟨p, _hpPath, hpDist⟩ := hconn.exists_path_of_dist r x
  obtain ⟨q, _hqPath, hqDist⟩ := hconn.exists_path_of_dist r y
  have hlen : p.length = q.length := by
    rw [hpDist, hqDist]
    omega
  obtain ⟨c, hc, hcLen⟩ := bounded_cycle_of_equal_geodesic_common_child
    p q hpDist hqDist hlen hxy hxrank hyrank hvx hvy
  have hpBound : p.length ≤ 4 := by rw [hpDist]; omega
  have hqBound : q.length ≤ 4 := by rw [hqDist]; omega
  have hgirthLe := G.girth_le_length hc
  omega

omit [Fintype V] [Nonempty V] in
/-- Maximum-rank selection on a simple cycle remains a peak through radius
five. -/
theorem cyclePeak_of_radiusFiveCenter
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 12 ≤ G.girth)
    (r : V) (hrad : RadiusFiveCenter G r) :
    ∀ v (c : G.Walk v v), c.IsCycle →
      ∃ i x y,
        i ≠ r ∧ G.Adj i x ∧ G.Adj i y ∧ x ≠ y ∧
        G.dist r x + 1 = G.dist r i ∧
        G.dist r y + 1 = G.dist r i := by
  intro v c hc
  let S : Finset V := c.support.toFinset
  have hS : S.Nonempty := ⟨v, by simp [S]⟩
  obtain ⟨i, hiS, hiMax⟩ := S.exists_mem_eq_sup hS (G.dist r)
  have hi : i ∈ c.support := by simpa [S] using hiS
  let q := c.rotate hi
  have hq : q.IsCycle := hc.rotate hi
  have hqnil : ¬q.Nil := hq.not_nil
  let x := q.snd
  let y := q.penultimate
  have hxq : x ∈ q.support :=
    List.mem_of_mem_tail (q.snd_mem_tail_support hqnil)
  have hyq : y ∈ q.support :=
    List.mem_of_mem_dropLast (q.penultimate_mem_dropLast_support hqnil)
  have hmax (z : V) (hzq : z ∈ q.support) : G.dist r z ≤ G.dist r i := by
    have hzc : z ∈ c.support := (c.mem_support_rotate_iff hi).mp hzq
    have hzS : z ∈ S := by simpa [S] using hzc
    rw [← hiMax]
    exact Finset.le_sup hzS
  have hir : i ≠ r := by
    intro hir
    subst i
    have hxle := hmax x hxq
    have hix : G.Adj r x := by simpa [q, x] using q.adj_snd hqnil
    rw [SimpleGraph.dist_self] at hxle
    have hzero : G.dist r x = 0 := Nat.eq_zero_of_le_zero hxle
    exact hix.ne ((hconn.dist_eq_zero_iff).mp hzero)
  have hix : G.Adj i x := by simpa [q, x] using q.adj_snd hqnil
  have hiy : G.Adj i y := by
    simpa [q, y] using (q.adj_penultimate hqnil).symm
  have hxy : x ≠ y := by simpa [q, x, y] using hq.snd_ne_penultimate
  have hiRank : G.dist r i ≤ 5 := hrad i
  have hxne : G.dist r x ≠ G.dist r i := by
    intro heq
    have hind := bfsLayer_independent_of_twelve_le_girth
      G hconn hgirth r (G.dist r i) hiRank
    exact hind (by rfl) heq hix.ne hix
  have hyne : G.dist r y ≠ G.dist r i := by
    intro heq
    have hind := bfsLayer_independent_of_twelve_le_girth
      G hconn hgirth r (G.dist r i) hiRank
    exact hind (by rfl) heq hiy.ne hiy
  have hxle := hmax x hxq
  have hyle := hmax y hyq
  have hxrank : G.dist r x + 1 = G.dist r i := by
    rcases hix.diff_dist_adj (u := r) with h | h | h <;> omega
  have hyrank : G.dist r y + 1 = G.dist r i := by
    rcases hiy.diff_dist_adj (u := r) with h | h | h <;> omega
  exact ⟨i, x, y, hir, hix, hiy, hxy, hxrank, hyrank⟩

/-- The rank-generic forest certificate instantiated through radius five. -/
noncomputable def radiusFiveForestCertificate
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 12 ≤ G.girth)
    (r : V) (hrad : RadiusFiveCenter G r) :
    RadiusThreeForestCertificate G where
  root := r
  rank := G.dist r
  rootRank := by simp
  uniqueParent := by
    intro v hvroot x y hvx hvy hxrank hyrank
    exact uniqueParent_of_twelve_le_girth_rank_five G hconn hgirth r v x y
      hvroot (hrad v) hvx hvy hxrank hyrank
  cyclePeak := cyclePeak_of_radiusFiveCenter G hconn hgirth r hrad

omit [Fintype V] [Nonempty V] in
/-- **Closed radius-five branch.** Every root in a connected graph of girth
at least twelve reaches a vertex at distance at least six. -/
theorem everyVertexHasDistanceAtLeastSix_of_connected_of_twelve_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 12 ≤ G.girth) :
    EveryVertexHasDistanceAtLeastSix G := by
  by_contra h
  obtain ⟨r, hrad⟩ := (not_everyVertexHasDistanceAtLeastSix_iff G).mp h
  have hacyc := (radiusFiveForestCertificate G hconn hgirth r hrad).isAcyclic
  have hzero := hacyc.girth_eq_zero
  omega

end WrittenOnTheWallII.GraphConjecture141RadiusFive
