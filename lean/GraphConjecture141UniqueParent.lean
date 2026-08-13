import GraphConjecture141RadiusThreeLayers

/-!
# WOWII 141: uniqueness of the preceding-layer parent

Two distinct parents in the same BFS layer are joined by their canonical
root-path splice.  Their common child closes that connector with two edges.
Shortestness keeps the child off both parent geodesics, hence off the splice,
so the closure is a simple cycle.  Through radius three its length is at most
eight, contradicting girth at least nine.
-/

namespace WrittenOnTheWallII.GraphConjecture141UniqueParent

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture141EqualLayerClosure
open WrittenOnTheWallII.GraphConjecture141RadiusThreeAcyclic
open WrittenOnTheWallII.GraphConjecture141RootPathSplice
open WrittenOnTheWallII.GraphConjecture141DistanceFour

universe u
variable {V : Type u} [DecidableEq V]

/-- A vertex one layer beyond the endpoint of a geodesic cannot occur on that
geodesic. -/
theorem child_not_mem_parent_geodesic
    {G : SimpleGraph V} {r x v : V} (p : G.Walk r x)
    (hpDist : p.length = G.dist r x)
    (hlayer : G.dist r x + 1 = G.dist r v) :
    v ∉ p.support := by
  intro hvp
  have htake := length_eq_dist_of_subwalk hpDist (p.isSubwalk_takeUntil hvp)
  have hle := p.length_takeUntil_le hvp
  rw [htake] at hle
  omega

omit [DecidableEq V] in
/-- Close a simple `x-y` connector through a fresh common neighbor `v`. -/
theorem close_path_through_common_neighbor
    {G : SimpleGraph V} {x y v : V} (t : G.Walk x y)
    (ht : t.IsPath) (hvNot : v ∉ t.support) (hxy : x ≠ y)
    (hvx : G.Adj v x) (hyv : G.Adj y v) :
    ∃ c : G.Walk v v, c.IsCycle ∧ c.length = t.length + 2 := by
  let e : G.Walk y v := Walk.cons hyv Walk.nil
  have he : e.IsPath := by
    simp [e, Walk.isPath_def, hyv.ne]
  have hte : (t.append e).IsPath := by
    rw [Walk.isPath_def, Walk.support_append]
    exact ht.support_nodup.append he.support_nodup.tail (by
      rw [List.disjoint_left]
      intro z hzT hzE
      simp [e] at hzE
      subst z
      exact hvNot hzT)
  have hedge : s(v, x) ∉ (t.append e).edges := by
    intro h
    rw [Walk.edges_append] at h
    rcases List.mem_append.mp h with htEdge | heEdge
    · exact hvNot (t.fst_mem_support_of_mem_edges htEdge)
    · have heq : v = y ∧ x = v := by
        simpa [e, Sym2.eq, Sym2.rel_iff', hxy, hyv.ne] using heEdge
      exact hxy (heq.2.trans heq.1)
  obtain ⟨c, hc, hlen⟩ := close_spliced_path_with_edge
    (t.append e) hte hvx hedge
  exact ⟨c, hc, by simp [e] at hlen ⊢; omega⟩

/-- Canonical splice with explicit support containment in the two source
geodesics. -/
theorem exists_canonical_splice_support_subset
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hp : p.IsPath) (hq : q.IsPath) :
    ∃ (w : V) (pxr : G.Walk x w) (qy : G.Walk w y),
      (∀ z, z ∈ pxr.support → z ∈ p.support) ∧
      (∀ z, z ∈ qy.support → z ∈ q.support) ∧
      (pxr.append qy).IsPath ∧
      (pxr.append qy).length ≤ p.length + q.length := by
  let s : Finset V := q.support.toFinset
  have hcommon : {z ∈ s | z ∈ p.reverse.support}.Nonempty := by
    refine ⟨r, ?_⟩
    simp only [Finset.mem_filter, s, List.mem_toFinset]
    exact ⟨q.start_mem_support, by
      rw [Walk.support_reverse, List.mem_reverse]
      exact p.start_mem_support⟩
  obtain ⟨w, hwqFin, hwpr, hfirst⟩ :=
    p.reverse.exists_mem_support_forall_mem_support_imp_eq s hcommon
  have hwq : w ∈ q.support := by simpa [s] using hwqFin
  let pxr := p.reverse.takeUntil w hwpr
  let qy := q.dropUntil w hwq
  have hpxr : pxr.IsPath := hp.reverse.takeUntil hwpr
  have hqy : qy.IsPath := hq.dropUntil hwq
  have hwNotQTail : w ∉ qy.support.tail := by
    have hn := hqy.support_nodup
    have hs : qy.support = w :: qy.support.tail :=
      (List.cons_head_tail qy.support_ne_nil).symm.trans (by simp)
    rw [hs, List.nodup_cons] at hn
    exact hn.1
  have hdisj : pxr.support.Disjoint qy.support.tail := by
    rw [List.disjoint_left]
    intro z hzP hzQ
    have hzQ' : z ∈ q.support :=
      q.support_dropUntil_subset hwq (List.mem_of_mem_tail hzQ)
    have hzQFin : z ∈ s := by simpa [s] using hzQ'
    have hzw : z = w := hfirst z hzQFin hzP
    subst z
    exact hwNotQTail hzQ
  have hsplice : (pxr.append qy).IsPath := by
    rw [Walk.isPath_def, Walk.support_append]
    exact hpxr.support_nodup.append hqy.support_nodup.tail hdisj
  refine ⟨w, pxr, qy, ?_, q.support_dropUntil_subset hwq, hsplice, ?_⟩
  · intro z hz
    have hzrev := (p.reverse.support_takeUntil_subset hwpr) hz
    simpa [Walk.support_reverse] using hzrev
  · simp only [Walk.length_append]
    have hpLe : pxr.length ≤ p.length := by
      calc pxr.length ≤ p.reverse.length := p.reverse.length_takeUntil_le hwpr
        _ = p.length := by simp
    have hqLe : qy.length ≤ q.length := q.length_dropUntil_le hwq
    omega

