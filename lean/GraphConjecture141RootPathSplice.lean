import GraphConjecture141CyclePathIntersection

/-!
# WOWII 141: last-common-root-path splice

This file packages the root-path half of the radius-three girth argument.  A
last common vertex is supplied by its exact suffix-intersection property; the
resulting suffixes are proved internally disjoint and splice to a simple path.
-/

namespace WrittenOnTheWallII.GraphConjecture141RootPathSplice

open SimpleGraph

universe u
variable {V : Type u} [DecidableEq V]

/-- `w` is a last common vertex of two root paths when it lies on both and the
two suffixes beginning at `w` share no other vertex. -/
def IsLastCommonVertex
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y) (w : V) : Prop :=
  ∃ (hpw : w ∈ p.support) (hqw : w ∈ q.support),
    ∀ z, z ∈ (p.dropUntil w hpw).support →
      z ∈ (q.dropUntil w hqw).support → z = w

/-- Supplying a last common vertex splits two simple root paths into suffixes
whose interiors are disjoint.  Reversing the first suffix and appending the
second therefore gives a simple path between the original endpoints.

The length bounds are kept explicitly for the eventual girth estimate.
-/
theorem splice_at_last_common_vertex
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hp : p.IsPath) (hq : q.IsPath) (w : V)
    (hw : IsLastCommonVertex p q w) :
    ∃ (px : G.Walk w x) (qy : G.Walk w y),
      px.IsPath ∧ qy.IsPath ∧
      px.reverse.support.Disjoint qy.support.tail ∧
      (px.reverse.append qy).IsPath ∧
      (px.reverse.append qy).length = px.length + qy.length ∧
      px.length ≤ p.length ∧ qy.length ≤ q.length ∧
      (px.reverse.append qy).length ≤ p.length + q.length := by
  obtain ⟨hpw, hqw, hlast⟩ := hw
  let px := p.dropUntil w hpw
  let qy := q.dropUntil w hqw
  have hpx : px.IsPath := hp.dropUntil hpw
  have hqy : qy.IsPath := hq.dropUntil hqw
  have hwNotQTail : w ∉ qy.support.tail := by
    have hn := hqy.support_nodup
    have hs : qy.support = w :: qy.support.tail := by
      exact (List.cons_head_tail qy.support_ne_nil).symm.trans (by simp)
    rw [hs, List.nodup_cons] at hn
    exact hn.1
  have hdisj : px.reverse.support.Disjoint qy.support.tail := by
    rw [List.disjoint_left]
    intro z hzP hzQ
    have hzP' : z ∈ px.support := by simpa using hzP
    have hzQ' : z ∈ qy.support := List.mem_of_mem_tail hzQ
    have hzw : z = w := hlast z hzP' hzQ'
    subst z
    exact hwNotQTail hzQ
  have hsplice : (px.reverse.append qy).IsPath := by
    rw [Walk.isPath_def, Walk.support_append]
    exact hpx.reverse.support_nodup.append hqy.support_nodup.tail hdisj
  have hlen : (px.reverse.append qy).length = px.length + qy.length := by
    simp
  have hpxLen : px.length ≤ p.length := p.length_dropUntil_le hpw
  have hqyLen : qy.length ≤ q.length := q.length_dropUntil_le hqw
  refine ⟨px, qy, hpx, hqy, hdisj, hsplice, hlen, hpxLen, hqyLen, ?_⟩
  rw [hlen]
  omega

omit [DecidableEq V] in
/-- Closing a spliced simple path by an endpoint edge gives a simple cycle
once the closing edge is known not to occur in the path. -/
theorem close_spliced_path_with_edge
    {G : SimpleGraph V} {x y : V} (t : G.Walk x y)
    (ht : t.IsPath) (hxy : G.Adj y x)
    (hedge : s(y, x) ∉ t.edges) :
    ∃ c : G.Walk y y, c.IsCycle ∧ c.length = t.length + 1 := by
  let c := Walk.cons hxy t
  have hc : c.IsCycle := (Walk.cons_isCycle_iff t hxy).2 ⟨ht, hedge⟩
  exact ⟨c, hc, by simp [c]⟩

/-- Complete bounded splice interface: two root paths with a supplied last
common vertex and an endpoint edge yield a simple cycle no longer than the two
original paths plus that edge. -/
theorem bounded_cycle_of_last_common_and_endpoint_edge
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hp : p.IsPath) (hq : q.IsPath) (w : V)
    (hw : IsLastCommonVertex p q w) (hxy : G.Adj y x)
    (hedge : ∀ (px : G.Walk w x) (qy : G.Walk w y),
      px.IsPath → qy.IsPath →
      s(y, x) ∉ (px.reverse.append qy).edges) :
    ∃ c : G.Walk y y,
      c.IsCycle ∧ c.length ≤ p.length + q.length + 1 := by
  obtain ⟨px, qy, hpx, hqy, _hdisj, hs, _hlen, _hpxLen, _hqyLen, hbound⟩ :=
    splice_at_last_common_vertex p q hp hq w hw
  obtain ⟨c, hc, hclen⟩ := close_spliced_path_with_edge
    (px.reverse.append qy) hs hxy (hedge px qy hpx hqy)
  exact ⟨c, hc, by omega⟩

end WrittenOnTheWallII.GraphConjecture141RootPathSplice
