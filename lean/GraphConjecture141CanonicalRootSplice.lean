import GraphConjecture141RootPathSplice

/-!
# WOWII 141: canonical last-common root-path splice

This module removes the supplied last-common-vertex premise from the v0.24
splice.  It applies mathlib's finite first-hit lemma to the reverse of one
simple root path and the support finset of the other.  The first common vertex
seen from the endpoint is the canonical last common vertex, and its two
outgoing path pieces splice without any additional certificate.
-/

namespace WrittenOnTheWallII.GraphConjecture141CanonicalRootSplice

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture141RootPathSplice

universe u
variable {V : Type u} [DecidableEq V]

/-- Two finite simple paths from the same root have a canonically selected
last common vertex.  Taking the prefix of the reversed first path and the
suffix of the second produces an internally disjoint simple endpoint path.
-/
theorem exists_canonical_root_path_splice
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hp : p.IsPath) (hq : q.IsPath) :
    ∃ (w : V) (pxr : G.Walk x w) (qy : G.Walk w y),
      pxr.IsPath ∧ qy.IsPath ∧
      pxr.support.Disjoint qy.support.tail ∧
      (pxr.append qy).IsPath ∧
      (pxr.append qy).length = pxr.length + qy.length ∧
      pxr.length ≤ p.length ∧ qy.length ≤ q.length ∧
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
  have hlen : (pxr.append qy).length = pxr.length + qy.length := by
    simp
  have hpxrLen : pxr.length ≤ p.length := by
    calc
      pxr.length ≤ p.reverse.length := p.reverse.length_takeUntil_le hwpr
      _ = p.length := by simp
  have hqyLen : qy.length ≤ q.length := q.length_dropUntil_le hwq
  refine ⟨w, pxr, qy, hpxr, hqy, hdisj, hsplice, hlen, hpxrLen,
    hqyLen, ?_⟩
  rw [hlen]
  omega

omit [DecidableEq V] in
/-- Canonical bounded-cycle interface.  Compared with v0.24, callers no
longer supply a last-common vertex or prove its suffix-intersection property;
only exclusion of the closing edge from the selected splice remains. -/
theorem bounded_cycle_of_root_paths_and_endpoint_edge
    [DecidableEq V]
    {G : SimpleGraph V} {r x y : V}
    (p : G.Walk r x) (q : G.Walk r y)
    (hp : p.IsPath) (hq : q.IsPath) (hxy : G.Adj y x)
    (hedge : ∀ (w : V) (pxr : G.Walk x w) (qy : G.Walk w y),
      pxr.IsPath → qy.IsPath →
      pxr.support.Disjoint qy.support.tail →
      s(y, x) ∉ (pxr.append qy).edges) :
    ∃ c : G.Walk y y,
      c.IsCycle ∧ c.length ≤ p.length + q.length + 1 := by
  obtain ⟨w, pxr, qy, hpxr, hqy, hdisj, hs, _hlen, _hpxrLen,
      _hqyLen, hbound⟩ := exists_canonical_root_path_splice p q hp hq
  obtain ⟨c, hc, hclen⟩ := close_spliced_path_with_edge
    (pxr.append qy) hs hxy (hedge w pxr qy hpxr hqy hdisj)
  exact ⟨c, hc, by omega⟩

end WrittenOnTheWallII.GraphConjecture141CanonicalRootSplice
