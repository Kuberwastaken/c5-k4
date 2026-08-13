import GraphConjecture141CanonicalRootSplice

/-!
# WOWII 141: equal-layer closing-edge exclusion

This module closes the final edge-exclusion premise in the canonical root-path
cycle construction.  Equal-length geodesics to distinct endpoints cannot
contain the opposite endpoint.  If their canonical splice contained the
closing endpoint edge, simplicity would force that splice to have length one,
placing one endpoint on the opposite geodesic and giving a contradiction.
-/

namespace WrittenOnTheWallII.GraphConjecture141EqualLayerClosure

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture141RootPathSplice

universe u
variable {V : Type u} [DecidableEq V]

/-- Distinct endpoints of equal-length root geodesics do not occur on the
opposite geodesic. -/
theorem equal_geodesic_endpoints_not_mem
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hpDist : p.length = G.dist r x) (hqDist : q.length = G.dist r y)
    (hlen : p.length = q.length) (hxy : x ≠ y) :
    x ∉ q.support ∧ y ∉ p.support := by
  constructor
  · intro hxq
    have htake := length_eq_dist_of_subwalk hqDist (q.isSubwalk_takeUntil hxq)
    have htakeLen : (q.takeUntil x hxq).length = q.length := by
      rw [htake, ← hpDist, hlen]
    have hxGet := q.getVert_length_takeUntil hxq
    rw [htakeLen, q.getVert_length] at hxGet
    exact hxy hxGet.symm
  · intro hyp
    have htake := length_eq_dist_of_subwalk hpDist (p.isSubwalk_takeUntil hyp)
    have htakeLen : (p.takeUntil y hyp).length = p.length := by
      rw [htake, ← hqDist, ← hlen]
    have hyGet := p.getVert_length_takeUntil hyp
    rw [htakeLen, p.getVert_length] at hyGet
    exact hxy hyGet

omit [DecidableEq V] in
/-- If the edge joining the endpoints occurs in a simple endpoint path, that
path consists of exactly that edge. -/
theorem simple_path_length_one_of_endpoint_edge_mem
    {G : SimpleGraph V} {x y : V} (t : G.Walk x y)
    (ht : t.IsPath) (hxy : x ≠ y) (hedge : s(y, x) ∈ t.edges) :
    t.length = 1 := by
  have hedge' : s(x, y) ∈ t.edges := by
    simpa [Sym2.eq_swap] using hedge
  have hsnd : y = t.snd := ht.eq_snd_of_mem_edges hedge'
  cases t with
  | nil => exact (hxy rfl).elim
  | @cons _ z _ hadj tail =>
      have htailPath : tail.IsPath := ht.of_cons
      have hz : z = y := by simpa using hsnd.symm
      subst z
      have htailNil : tail = Walk.nil :=
        (Walk.isPath_iff_eq_nil tail).mp htailPath
      subst tail
      simp

/-- For common `w`, an internally disjoint simple splice of equal-layer
geodesics cannot contain the closing endpoint edge. -/
theorem equal_geodesic_splice_closing_edge_not_mem
    {G : SimpleGraph V} {r x y w : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hpDist : p.length = G.dist r x) (hqDist : q.length = G.dist r y)
    (hlen : p.length = q.length) (hxy : x ≠ y)
    (hwp : w ∈ p.support) (hwq : w ∈ q.support)
    (pxr : G.Walk x w) (qy : G.Walk w y)
    (hsplice : (pxr.append qy).IsPath) :
    s(y, x) ∉ (pxr.append qy).edges := by
  intro hedge
  have hone := simple_path_length_one_of_endpoint_edge_mem
    (pxr.append qy) hsplice hxy hedge
  have hsum : pxr.length + qy.length = 1 := by
    simpa using hone
  obtain hpxZero | hqyZero : pxr.length = 0 ∨ qy.length = 0 := by omega
  · have hxw : x = w := Walk.eq_of_length_eq_zero hpxZero
    have hnot := (equal_geodesic_endpoints_not_mem p q hpDist hqDist hlen hxy).1
    exact hnot (hxw ▸ hwq)
  · have hwy : w = y := Walk.eq_of_length_eq_zero hqyZero
    have hnot := (equal_geodesic_endpoints_not_mem p q hpDist hqDist hlen hxy).2
    exact hnot (hwy ▸ hwp)

