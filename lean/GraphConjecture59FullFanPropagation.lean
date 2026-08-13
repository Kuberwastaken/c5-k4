import GraphConjecture59PathAttachmentObstruction

/-!
# WOWII 59: propagation forced by the full-fan residue

The center-plus-endpoint obstruction from v28 contains a four-vertex induced
path `q-p-a-w`, where `w` is the endpoint missed by `q`.  A third core-side
vertex `d`, nonadjacent to `a`, can be added unless it meets at least two of
`q,p,w`.  Thus the global hypothesis `f(G)=4` converts the local full fan into
a sharp two-neighbor cover constraint on every such third core vertex.
-/

namespace WrittenOnTheWallII.GraphConjecture59FullFanPropagation

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility
open WrittenOnTheWallII.GraphConjecture59PathFanClosure
open WrittenOnTheWallII.GraphConjecture59PathObstructionSplit
open WrittenOnTheWallII.GraphConjecture59PathAttachmentSplit
open WrittenOnTheWallII.GraphConjecture59PathAttachmentObstruction

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The third core-side vertex meets at least two vertices of the path frame
`q-p-a-w`, excluding `a`, to which it is known to be nonadjacent. -/
def ThirdCoreCover (G : SimpleGraph V) (d w p q : V) : Prop :=
  (G.Adj d q ∧ G.Adj d p) ∨
  (G.Adj d q ∧ G.Adj d w) ∨
  (G.Adj d p ∧ G.Adj d w)

omit [Fintype V] in
/-- Four vertices induce a forest when the three nonedges form a spanning
path in the complement. -/
theorem three_nonedges_frame_isAcyclic
    (G : SimpleGraph V) (a w p q : V)
    (hqa : ¬G.Adj q a) (hqw : ¬G.Adj q w) (hpw : ¬G.Adj p w) :
    (G.induce (({a, w, p, q} : Finset V) : Set V)).IsAcyclic := by
  have hqI : G.IsIndepSet (({q} : Finset V) : Set V) := by
    intro r hr s hs hrs hadj
    change r ∈ ({q} : Finset V) at hr
    change s ∈ ({q} : Finset V) at hs
    simp only [mem_singleton] at hr hs
    exact hrs (hr.trans hs.symm)
  have hqp :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
      G ({q} : Finset V) p hqI
  have hqp' :
      (G.induce (insert p ({q} : Set V))).IsAcyclic := by
    have hset :
        insert p ({q} : Set V) = (({p, q} : Finset V) : Set V) := by
      ext r
      simp
    rw [hset]
    exact hqp
  have hqpa := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert p ({q} : Set V)) a hqp' (by
      intro x hx y hy hax hay
      by_contra hxy
      simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hx hy
      rcases hx with rfl | rfl <;> rcases hy with rfl | rfl <;>
        simp_all [G.adj_comm])
  have hqpaw := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert a (insert p ({q} : Set V))) w hqpa (by
      intro x hx y hy hwx hwy
      by_contra hxy
      simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hx hy
      rcases hx with rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({a, w, p, q} : Finset V) : Set V) =
        insert w (insert a (insert p ({q} : Set V))) := by
    ext r
    simp [or_left_comm]
  rw [hset]
  exact hqpaw

omit [Fintype V] in
/-- The fixed full-fan frame `q-p-a-w` induces a forest. -/
theorem full_fan_frame_isAcyclic
    (G : SimpleGraph V) (a w p q : V)
    (_hpa : G.Adj p a) (_hpq : G.Adj p q) (_haw : G.Adj a w)
    (hqa : ¬G.Adj q a) (hqw : ¬G.Adj q w) (hpw : ¬G.Adj p w) :
    (G.induce (({a, w, p, q} : Finset V) : Set V)).IsAcyclic :=
  three_nonedges_frame_isAcyclic G a w p q hqa hqw hpw

