import GraphConjecture59OppositeColumnClosure

/-!
# WOWII 59: propagation across the nondeficient core columns

The v31 opposite-column closure determines the local profile of the unique
deficient column in the surviving `K3,3-e` branch.  This complementary rung
uses the other two columns.  It extracts the deficient column from the exact
matrix profile, forces `q` across every opposite-core column, and proves that
the two nondeficient columns jointly cover the four named frame vertices.
-/

namespace WrittenOnTheWallII.GraphConjecture59MissingColumnPropagation

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59PathAttachmentSplit
open WrittenOnTheWallII.GraphConjecture59PathFanClosure
open WrittenOnTheWallII.GraphConjecture59ThreeCoreClosure

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- At the matrix level, a unique missing edge in row `a` selects a column
where each of the other two distinct rows is present. -/
theorem deficient_row_supplies_column
    (E : Fin 3 → Fin 3 → Bool) (a b d : Fin 3)
    (hab : a ≠ b) (had : a ≠ d)
    (hmissing :
      WrittenOnTheWallII.GraphConjecture59CoreCoverSynthesis.OneMissingCoreEdgeAtRow
        E a) :
    ∃ t, E a t = false ∧ E b t = true ∧ E d t = true := by
  obtain ⟨t, hat, hunique⟩ := hmissing
  refine ⟨t, hat, ?_, ?_⟩
  · apply Bool.of_not_eq_false
    intro hbt
    exact hab (hunique b t hbt).1.symm
  · apply Bool.of_not_eq_false
    intro hdt
    exact had (hunique d t hdt).1.symm