omit [DecidableEq V] in
/-- Equal-layer parent geodesics and a common child produce a simple cycle of
length at most the two geodesic lengths plus two. -/
theorem bounded_cycle_of_equal_geodesic_common_child
    [DecidableEq V]
    {G : SimpleGraph V} {r x y v : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hpDist : p.length = G.dist r x) (hqDist : q.length = G.dist r y)
    (hlen : p.length = q.length) (hxy : x ≠ y)
    (hxLayer : G.dist r x + 1 = G.dist r v)
    (hyLayer : G.dist r y + 1 = G.dist r v)
    (hvx : G.Adj v x) (hvy : G.Adj v y) :
    ∃ c : G.Walk v v,
      c.IsCycle ∧ c.length ≤ p.length + q.length + 2 := by
  have hp : p.IsPath := p.isPath_of_length_eq_dist hpDist
  have hq : q.IsPath := q.isPath_of_length_eq_dist hqDist
  obtain ⟨w, pxr, qy, hpxSub, hqySub, hsplice, hbound⟩ :=
    exists_canonical_splice_support_subset p q hp hq
  have hvp : v ∉ p.support := child_not_mem_parent_geodesic p hpDist hxLayer
  have hvq : v ∉ q.support := child_not_mem_parent_geodesic q hqDist hyLayer
  have hvsplice : v ∉ (pxr.append qy).support := by
    rw [Walk.mem_support_append_iff]
    push_neg
    constructor
    · intro hv
      apply hvp
      exact hpxSub v hv
    · intro hv
      apply hvq
      exact hqySub v hv
  obtain ⟨c, hc, hclen⟩ := close_path_through_common_neighbor
    (pxr.append qy) hsplice hvsplice hxy hvx hvy.symm
  exact ⟨c, hc, by omega⟩

/-- **Unique parent through radius three.** In a connected graph of girth at
least nine, a positive-layer vertex of rank at most three has at most one
neighbor in the preceding layer. -/
theorem uniqueParent_of_nine_le_girth
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 9 ≤ G.girth)
    (r v x y : V) (_hvroot : v ≠ r)
    (hvRank : G.dist r v ≤ 3)
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
  have hpBound : p.length ≤ 2 := by rw [hpDist]; omega
  have hqBound : q.length ≤ 2 := by rw [hqDist]; omega
  have hgirthLe := G.girth_le_length hc
  omega

/-- Exact `RadiusThreeForestCertificate.uniqueParent` field for distance rank
around a radius-three center. -/
theorem radiusThree_uniqueParent
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 9 ≤ G.girth)
    (r : V) (hrad : RadiusThreeCenter G r) :
    ∀ v, v ≠ r → ∀ x y,
      G.Adj v x → G.Adj v y →
      G.dist r x + 1 = G.dist r v →
      G.dist r y + 1 = G.dist r v → x = y := by
  intro v hvroot x y hvx hvy hxrank hyrank
  exact uniqueParent_of_nine_le_girth G hconn hgirth r v x y hvroot
    (hrad v) hvx hvy hxrank hyrank

/-- All radius-three forest-certificate fields except the finite cycle-peak
selection are now derived from connectedness and girth. -/
noncomputable def radiusThreeForestCertificate_of_cyclePeak
    (G : SimpleGraph V) (hconn : G.Connected) (hgirth : 9 ≤ G.girth)
    (r : V) (hrad : RadiusThreeCenter G r)
    (hpeak : ∀ v (c : G.Walk v v), c.IsCycle →
      ∃ i x y,
        i ≠ r ∧ G.Adj i x ∧ G.Adj i y ∧ x ≠ y ∧
        G.dist r x + 1 = G.dist r i ∧
        G.dist r y + 1 = G.dist r i) :
    RadiusThreeForestCertificate G where
  root := r
  rank := G.dist r
  rootRank := by simp
  uniqueParent := radiusThree_uniqueParent G hconn hgirth r hrad
  cyclePeak := hpeak

end WrittenOnTheWallII.GraphConjecture141UniqueParent