omit [Fintype V] in
/-- With the fixed opposite nonedges `q-a` and `p-w`, the four-vertex frame
is acyclic unless all four perimeter edges of `q-p-a-w-q` are present. -/
theorem frame_isAcyclic_of_not_rectangle
    (G : SimpleGraph V) (a w p q : V)
    (hqa : ¬G.Adj q a) (hpw : ¬G.Adj p w)
    (hrect : ¬(G.Adj q p ∧ G.Adj p a ∧ G.Adj a w ∧ G.Adj w q)) :
    (G.induce (({a, w, p, q} : Finset V) : Set V)).IsAcyclic := by
  by_cases hqp : G.Adj q p
  · by_cases hpa : G.Adj p a
    · by_cases haw : G.Adj a w
      · have hqw : ¬G.Adj q w := by
          intro h
          exact hrect ⟨hqp, hpa, haw, h.symm⟩
        exact three_nonedges_frame_isAcyclic G a w p q hqa hqw hpw
      · have hacyc := three_nonedges_frame_isAcyclic
          G q w p a (by simpa [G.adj_comm] using hqa) haw hpw
        have hset :
            (({a, w, p, q} : Finset V) : Set V) =
              (({q, w, p, a} : Finset V) : Set V) := by
          ext r
          simp [or_comm, or_left_comm]
        rw [hset]
        exact hacyc
    · have hacyc := three_nonedges_frame_isAcyclic
        G q p w a (by simpa [G.adj_comm] using hqa)
          (by simpa [G.adj_comm] using hpa)
          (by simpa [G.adj_comm] using hpw)
      have hset :
          (({a, w, p, q} : Finset V) : Set V) =
            (({q, p, w, a} : Finset V) : Set V) := by
        ext r
        simp [or_comm, or_left_comm]
      rw [hset]
      exact hacyc
  · have hacyc := three_nonedges_frame_isAcyclic
      G a p w q hqa hqp (by simpa [G.adj_comm] using hpw)
    have hset :
        (({a, w, p, q} : Finset V) : Set V) =
          (({a, p, w, q} : Finset V) : Set V) := by
      ext r
      simp [or_left_comm]
    rw [hset]
    exact hacyc

omit [Fintype V] in
/-- A nonsaturated frame plus a third core vertex is a five-forest whenever
the latter fails the same two-neighbor cover. -/
theorem frame_with_sparse_third_core_isAcyclic
    (G : SimpleGraph V) (a d w p q : V)
    (had : ¬G.Adj a d) (hqa : ¬G.Adj q a) (hpw : ¬G.Adj p w)
    (hrect : ¬(G.Adj q p ∧ G.Adj p a ∧ G.Adj a w ∧ G.Adj w q))
    (hcover : ¬ThirdCoreCover G d w p q) :
    (G.induce (({a, d, w, p, q} : Finset V) : Set V)).IsAcyclic := by
  have hframe := frame_isAcyclic_of_not_rectangle G a w p q hqa hpw hrect
  have hplus := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G ((({a, w, p, q} : Finset V) : Set V)) d hframe (by
      intro x hx y hy hdx hdy
      by_contra hxy
      change x ∈ ({a, w, p, q} : Finset V) at hx
      change y ∈ ({a, w, p, q} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;>
        simp_all [ThirdCoreCover, G.adj_comm])
  have hset :
      (({a, d, w, p, q} : Finset V) : Set V) =
        insert d ((({a, w, p, q} : Finset V) : Set V)) := by
    ext r
    simp [or_left_comm]
  rw [hset]
  exact hplus

/-- Under `f(G)=4`, every nonsaturated frame forces the third-core cover. -/
theorem third_core_cover_of_nonsaturated_frame_of_f_eq_four
    (G : SimpleGraph V) (a d w p q : V)
    (hdist : PairwiseDistinctPathExtensions a d w p q)
    (had : ¬G.Adj a d) (hqa : ¬G.Adj q a) (hpw : ¬G.Adj p w)
    (hrect : ¬(G.Adj q p ∧ G.Adj p a ∧ G.Adj a w ∧ G.Adj w q))
    (hf : G.largestInducedForestSize = 4) :
    ThirdCoreCover G d w p q := by
  by_contra hcover
  have hacyc := frame_with_sparse_third_core_isAcyclic
    G a d w p q had hqa hpw hrect hcover
  have hcard : ({a, d, w, p, q} : Finset V).card = 5 := by
    rcases hdist with ⟨hadV, hawV, hapV, haqV, hdwV,
      hdpV, hdqV, hwpV, hwqV, hpqV⟩
    simp [hadV, hawV, hapV, haqV, hdwV, hdpV, hdqV, hwpV, hwqV, hpqV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, d, w, p, q} : Finset V) hacyc
  rw [hcard, hf] at hbound
  omega