omit [Fintype V] in
/-- If `q` misses any opposite-core vertex `t`, the independent aligned core
triple together with `t,q` is a forest.  Unlike the v31 deficient-column
lemma, all incidences from `t` to the triple are unrestricted, so this applies
to every column. -/
theorem arbitrary_column_without_q_isAcyclic
    (G : SimpleGraph V) (a b d t q : V)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b) (hqt : ¬G.Adj q t) :
    (G.induce (({a, b, d, t, q} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({a, b, d} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({a, b, d} : Finset V) at hr
    change s ∈ ({a, b, d} : Finset V) at hs
    simp only [mem_insert, mem_singleton] at hr hs
    rcases hr with rfl | rfl | rfl <;> rcases hs with rfl | rfl | rfl <;>
      simp_all [G.adj_comm]
  have ht :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({a, b, d} : Finset V) t hI
  have ht' :
      (G.induce (insert t ((({a, b, d} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert t ((({a, b, d} : Finset V) : Set V)) =
          (({t, a, b, d} : Finset V) : Set V) := by
      ext r
      simp [or_left_comm]
    rw [hset]
    exact ht
  have hq := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert t ((({a, b, d} : Finset V) : Set V))) q ht' (by
      intro x hx y hy hqx hqy
      by_contra hxy
      change x = t ∨ x ∈ ({a, b, d} : Finset V) at hx
      change y = t ∨ y ∈ ({a, b, d} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, b, d, t, q} : Finset V) : Set V) =
        insert q (insert t ((({a, b, d} : Finset V) : Set V))) := by
    ext r
    simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff]
    aesop
  rw [hset]
  exact hq

/-- Hence `f(G)=4` makes `q` complete to the whole opposite core, not only
to the deficient column handled in v31. -/
theorem saturated_core_forces_q_column
    (G : SimpleGraph V) (a b d t q : V)
    (hdist : PairwiseDistinctPathExtensions a b d t q)
    (hab : ¬G.Adj a b) (had : ¬G.Adj a d) (hbd : ¬G.Adj b d)
    (hqa : ¬G.Adj q a) (hqb : ¬G.Adj q b)
    (hf : G.largestInducedForestSize = 4) : G.Adj q t := by
  by_contra hqt
  have hacyc := arbitrary_column_without_q_isAcyclic
    G a b d t q hab had hbd hqa hqb hqt
  have hcard : ({a, b, d, t, q} : Finset V).card = 5 := by
    rcases hdist with ⟨habV, hadV, hatV, haqV, hbdV,
      hbtV, hbqV, hdtV, hdqV, htqV⟩
    simp [habV, hadV, hatV, haqV, hbdV, hbtV, hbqV, hdtV, hdqV, htqV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, b, d, t, q} : Finset V) hacyc
  rw [hcard, hf] at hbound
  omega

omit [Fintype V] in
/-- If a frame vertex `z` misses both nondeficient columns `r,s`, then
`{a,r,s,t,z}` is a forest.  The possible edge `t-z` is unrestricted. -/
theorem complete_columns_uncovered_frame_isAcyclic
    (G : SimpleGraph V) (a r s t z : V)
    (hrs : ¬G.Adj r s) (hrt : ¬G.Adj r t) (hst : ¬G.Adj s t)
    (hat : ¬G.Adj a t) (hzr : ¬G.Adj z r) (hzs : ¬G.Adj z s) :
    (G.induce (({a, r, s, t, z} : Finset V) : Set V)).IsAcyclic := by
  have hI : G.IsIndepSet (({r, s} : Finset V) : Set V) := by
    intro x hx y hy hxy hadj
    change x ∈ ({r, s} : Finset V) at hx
    change y ∈ ({r, s} : Finset V) at hy
    simp only [mem_insert, mem_singleton] at hx hy
    rcases hx with rfl | rfl <;> rcases hy with rfl | rfl <;>
      simp_all [G.adj_comm]
  have ha :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({r, s} : Finset V) a hI
  have ha' :
      (G.induce (insert a ((({r, s} : Finset V) : Set V)))).IsAcyclic := by
    have hset :
        insert a ((({r, s} : Finset V) : Set V)) =
          (({a, r, s} : Finset V) : Set V) := by
      ext x
      simp
    rw [hset]
    exact ha
  have haz := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert a ((({r, s} : Finset V) : Set V))) z ha' (by
      intro x hx y hy hzx hzy
      by_contra hxy
      change x = a ∨ x ∈ ({r, s} : Finset V) at hx
      change y = a ∨ y ∈ ({r, s} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hazt := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert z (insert a ((({r, s} : Finset V) : Set V)))) t haz (by
      intro x hx y hy htx hty
      by_contra hxy
      change x = z ∨ x = a ∨ x ∈ ({r, s} : Finset V) at hx
      change y = z ∨ y = a ∨ y ∈ ({r, s} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, r, s, t, z} : Finset V) : Set V) =
        insert t (insert z (insert a ((({r, s} : Finset V) : Set V)))) := by
    ext x
    simp only [Finset.coe_insert, Finset.coe_singleton, Set.mem_insert_iff,
      Set.mem_singleton_iff]
    aesop
  rw [hset]
  exact hazt

/-- The two nondeficient columns therefore jointly cover every named frame
vertex. -/
theorem complete_columns_force_frame_cover
    (G : SimpleGraph V) (a r s t z : V)
    (hdist : PairwiseDistinctPathExtensions a r s t z)
    (hrs : ¬G.Adj r s) (hrt : ¬G.Adj r t) (hst : ¬G.Adj s t)
    (hat : ¬G.Adj a t) (hf : G.largestInducedForestSize = 4) :
    G.Adj r z ∨ G.Adj s z := by
  by_contra hcover
  push_neg at hcover
  have hacyc := complete_columns_uncovered_frame_isAcyclic
    G a r s t z hrs hrt hst hat
      (by simpa [G.adj_comm] using hcover.1)
      (by simpa [G.adj_comm] using hcover.2)
  have hcard : ({a, r, s, t, z} : Finset V).card = 5 := by
    rcases hdist with ⟨harV, hasV, hatV, hazV, hrsV,
      hrtV, hrzV, hstV, hszV, htzV⟩
    simp [harV, hasV, hatV, hazV, hrsV, hrtV, hrzV, hstV, hszV, htzV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, r, s, t, z} : Finset V) hacyc
  rw [hcard, hf] at hbound
  omega

/-- A vertex meets at least two members of a four-vertex frame. -/
def HitsTwoFrame (G : SimpleGraph V) (x u c v p : V) : Prop :=
  (G.Adj x u ∧ G.Adj x c) ∨ (G.Adj x u ∧ G.Adj x v) ∨
  (G.Adj x u ∧ G.Adj x p) ∨ (G.Adj x c ∧ G.Adj x v) ∨
  (G.Adj x c ∧ G.Adj x p) ∨ (G.Adj x v ∧ G.Adj x p)

omit [Fintype V] [DecidableEq V] in
/-- Four pointwise covers by two columns force one column to hit at least
two of the frame vertices. -/
theorem one_column_hits_two_frame
    (G : SimpleGraph V) (r s u c v p : V)
    (hu : G.Adj r u ∨ G.Adj s u) (hc : G.Adj r c ∨ G.Adj s c)
    (hv : G.Adj r v ∨ G.Adj s v) (hp : G.Adj r p ∨ G.Adj s p) :
    HitsTwoFrame G r u c v p ∨ HitsTwoFrame G s u c v p := by
  simp only [HitsTwoFrame]
  tauto

/-- Six named distinct neighbors certify degree at least six. -/
theorem six_le_degree_of_six_neighbors
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (x a b c d e f : V) (hnodup : [a, b, c, d, e, f].Nodup)
    (ha : G.Adj x a) (hb : G.Adj x b) (hc : G.Adj x c)
    (hd : G.Adj x d) (he : G.Adj x e) (hf : G.Adj x f) :
    6 ≤ G.degree x := by
  let N : Finset V := [a, b, c, d, e, f].toFinset
  have hNcard : N.card = 6 := by
    simpa [N] using List.toFinset_card_of_nodup hnodup
  have hsub : N ⊆ G.neighborFinset x := by
    intro y hy
    simp only [N, List.mem_toFinset, List.mem_cons, List.not_mem_nil, or_false] at hy
    rcases hy with rfl | rfl | rfl | rfl | rfl | rfl <;>
      simp_all [G.mem_neighborFinset]
  have hcard := card_le_card hsub
  rw [hNcard, G.card_neighborFinset_eq_degree] at hcard
  exact hcard

/-- Four base neighbors and a two-hit frame give degree at least six. -/
theorem six_le_degree_of_two_frame_hits
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (x a b d q u c v p : V)
    (hnodup : [a, b, d, q, u, c, v, p].Nodup)
    (hxa : G.Adj x a) (hxb : G.Adj x b)
    (hxd : G.Adj x d) (hxq : G.Adj x q)
    (hhits : HitsTwoFrame G x u c v p) : 6 ≤ G.degree x := by
  rcases hhits with h | h | h | h | h | h
  · exact six_le_degree_of_six_neighbors G x a b d q u c
      (List.Nodup.sublist (by simp) hnodup) hxa hxb hxd hxq h.1 h.2
  · exact six_le_degree_of_six_neighbors G x a b d q u v
      (List.Nodup.sublist (by simp) hnodup) hxa hxb hxd hxq h.1 h.2
  · exact six_le_degree_of_six_neighbors G x a b d q u p
      (List.Nodup.sublist (by simp) hnodup) hxa hxb hxd hxq h.1 h.2
  · exact six_le_degree_of_six_neighbors G x a b d q c v
      (List.Nodup.sublist (by simp) hnodup) hxa hxb hxd hxq h.1 h.2
  · exact six_le_degree_of_six_neighbors G x a b d q c p
      (List.Nodup.sublist (by simp) hnodup) hxa hxb hxd hxq h.1 h.2
  · exact six_le_degree_of_six_neighbors G x a b d q v p
      (List.Nodup.sublist (by simp) hnodup) hxa hxb hxd hxq h.1 h.2

/-- Pointwise frame coverage forces at least one nondeficient column to have
degree at least six. -/
theorem one_complete_column_has_degree_six
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (r s a b d q u c v p : V)
    (hrnodup : [a, b, d, q, u, c, v, p].Nodup)
    (hsnodup : [a, b, d, q, u, c, v, p].Nodup)
    (hra : G.Adj r a) (hrb : G.Adj r b)
    (hrd : G.Adj r d) (hrq : G.Adj r q)
    (hsa : G.Adj s a) (hsb : G.Adj s b)
    (hsd : G.Adj s d) (hsq : G.Adj s q)
    (hu : G.Adj r u ∨ G.Adj s u) (hc : G.Adj r c ∨ G.Adj s c)
    (hv : G.Adj r v ∨ G.Adj s v) (hp : G.Adj r p ∨ G.Adj s p) :
    6 ≤ G.degree r ∨ 6 ≤ G.degree s := by
  rcases one_column_hits_two_frame G r s u c v p hu hc hv hp with hr | hs
  · exact Or.inl <| six_le_degree_of_two_frame_hits
      G r a b d q u c v p hrnodup hra hrb hrd hrq hr
  · exact Or.inr <| six_le_degree_of_two_frame_hits
      G s a b d q u c v p hsnodup hsa hsb hsd hsq hs

/-- The saturated frame and all-column propagation give `degree(q) ≥ 8`. -/
theorem eight_le_degree_of_saturated_q
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (q u c v p d r s t : V)
    (hnodup : [u, c, v, p, d, r, s, t].Nodup)
    (hqu : G.Adj q u) (hqc : G.Adj q c) (hqv : G.Adj q v)
    (hqp : G.Adj q p) (hqd : G.Adj q d)
    (hqr : G.Adj q r) (hqs : G.Adj q s) (hqt : G.Adj q t) :
    8 ≤ G.degree q :=
  eight_le_degree_of_eight_neighbors
    G q u c v p d r s t hnodup hqu hqc hqv hqp hqd hqr hqs hqt

end WrittenOnTheWallII.GraphConjecture59MissingColumnPropagation
