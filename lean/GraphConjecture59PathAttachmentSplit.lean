import GraphConjecture59PathFanClosure

/-!
# WOWII 59: attachment split for the remaining path obstruction
-/

namespace WrittenOnTheWallII.GraphConjecture59PathAttachmentSplit

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
open WrittenOnTheWallII.GraphConjecture59TwoVertexCompatibility
open WrittenOnTheWallII.GraphConjecture59PathFanClosure

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
lemma induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    (G : SimpleGraph V) (S : Set V) (v : V)
    (hS : (G.induce S).IsAcyclic)
    (huniq : ∀ x ∈ S, ∀ y ∈ S,
      G.Adj v x → G.Adj v y → x = y) :
    (G.induce (insert v S)).IsAcyclic := by
  let T : Set V := insert v S
  let H : SimpleGraph T := G.induce T
  let w : T := ⟨v, by simp [T]⟩
  have hbase : (H.induce {x : T | (x : V) ∈ S}).IsAcyclic := by
    let f : H.induce {x : T | (x : V) ∈ S} →g G.induce (S : Set V) :=
      { toFun := fun x ↦ ⟨(x : V), x.property⟩
        map_rel' := fun hadj ↦ SimpleGraph.induce_adj.mpr <|
          SimpleGraph.induce_adj.mp hadj }
    apply hS.comap f
    intro x y h
    apply Subtype.ext
    apply Subtype.ext
    exact congrArg (fun z : ↑(S : Set V) ↦ (z : V)) h
  show H.IsAcyclic
  intro r c hc
  by_cases hw : w ∈ c.support
  · let d := c.rotate hw
    have hd : d.IsCycle := hc.rotate hw
    have hvs : H.Adj w d.snd := by
      exact d.adj_snd hd.not_nil
    have hvp : H.Adj w d.penultimate := by
      exact (d.adj_penultimate hd.not_nil).symm
    have hsS : (d.snd : V) ∈ S := by
      have hsT : (d.snd : V) ∈ insert v S := d.snd.property
      rcases Set.mem_insert_iff.mp hsT with hs | hs
      · exact False.elim (hvs.ne (Subtype.ext hs.symm))
      · exact hs
    have hpS : (d.penultimate : V) ∈ S := by
      have hpT : (d.penultimate : V) ∈ insert v S := d.penultimate.property
      rcases Set.mem_insert_iff.mp hpT with hp | hp
      · exact False.elim (hvp.ne (Subtype.ext hp.symm))
      · exact hp
    apply hd.snd_ne_penultimate
    apply Subtype.ext
    exact huniq d.snd hsS d.penultimate hpS
      (SimpleGraph.induce_adj.mp hvs) (SimpleGraph.induce_adj.mp hvp)
  · have hall : ∀ x ∈ c.support, x ∈ {x : T | (x : V) ∈ S} := by
      intro x hx
      have hxT : (x : V) ∈ insert v S := x.property
      rcases Set.mem_insert_iff.mp hxT with hxv | hxS
      · have hxw : x = w := Subtype.ext hxv
        exact False.elim (hw (hxw ▸ hx))
      · exact hxS
    let d := c.induce {x : T | (x : V) ∈ S} hall
    apply hbase d
    have hm : (d.map (Embedding.induce _).toHom).IsCycle := by
      rw [Walk.map_induce c hall]
      exact hc
    exact (Walk.map_isCycle_iff_of_injective
      (Embedding.induce (G := H) ({x : T | (x : V) ∈ S})).injective).mp hm

/-- `q` meets at least two vertices of the outside triple. -/
def QHitsTwoOutside (G : SimpleGraph V) (x y z q : V) : Prop :=
  (G.Adj q x ∧ G.Adj q y) ∨
  (G.Adj q x ∧ G.Adj q z) ∨
  (G.Adj q y ∧ G.Adj q z)