/-- Membership-enriched canonical splice.  The v0.25 constructor already
proved all path and length fields; this variant retains the two common-support
facts needed by the metric closing-edge argument. -/
theorem exists_canonical_root_path_splice_with_common
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hp : p.IsPath) (hq : q.IsPath) :
    ∃ (w : V) (pxr : G.Walk x w) (qy : G.Walk w y),
      w ∈ p.support ∧ w ∈ q.support ∧
      pxr.IsPath ∧ qy.IsPath ∧
      pxr.support.Disjoint qy.support.tail ∧
      (pxr.append qy).IsPath ∧
      (pxr.append qy).length ≤ p.length + q.length := by
  let s : Finset V := q.support.toFinset
  have hcommon : {z ∈ s | z ∈ p.reverse.support}.Nonempty := by
    refine ⟨r, ?_⟩
    simp only [Finset.mem_filter, s, List.mem_toFinset]
    constructor
    · exact q.start_mem_support
    · rw [Walk.support_reverse, List.mem_reverse]
      exact p.start_mem_support
  obtain ⟨w, hwqFin, hwpr, hfirst⟩ :=
    p.reverse.exists_mem_support_forall_mem_support_imp_eq s hcommon
  have hwp : w ∈ p.support := by
    rw [Walk.support_reverse, List.mem_reverse] at hwpr
    exact hwpr
  have hwq : w ∈ q.support := by
    simpa [s] using hwqFin
  let pxr := p.reverse.takeUntil w hwpr
  let qy := q.dropUntil w hwq
  have hpxr : pxr.IsPath := hp.reverse.takeUntil hwpr
  have hqy : qy.IsPath := hq.dropUntil hwq
  have hwNotQTail : w ∉ qy.support.tail := by
    have hn := hqy.support_nodup
    have hs : qy.support = w :: qy.support.tail := by
      exact (List.cons_head_tail qy.support_ne_nil).symm.trans (by simp)
    rw [hs, List.nodup_cons] at hn
    exact hn.1
  have hdisj : pxr.support.Disjoint qy.support.tail := by
    rw [List.disjoint_left]
    intro z hzP hzQ
    have hzQ' : z ∈ q.support :=
      q.support_dropUntil_subset hwq (List.mem_of_mem_tail hzQ)
    have hzQFin : z ∈ s := by
      simpa [s] using hzQ'
    have hzw : z = w := hfirst z hzQFin hzP
    subst z
    exact hwNotQTail hzQ
  have hsplice : (pxr.append qy).IsPath := by
    rw [Walk.isPath_def, Walk.support_append]
    exact hpxr.support_nodup.append hqy.support_nodup.tail hdisj
  have hpxrLen : pxr.length ≤ p.length := by
    calc
      pxr.length ≤ p.reverse.length := p.reverse.length_takeUntil_le hwpr
      _ = p.length := by simp
  have hqyLen : qy.length ≤ q.length := q.length_dropUntil_le hwq
  refine ⟨w, pxr, qy, hwp, hwq, hpxr, hqy, hdisj, hsplice, ?_⟩
  simp only [Walk.length_append]
  omega

omit [DecidableEq V] in
/-- Equal-length geodesics to distinct adjacent endpoints canonically close to
a simple cycle.  No last-common witness and no closing-edge exclusion premise
is supplied by the caller. -/
theorem bounded_cycle_of_equal_geodesic_endpoint_edge
    [DecidableEq V]
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hpDist : p.length = G.dist r x) (hqDist : q.length = G.dist r y)
    (hlen : p.length = q.length) (hxy : x ≠ y) (hadj : G.Adj y x) :
    ∃ c : G.Walk y y,
      c.IsCycle ∧ c.length ≤ p.length + q.length + 1 := by
  have hp : p.IsPath := p.isPath_of_length_eq_dist hpDist
  have hq : q.IsPath := q.isPath_of_length_eq_dist hqDist
  obtain ⟨w, pxr, qy, hwp, hwq, _hpxr, _hqy, _hdisj, hsplice,
      hbound⟩ := exists_canonical_root_path_splice_with_common p q hp hq
  have hedge : s(y, x) ∉ (pxr.append qy).edges :=
    equal_geodesic_splice_closing_edge_not_mem p q hpDist hqDist hlen hxy
      hwp hwq pxr qy hsplice
  obtain ⟨c, hc, hclen⟩ := close_spliced_path_with_edge
    (pxr.append qy) hsplice hadj hedge
  exact ⟨c, hc, by omega⟩

omit [DecidableEq V] in
/-- Radius-three numerical specialization: adjacent distinct vertices in the
same layer, witnessed by root geodesics of length at most three, lie on a
simple cycle of length at most seven. -/
theorem cycle_length_le_seven_of_equal_layer_three
    [DecidableEq V]
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hpDist : p.length = G.dist r x) (hqDist : q.length = G.dist r y)
    (hlen : p.length = q.length) (hpThree : p.length ≤ 3)
    (hxy : x ≠ y) (hadj : G.Adj y x) :
    ∃ c : G.Walk y y, c.IsCycle ∧ c.length ≤ 7 := by
  obtain ⟨c, hc, hbound⟩ := bounded_cycle_of_equal_geodesic_endpoint_edge
    p q hpDist hqDist hlen hxy hadj
  exact ⟨c, hc, by omega⟩

end WrittenOnTheWallII.GraphConjecture141EqualLayerClosure