omit [Fintype V] in
/-- If the third core vertex does not satisfy the two-neighbor cover, it can
be added to the full-fan frame without creating a cycle. -/
theorem full_fan_frame_with_sparse_third_core_isAcyclic
    (G : SimpleGraph V) (a d w p q : V)
    (hpa : G.Adj p a) (hpq : G.Adj p q) (haw : G.Adj a w)
    (had : ¬G.Adj a d)
    (hqa : ¬G.Adj q a) (hqw : ¬G.Adj q w) (hpw : ¬G.Adj p w)
    (hcover : ¬ThirdCoreCover G d w p q) :
    (G.induce (({a, d, w, p, q} : Finset V) : Set V)).IsAcyclic := by
  have hframe := full_fan_frame_isAcyclic
    G a w p q hpa hpq haw hqa hqw hpw
  have hplus := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G ((({a, w, p, q} : Finset V) : Set V)) d hframe (by
      intro x hx y hy hdx hdy
      by_contra hxy
      change x ∈ ({a, w, p, q} : Finset V) at hx
      change y ∈ ({a, w, p, q} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl | rfl <;>
        simp_all [ThirdCoreCover, G.adj_comm])
  have hset :
      (({a, d, w, p, q} : Finset V) : Set V) =
        insert d ((({a, w, p, q} : Finset V) : Set V)) := by
    ext r
    simp [or_left_comm]
  rw [hset]
  exact hplus

/-- A sparse third core vertex gives an explicit five-forest. -/
theorem five_le_f_of_sparse_third_core_in_full_fan_frame
    (G : SimpleGraph V) (a d w p q : V)
    (hdist : PairwiseDistinctPathExtensions a d w p q)
    (hpa : G.Adj p a) (hpq : G.Adj p q) (haw : G.Adj a w)
    (had : ¬G.Adj a d)
    (hqa : ¬G.Adj q a) (hqw : ¬G.Adj q w) (hpw : ¬G.Adj p w)
    (hcover : ¬ThirdCoreCover G d w p q) :
    5 ≤ G.largestInducedForestSize := by
  have hacyc := full_fan_frame_with_sparse_third_core_isAcyclic
    G a d w p q hpa hpq haw had hqa hqw hpw hcover
  have hcard : ({a, d, w, p, q} : Finset V).card = 5 := by
    rcases hdist with ⟨hadV, hawV, hapV, haqV, hdwV,
      hdpV, hdqV, hwpV, hwqV, hpqV⟩
    simp [hadV, hawV, hapV, haqV, hdwV, hdpV, hdqV, hwpV, hwqV, hpqV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({a, d, w, p, q} : Finset V) hacyc
  simpa [hcard] using hbound

/-- **Global propagation.** Under `f(G)=4`, every same-side third core vertex
must hit at least two of `q,p,w`; otherwise the preceding explicit five-set
contradicts maximality. -/
theorem third_core_cover_of_full_fan_frame_of_f_eq_four
    (G : SimpleGraph V) (a d w p q : V)
    (hdist : PairwiseDistinctPathExtensions a d w p q)
    (hpa : G.Adj p a) (hpq : G.Adj p q) (haw : G.Adj a w)
    (had : ¬G.Adj a d)
    (hqa : ¬G.Adj q a) (hqw : ¬G.Adj q w) (hpw : ¬G.Adj p w)
    (hf : G.largestInducedForestSize = 4) :
    ThirdCoreCover G d w p q := by
  by_contra hcover
  have hfive := five_le_f_of_sparse_third_core_in_full_fan_frame
    G a d w p q hdist hpa hpq haw had hqa hqw hpw hcover
  omega

/-- Specialization to the center-plus-exactly-one-endpoint full-fan residue.
The endpoint missed by `q` becomes the frame endpoint `w`. -/
theorem center_endpoint_full_fan_forces_third_core_cover
    (G : SimpleGraph V) (a b d u c v p q : V)
    (hdistU : PairwiseDistinctPathExtensions a d u p q)
    (hdistV : PairwiseDistinctPathExtensions a d v p q)
    (halign : AlignedOutsideTriple G a b u c v)
    (hcompat : OppositeSideCompatible G a b u c v p q)
    (hattach : G.Adj q c ∧
      ((G.Adj q u ∧ ¬G.Adj q v) ∨ (¬G.Adj q u ∧ G.Adj q v)))
    (hfan : CoreExtensionFan G a b p q)
    (had : ¬G.Adj a d)
    (hf : G.largestInducedForestSize = 4) :
    (G.Adj q u ∧ ¬G.Adj q v ∧ ThirdCoreCover G d v p q) ∨
      (¬G.Adj q u ∧ G.Adj q v ∧ ThirdCoreCover G d u p q) := by
  rcases hcompat with ⟨hpu, hpc, hpv, hqa, hqb⟩
  rcases hfan with ⟨hpq, hpa, hpb⟩
  rcases hattach.2 with hleft | hright
  · exact Or.inl ⟨hleft.1, hleft.2,
      third_core_cover_of_full_fan_frame_of_f_eq_four
        G a d v p q hdistV hpa hpq halign.2.2.1 had hqa hleft.2 hpv hf⟩
  · exact Or.inr ⟨hright.1, hright.2,
      third_core_cover_of_full_fan_frame_of_f_eq_four
        G a d u p q hdistU hpa hpq halign.1 had hqa hright.1 hpu hf⟩

/-- The endpoints-only residue propagates through the missed center.  The
edge `p-q` is irrelevant, matching the v28 obstruction table. -/
theorem endpoints_only_forces_third_core_cover
    (G : SimpleGraph V) (a b d u c v p q : V)
    (hdist : PairwiseDistinctPathExtensions a d c p q)
    (hcompat : OppositeSideCompatible G a b u c v p q)
    (hattach : G.Adj q u ∧ ¬G.Adj q c ∧ G.Adj q v)
    (had : ¬G.Adj a d)
    (hf : G.largestInducedForestSize = 4) :
    ThirdCoreCover G d c p q := by
  rcases hcompat with ⟨hpu, hpc, hpv, hqa, hqb⟩
  apply third_core_cover_of_nonsaturated_frame_of_f_eq_four
    G a d c p q hdist had hqa hpc
  · intro hrect
    exact hattach.2.1 hrect.2.2.2.symm
  · exact hf

/-- In the all-three attachment case, any core choice for which the two fan
edges `p-q` and `p-a` are not both present yields the same forced cover.  The
only case not covered is the fully saturated rectangle. -/
theorem all_three_nonsaturated_core_forces_cover
    (G : SimpleGraph V) (a d w p q : V)
    (hdist : PairwiseDistinctPathExtensions a d w p q)
    (had : ¬G.Adj a d) (hqa : ¬G.Adj q a) (hpw : ¬G.Adj p w)
    (hfanmiss : ¬(G.Adj p q ∧ G.Adj p a))
    (hf : G.largestInducedForestSize = 4) :
    ThirdCoreCover G d w p q := by
  apply third_core_cover_of_nonsaturated_frame_of_f_eq_four
    G a d w p q hdist had hqa hpw
  · intro hrect
    exact hfanmiss ⟨hrect.1.symm, hrect.2.1⟩
  · exact hf

end WrittenOnTheWallII.GraphConjecture59FullFanPropagation