omit [Fintype V] in
/-- The path together with `p,q` is acyclic whenever `q` has at most one
neighbor on the path. -/
theorem path_extensions_isAcyclic_of_q_hits_at_most_one
    (G : SimpleGraph V) (u c v p q : V)
    (huv : ¬G.Adj u v)
    (hpu : ¬G.Adj p u) (hpc : ¬G.Adj p c) (hpv : ¬G.Adj p v)
    (hq : ¬((G.Adj q u ∧ G.Adj q c) ∨
      (G.Adj q u ∧ G.Adj q v) ∨ (G.Adj q c ∧ G.Adj q v))) :
    (G.induce (({u, c, v, p, q} : Finset V) : Set V)).IsAcyclic := by
  have hpath :
      (G.induce (({u, c, v} : Finset V) : Set V)).IsAcyclic := by
    have hI : G.IsIndepSet (({u, v} : Finset V) : Set V) := by
      intro r hr s hs hrs hadj
      change r ∈ ({u, v} : Finset V) at hr
      change s ∈ ({u, v} : Finset V) at hs
      simp only [mem_insert, mem_singleton] at hr hs
      rcases hr with rfl | rfl <;> rcases hs with rfl | rfl <;>
        simp_all [G.adj_comm]
    have hacyc :=
      _root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
        G ({u, v} : Finset V) c hI
    have hset :
        (({u, c, v} : Finset V) : Set V) =
          (({c, u, v} : Finset V) : Set V) := by
      ext r
      simp [or_left_comm]
    rw [hset]
    exact hacyc
  have hqacyc := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (({u, c, v} : Finset V) : Set V) q hpath (by
      intro x hx y hy hqx hqy
      by_contra hxy
      change x ∈ ({u, c, v} : Finset V) at hx
      change y ∈ ({u, c, v} : Finset V) at hy
      simp only [mem_insert, mem_singleton] at hx hy
      rcases hx with rfl | rfl | rfl <;>
        rcases hy with rfl | rfl | rfl <;>
        simp_all [G.adj_comm])
  have hpacyc := induce_insert_isAcyclic_of_acyclic_of_unique_neighbor
    G (insert q ((({u, c, v} : Finset V) : Set V))) p hqacyc (by
      intro x hx y hy hpx hpy
      by_contra hxy
      simp only [Set.mem_insert_iff] at hx hy
      rcases hx with rfl | hx <;> rcases hy with rfl | hy
      · exact hxy rfl
      · change y ∈ ({u, c, v} : Finset V) at hy
        simp only [mem_insert, mem_singleton] at hy
        rcases hy with rfl | rfl | rfl <;> simp_all [G.adj_comm]
      · change x ∈ ({u, c, v} : Finset V) at hx
        simp only [mem_insert, mem_singleton] at hx
        rcases hx with rfl | rfl | rfl <;> simp_all [G.adj_comm]
      · change x ∈ ({u, c, v} : Finset V) at hx
        change y ∈ ({u, c, v} : Finset V) at hy
        simp only [mem_insert, mem_singleton] at hx hy
        rcases hx with rfl | rfl | rfl <;>
          rcases hy with rfl | rfl | rfl <;> simp_all [G.adj_comm])
  have hset :
      (({u, c, v, p, q} : Finset V) : Set V) =
        insert p (insert q ((({u, c, v} : Finset V) : Set V))) := by
    ext r
    simp [or_comm, or_left_comm]
  rw [hset]
  exact hpacyc

/-- The explicit five-set gives the forest bound under the at-most-one-hit
condition. -/
theorem five_le_f_of_q_hits_at_most_one
    (G : SimpleGraph V) (u c v p q : V)
    (hdist : PairwiseDistinctPathExtensions u c v p q)
    (huv : ¬G.Adj u v)
    (hpu : ¬G.Adj p u) (hpc : ¬G.Adj p c) (hpv : ¬G.Adj p v)
    (hq : ¬((G.Adj q u ∧ G.Adj q c) ∨
      (G.Adj q u ∧ G.Adj q v) ∨ (G.Adj q c ∧ G.Adj q v))) :
    5 ≤ G.largestInducedForestSize := by
  have hacyc := path_extensions_isAcyclic_of_q_hits_at_most_one
    G u c v p q huv hpu hpc hpv hq
  have hcard : ({u, c, v, p, q} : Finset V).card = 5 := by
    rcases hdist with ⟨huc, huvV, hup, huq, hcv, hcp, hcq, hvp, hvq, hpq⟩
    simp [huc, huvV, hup, huq, hcv, hcp, hcq, hvp, hvq, hpq]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G ({u, c, v, p, q} : Finset V) hacyc
  simpa [hcard] using hbound

/-- **Exact next obstruction split.** In the outside-path branch, either an
explicit five-vertex induced forest exists, or `q` hits at least two of the
three path vertices. -/
theorem five_le_f_or_q_hits_two_outside
    (G : SimpleGraph V) (a b x y z p q : V)
    (hdist : PairwiseDistinctSeven a b x y z p q)
    (hout : RealizesOutsideType G x y z .path)
    (hcompat : OppositeSideCompatible G a b x y z p q) :
    5 ≤ G.largestInducedForestSize ∨ QHitsTwoOutside G x y z q := by
  by_cases hq : QHitsTwoOutside G x y z q
  · exact Or.inr hq
  · left
    rcases hdist with ⟨hfive, hpa, hpb, hpx, hpy, hpz,
      hqa, hqb, hqxV, hqyV, hqzV, hpq⟩
    rcases hfive with ⟨habV, haxV, hayV, hazV, hbxV, hbyV, hbzV,
      hxyV, hxzV, hyzV⟩
    rcases hcompat with ⟨hpxE, hpyE, hpzE, hqaE, hqbE⟩
    rcases hout with h | h | h
    · exact five_le_f_of_q_hits_at_most_one G y x z p q
        ⟨hxyV.symm, hyzV, hpy.symm, hqyV.symm, hxzV, hpx.symm,
          hqxV.symm, hpz.symm, hqzV.symm, hpq⟩
        h.2.2 hpyE hpxE hpzE (by
          simp only [QHitsTwoOutside] at hq ⊢
          tauto)
    · exact five_le_f_of_q_hits_at_most_one G x y z p q
        ⟨hxyV, hxzV, hpx.symm, hqxV.symm, hyzV, hpy.symm,
          hqyV.symm, hpz.symm, hqzV.symm, hpq⟩
        h.2.2 hpxE hpyE hpzE hq
    · exact five_le_f_of_q_hits_at_most_one G x z y p q
        ⟨hxzV, hxyV, hpx.symm, hqxV.symm, hyzV.symm, hpz.symm,
          hqzV.symm, hpy.symm, hqyV.symm, hpq⟩
        h.2.2 hpxE hpzE hpyE (by
          simp only [QHitsTwoOutside] at hq ⊢
          tauto)

end WrittenOnTheWallII.GraphConjecture59PathAttachmentSplit
