import GraphConjecture59FullFanPropagation
import GraphConjecture59RelabeledCoreProfile

/-!
# WOWII 59: composition with the exact three-by-three core

The end-to-end core profile supplies a genuine third vertex on the aligned
core side.  That vertex immediately closes every path attachment in which
`q` misses one path vertex.  The only surviving local configuration is the
all-three/full-fan rectangle; global `f(G)=4` then forces the third core
vertex to copy all five outside adjacencies and all three opposite-core
adjacencies.
-/

namespace WrittenOnTheWallII.GraphConjecture59ThreeCoreClosure

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility
open WrittenOnTheWallII.GraphConjecture59PathFanClosure
open WrittenOnTheWallII.GraphConjecture59PathAttachmentSplit
open WrittenOnTheWallII.GraphConjecture59FullFanPropagation
open WrittenOnTheWallII.GraphConjecture59CyclicCardRectangle
open WrittenOnTheWallII.GraphConjecture59RelabeledCoreProfile

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- Three independent core-side vertices, one arbitrary common attachment,
and a vertex avoiding the first two cores and that attachment induce a
forest.  Its edge to the third core is unrestricted. -/
theorem three_core_missed_vertex_isAcyclic
    (G : SimpleGraph V) (a b d w q : V)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b) (hqw : ¬G.Adj q w) :
    (G.induce (({a, b, d, w, q} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({a, b, d} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({a, b, d} : Finset V) at hr
    change s ∈ ({a, b, d} : Finset V) at hs
    simp only [mem_insert, mem_singleton] at hr hs
    rcases hr with rfl | rfl | rfl <;> rcases hs with rfl | rfl | rfl <;>
      simp_all [G.adj_comm]
  have hstar :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({a, b, d} : Finset V) w hI
  have hstar' :
      (G.induce (insert w ((({a, b, d} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert w ((({a, b, d} : Finset V) : Set V)) =
          (({w, a, b, d} : Finset V) : Set V) := by
      ext r
      simp [or_left_comm]
    rw [hset]
    exact hstar
  have hplus := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert w ((({a, b, d} : Finset V) : Set V))) q hstar' (by
      intro x hx y hy hqx hqy
      by_contra hxy
      change x = w ∨ x ∈ ({a, b, d} : Finset V) at hx
      change y = w ∨ y ∈ ({a, b, d} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, b, d, w, q} : Finset V) : Set V) =
        insert q (insert w ((({a, b, d} : Finset V) : Set V))) := by
    ext r
    simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff]
    aesop
  rw [hset]
  exact hplus

/-- The missed-vertex witness yields an induced forest of order five. -/
theorem five_le_f_of_three_core_missed_vertex
    (G : SimpleGraph V) (a b d w q : V)
    (hdist : PairwiseDistinctPathExtensions a b d w q)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b) (hqw : ¬G.Adj q w) :
    5 ≤ G.largestInducedForestSize := by
  have hacyc := three_core_missed_vertex_isAcyclic
    G a b d w q hab had hbd hqa hqb hqw
  have hcard : ({a, b, d, w, q} : Finset V).card = 5 := by
    rcases hdist with ⟨habV, hadV, hawV, haqV, hbdV,
      hbwV, hbqV, hdwV, hdqV, hwqV⟩
    simp [habV, hadV, hawV, haqV, hbdV, hbwV, hbqV, hdwV, hdqV, hwqV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, b, d, w, q} : Finset V) hacyc
  simpa [hcard] using hbound

omit [Fintype V] in
/-- A three-set containing distinct `a,b` has a third member. -/
lemma exists_third_of_card_eq_three
    (A : Finset V) (hcard : A.card = 3)
    {a b : V} (hab : a ≠ b) :
    ∃ d ∈ A, d ≠ a ∧ d ≠ b := by
  by_contra hnone
  have hsub : A ⊆ {a, b} := by
    intro d hd
    by_cases hda : d = a
    · simp [hda]
    · have hdb : d = b := by
        by_contra hdb
        exact hnone ⟨d, hd, hda, hdb⟩
      simp [hdb]
  have hle := card_le_card hsub
  have hp : ({a, b} : Finset V).card = 2 := by simp [hab]
  omega

/-- **Composition with the end-to-end profile.** Any attachment missed by
`q` contradicts `f(G)=4`, because the exact `3+3` relabeling supplies a third
same-color core vertex for the preceding five-forest. -/
theorem missed_attachment_impossible_in_exact_three_core
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (c : V → Fin 2) (a b w q : V)
    (hc : ∀ u ∈ S, ∀ v ∈ S, G.Adj u v → c u ≠ c v)
    (hSbip : (G.induce (S : Set V)).IsBipartite)
    (hSsix : S.card = 6) (hf : G.largestInducedForestSize = 4)
    (hclass : ∀ k : Fin 2, (S.filter fun v ↦ c v = k).card = 3)
    (haS : a ∈ S) (hbS : b ∈ S) (hca : c a = 0) (hcb : c b = 0)
    (hwout : w ∉ S) (hqout : q ∉ S)
    (hdist : PairwiseDistinctFour a b w q)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b) (hqw : ¬G.Adj q w) : False := by
  obtain ⟨A, B, eA, eB, hA, hB, hprofile⟩ :=
    exists_relabeling_with_exact_core_profile
      G S c hc hSbip hSsix hf hclass
  have hAcard : A.card = 3 := by
    rw [← Fintype.card_coe]
    simpa using Fintype.card_congr eA.symm
  have haA : a ∈ A := by rw [hA]; simp [haS, hca]
  have hbA : b ∈ A := by rw [hA]; simp [hbS, hcb]
  obtain ⟨d, hdA, hda, hdb⟩ :=
    exists_third_of_card_eq_three A hAcard hdist.1
  have hdData : d ∈ S ∧ c d = 0 := by
    rw [hA] at hdA
    simpa using (mem_filter.mp hdA)
  have hab : ¬G.Adj a b := by
    intro hadj
    exact (hc a haS b hbS hadj) (hca.trans hcb.symm)
  have had : ¬G.Adj a d := by
    intro hadj
    exact (hc a haS d hdData.1 hadj) (hca.trans hdData.2.symm)
  have hbd : ¬G.Adj b d := by
    intro hadj
    exact (hc b hbS d hdData.1 hadj) (hcb.trans hdData.2.symm)
  have hdw : d ≠ w := by
    intro h
    apply hwout
    rw [← h]
    exact hdData.1
  have hdq : d ≠ q := by
    intro h
    apply hqout
    rw [← h]
    exact hdData.1
  have hdistFive : PairwiseDistinctPathExtensions a b d w q :=
    ⟨hdist.1, hda.symm, hdist.2.1, hdist.2.2.1,
      hdb.symm, hdist.2.2.2.1, hdist.2.2.2.2.1,
      hdw, hdq, hdist.2.2.2.2.2⟩
  have hfive := five_le_f_of_three_core_missed_vertex
    G a b d w q hdistFive hab had hbd hqa hqb hqw
  omega

omit [Fintype V] in
/-- In the all-three case, if either `d-q` or `d-w` is missing then the same
three-core set is a five-forest. -/
theorem allhit_three_core_isAcyclic_of_missing_edge
    (G : SimpleGraph V) (a b d w q : V)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b)
    (hmiss : ¬(G.Adj q d ∧ G.Adj q w)) :
    (G.induce (({a, b, d, w, q} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({a, b, d} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({a, b, d} : Finset V) at hr
    change s ∈ ({a, b, d} : Finset V) at hs
    simp only [mem_insert, mem_singleton] at hr hs
    rcases hr with rfl | rfl | rfl <;> rcases hs with rfl | rfl | rfl <;>
      simp_all [G.adj_comm]
  have hstar :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({a, b, d} : Finset V) w hI
  have hstar' :
      (G.induce (insert w ((({a, b, d} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert w ((({a, b, d} : Finset V) : Set V)) =
          (({w, a, b, d} : Finset V) : Set V) := by
      ext r
      simp [or_left_comm]
    rw [hset]
    exact hstar
  have hplus := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert w ((({a, b, d} : Finset V) : Set V))) q hstar' (by
      intro x hx y hy hqx hqy
      by_contra hxy
      change x = w ∨ x ∈ ({a, b, d} : Finset V) at hx
      change y = w ∨ y ∈ ({a, b, d} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, b, d, w, q} : Finset V) : Set V) =
        insert q (insert w ((({a, b, d} : Finset V) : Set V))) := by
    ext r
    simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff]
    aesop
  rw [hset]
  exact hplus

/-- Global `f=4` forces both `d-q` and `d-w` in the saturated all-three
configuration. -/
theorem allhit_three_core_forces_edges
    (G : SimpleGraph V) (a b d w q : V)
    (hdist : PairwiseDistinctPathExtensions a b d w q)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b)
    (hf : G.largestInducedForestSize = 4) :
    G.Adj q d ∧ G.Adj q w := by
  by_contra hmiss
  have hacyc := allhit_three_core_isAcyclic_of_missing_edge
    G a b d w q hab had hbd hqa hqb hmiss
  have hcard : ({a, b, d, w, q} : Finset V).card = 5 := by
    rcases hdist with ⟨habV, hadV, hawV, haqV, hbdV,
      hbwV, hbqV, hdwV, hdqV, hwqV⟩
    simp [habV, hadV, hawV, haqV, hbdV, hbwV, hbqV, hdwV, hdqV, hwqV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, b, d, w, q} : Finset V) hacyc
  rw [hcard, hf] at hbound
  omega

omit [Fintype V] in
/-- Once `d-q` is forced, missing `p-d` makes `{a,b,d,p,q}` a five-forest. -/
theorem saturated_fan_isAcyclic_of_missing_pd
    (G : SimpleGraph V) (a b d p q : V)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b) (hpd : ¬G.Adj p d) :
    (G.induce (({a, b, d, p, q} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({a, b} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({a, b} : Finset V) at hr
    change s ∈ ({a, b} : Finset V) at hs
    simp only [mem_insert, mem_singleton] at hr hs
    rcases hr with rfl | rfl <;> rcases hs with rfl | rfl <;>
      simp_all [G.adj_comm]
  have hp :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({a, b} : Finset V) p hI
  have hp' :
      (G.induce (insert p ((({a, b} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert p ((({a, b} : Finset V) : Set V)) =
          (({p, a, b} : Finset V) : Set V) := by ext r; simp [or_left_comm]
    rw [hset]
    exact hp
  have hpq := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert p ((({a, b} : Finset V) : Set V))) q hp' (by
      intro x hx y hy hqx hqy
      by_contra hxy
      change x = p ∨ x ∈ ({a, b} : Finset V) at hx
      change y = p ∨ y ∈ ({a, b} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl <;> rcases hy with rfl | rfl | rfl <;>
        simp_all [G.adj_comm])
  have hpqd := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert q (insert p ((({a, b} : Finset V) : Set V)))) d hpq (by
      intro x hx y hy hdx hdy
      by_contra hxy
      change x = q ∨ x = p ∨ x ∈ ({a, b} : Finset V) at hx
      change y = q ∨ y = p ∨ y ∈ ({a, b} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, b, d, p, q} : Finset V) : Set V) =
        insert d (insert q (insert p ((({a, b} : Finset V) : Set V)))) := by
    ext r
    simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff]
    aesop
  rw [hset]
  exact hpqd

/-- Hence the saturated all-three/full-fan case forces `p-d`. -/
theorem saturated_fan_forces_pd
    (G : SimpleGraph V) (a b d p q : V)
    (hdist : PairwiseDistinctPathExtensions a b d p q)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b)
    (hf : G.largestInducedForestSize = 4) : G.Adj p d := by
  by_contra hpd
  have hacyc := saturated_fan_isAcyclic_of_missing_pd
    G a b d p q hab had hbd hqa hqb hpd
  have hcard : ({a, b, d, p, q} : Finset V).card = 5 := by
    rcases hdist with ⟨habV, hadV, hapV, haqV, hbdV,
      hbpV, hbqV, hdpV, hdqV, hpqV⟩
    simp [habV, hadV, hapV, haqV, hbdV, hbpV, hbqV, hdpV, hdqV, hpqV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, b, d, p, q} : Finset V) hacyc
  rw [hcard, hf] at hbound
  omega

omit [Fintype V] in
/-- If an opposite-core vertex `t` misses `d`, then `{a,b,d,t,q}` is a
five-forest even with arbitrary `t`-attachments to `a,b,q`. -/
theorem opposite_core_missing_d_isAcyclic
    (G : SimpleGraph V) (a b d t q : V)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b) (hdt : ¬G.Adj d t) :
    (G.induce (({a, b, d, t, q} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({a, b, q} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({a, b, q} : Finset V) at hr
    change s ∈ ({a, b, q} : Finset V) at hs
    simp only [mem_insert, mem_singleton] at hr hs
    rcases hr with rfl | rfl | rfl <;> rcases hs with rfl | rfl | rfl <;>
      simp_all [G.adj_comm]
  have ht :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({a, b, q} : Finset V) t hI
  have ht' :
      (G.induce (insert t ((({a, b, q} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert t ((({a, b, q} : Finset V) : Set V)) =
          (({t, a, b, q} : Finset V) : Set V) := by ext r; simp [or_left_comm]
    rw [hset]
    exact ht
  have htd := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert t ((({a, b, q} : Finset V) : Set V))) d ht' (by
      intro x hx y hy hdx hdy
      by_contra hxy
      change x = t ∨ x ∈ ({a, b, q} : Finset V) at hx
      change y = t ∨ y ∈ ({a, b, q} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, b, d, t, q} : Finset V) : Set V) =
        insert d (insert t ((({a, b, q} : Finset V) : Set V))) := by
    ext r
    simp [or_left_comm]
  rw [hset]
  exact htd

/-- Once `d-q` is forced, `f=4` makes `d` complete to the opposite core
side. -/
theorem saturated_third_core_forces_internal_edge
    (G : SimpleGraph V) (a b d t q : V)
    (hdist : PairwiseDistinctPathExtensions a b d t q)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b)
    (hf : G.largestInducedForestSize = 4) : G.Adj d t := by
  by_contra hdt
  have hacyc := opposite_core_missing_d_isAcyclic
    G a b d t q hab had hbd hqa hqb hdt
  have hcard : ({a, b, d, t, q} : Finset V).card = 5 := by
    rcases hdist with ⟨habV, hadV, hatV, haqV, hbdV,
      hbtV, hbqV, hdtV, hdqV, htqV⟩
    simp [habV, hadV, hatV, haqV, hbdV, hbtV, hbqV, hdtV, hdqV, htqV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, b, d, t, q} : Finset V) hacyc
  rw [hcard, hf] at hbound
  omega

/-- Eight explicit distinct neighbors give the saturated third core vertex
degree at least eight. -/
theorem eight_le_degree_of_eight_neighbors
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (d u c v p q r s t : V)
    (hnodup : [u, c, v, p, q, r, s, t].Nodup)
    (hu : G.Adj d u) (hc : G.Adj d c) (hv : G.Adj d v)
    (hp : G.Adj d p) (hq : G.Adj d q)
    (hr : G.Adj d r) (hs : G.Adj d s) (ht : G.Adj d t) :
    8 ≤ G.degree d := by
  let N : Finset V := [u, c, v, p, q, r, s, t].toFinset
  have hNcard : N.card = 8 := by
    simpa [N] using List.toFinset_card_of_nodup hnodup
  have hsub : N ⊆ G.neighborFinset d := by
    intro x hx
    simp only [N, List.mem_toFinset, List.mem_cons, List.not_mem_nil, or_false] at hx
    rcases hx with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;>
      simp_all [G.mem_neighborFinset]
  have hcard := card_le_card hsub
  rw [hNcard, G.card_neighborFinset_eq_degree] at hcard
  exact hcard

end WrittenOnTheWallII.GraphConjecture59ThreeCoreClosure
