import GraphConjecture141Splice

/-!
# WOWII 141: the leaf-extension bridge for girth six and seven

This file proves the missing generic graph lemma: adjoining one vertex with a
unique neighbor to a tree preserves `IsTree`.  It then packages the precise
distance-two/max-center hypotheses sufficient to build the v0.9 splice.
-/

namespace WrittenOnTheWallII.GraphConjecture141GirthSeven

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141Splice
open WrittenOnTheWallII.GraphConjecture141Extraction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- Adjoining a vertex with exactly one neighbor to a tree preserves the tree
property.  The old tree is represented as the induced complement of the new
vertex. -/
lemma isTree_of_induce_compl_singleton_isTree_of_existsUnique_adj
    (H : SimpleGraph V) (x : V)
    (hbase : (H.induce ({x}ᶜ : Set V)).IsTree)
    (hleaf : ∃! a : V, H.Adj x a) :
    H.IsTree := by
  classical
  obtain ⟨a, hxa, huniq⟩ := hleaf
  have hax : a ≠ x := hxa.ne.symm
  have ha : a ∈ ({x}ᶜ : Set V) := by simp [hax]
  have hconn : H.Connected := by
    rw [connected_iff_exists_forall_reachable]
    refine ⟨a, ?_⟩
    intro w
    by_cases hw : w = x
    · subst w
      exact hxa.symm.reachable
    · let a' : ({x}ᶜ : Set V) := ⟨a, ha⟩
      let w' : ({x}ᶜ : Set V) := ⟨w, by simp [hw]⟩
      have hr : (H.induce ({x}ᶜ : Set V)).Reachable a' w' :=
        hbase.isConnected a' w'
      simpa [a', w'] using hr.map (Embedding.induce _).toHom
  refine ⟨hconn, ?_⟩
  intro v p hp
  by_cases hxmem : x ∈ p.support
  · let q := p.rotate hxmem
    have hq : q.IsCycle := hp.rotate hxmem
    have hxsnd : H.Adj x q.snd := q.adj_snd hq.not_nil
    have hxpen : H.Adj x q.penultimate :=
      (q.adj_penultimate hq.not_nil).symm
    exact hq.snd_ne_penultimate (huniq q.snd hxsnd |>.trans (huniq q.penultimate hxpen).symm)
  · have hcontained : ∀ y ∈ p.support, y ∈ ({x}ᶜ : Set V) := by
      intro y hy
      simp only [Set.mem_compl_iff, Set.mem_singleton_iff]
      exact fun hyx => hxmem (hyx ▸ hy)
    let q := p.induce ({x}ᶜ : Set V) hcontained
    let emb : H.induce ({x}ᶜ : Set V) ↪g H := Embedding.induce _
    have hq : q.IsCycle := by
      have hmap : (q.map emb.toHom).IsCycle := by
        simpa [q, emb] using hp
      exact (Walk.map_isCycle_iff_of_injective
        (p := q) (f := emb.toHom) emb.injective).mp hmap
    exact hbase.IsAcyclic q hq

/-- Concrete data sufficient for the distance-two splice.  The local set is
maximum both at its center and globally; `extra` attaches to exactly one
retained local vertex. -/
structure DistanceTwoLeafData (G : SimpleGraph V) [DecidableRel G.Adj] where
  center : V
  localSet : Finset V
  extra : V
  attachment : V
  localIndependent : G.IsIndepSet (localSet : Set V)
  localSubset : localSet ⊆ G.neighborFinset center
  localCard : localSet.card = indepNeighborsCard G center
  centerMaximal : indepNeighborsCard G center =
    Finset.univ.sup (indepNeighborsCard G)
  attachment_mem : attachment ∈ localSet
  extra_not_mem : extra ∉ insert center localSet
  center_extra_nonadj : ¬G.Adj center extra
  extra_unique_local : ∀ a ∈ localSet, G.Adj extra a ↔ a = attachment

/-- The explicit star-plus-leaf set induced by `DistanceTwoLeafData` is a
tree. -/
lemma distanceTwoLeaf_inducedTree
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (D : DistanceTwoLeafData G) :
    (G.induce
      (↑(insert D.extra (insert D.center D.localSet)) : Set V)).IsTree := by
  let S : Finset V := insert D.extra (insert D.center D.localSet)
  let H := G.induce (↑S : Set V)
  let x : (S : Set V) := ⟨D.extra, by simp [S]⟩
  have hx_unique : ∃! a : (S : Set V), H.Adj x a := by
    let a : (S : Set V) := ⟨D.attachment, by simp [S, D.attachment_mem]⟩
    refine ⟨a, ?_, ?_⟩
    · apply SimpleGraph.induce_adj.mpr
      exact (D.extra_unique_local D.attachment D.attachment_mem).mpr rfl
    · intro y hxy
      apply Subtype.ext
      have hxyG : G.Adj D.extra (y : V) := SimpleGraph.induce_adj.mp hxy
      have hyS : (y : V) = D.extra ∨ (y : V) = D.center ∨ (y : V) ∈ D.localSet := by
        simpa [S] using y.property
      rcases hyS with hyx | hyc | hyA
      · exact (G.loopless D.extra (hyx ▸ hxyG)).elim
      · exact (D.center_extra_nonadj (hyc ▸ hxyG.symm)).elim
      · exact (D.extra_unique_local y hyA).mp hxyG
  have hbase : (H.induce ({x}ᶜ : Set (S : Set V))).IsTree := by
    let B : Finset V := insert D.center D.localSet
    let f : (↥({x}ᶜ : Set (S : Set V))) → (↥(↑B : Set V)) := fun y =>
      ⟨y.val.val, by
        have hyS : y.val.val = D.extra ∨ y.val.val ∈ B := by
          simpa [S, B] using y.val.property
        rcases hyS with hye | hyB
        · exfalso
          apply y.property
          apply Subtype.ext
          exact hye
        · exact hyB⟩
    have hf_inj : Function.Injective f := by
      intro y z hyz
      apply Subtype.ext
      apply Subtype.ext
      simpa [f] using congrArg Subtype.val hyz
    have hf_surj : Function.Surjective f := by
      intro z
      let ys : (S : Set V) := ⟨z, by
        change (z : V) ∈ insert D.extra (insert D.center D.localSet)
        exact Finset.mem_insert_of_mem z.property⟩
      have hysx : ys ≠ x := by
        intro h
        apply D.extra_not_mem
        have hzextra : (z : V) = D.extra := congrArg Subtype.val h
        simpa [B, hzextra] using z.property
      let y : (↥({x}ᶜ : Set (S : Set V))) := ⟨ys, by
        simpa only [Set.mem_compl_iff, Set.mem_singleton_iff] using hysx⟩
      refine ⟨y, ?_⟩
      apply Subtype.ext
      rfl
    let e : (↥({x}ᶜ : Set (S : Set V))) ≃ (↥(↑B : Set V)) :=
      Equiv.ofBijective f ⟨hf_inj, hf_surj⟩
    let iso : H.induce ({x}ᶜ : Set (S : Set V)) ≃g
        G.induce (↑B : Set V) := {
      toEquiv := e
      map_rel_iff' := by intro y z; rfl
    }
    apply iso.isTree_iff.mpr
    apply induce_insert_isTree_of_indep_neighbors G D.center D.localSet
      D.localIndependent
    intro y hy
    rw [← coe_neighborFinset]
    exact D.localSubset hy
  simpa [H, S] using
    isTree_of_induce_compl_singleton_isTree_of_existsUnique_adj H x hbase hx_unique

/-- The concrete distance-two leaf data discharges every field of the abstract
v0.9 splice certificate. -/
def DistanceTwoLeafData.toOneVertexSplice
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (D : DistanceTwoLeafData G) : OneVertexSplice G where
  center := D.center
  localSet := D.localSet
  extra := D.extra
  localIndependent := D.localIndependent
  localSubset := D.localSubset
  localCard := D.localCard
  centerMaximal := D.centerMaximal
  extra_not_mem := D.extra_not_mem
  inducedTree := distanceTwoLeaf_inducedTree G D

/-- Exact upstream-shaped WOWII 141 in the new girth-six-or-seven range,
assuming the sharply isolated max-center distance-two leaf data. -/
theorem conjecture141_of_girth_six_or_seven_of_distanceTwoLeafData
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 6 ≤ G.girth) (hgirthUpper : G.girth ≤ 7)
    (D : DistanceTwoLeafData G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  exact conjecture141_of_girth_six_or_seven_of_oneVertexSplice
    G hgirthLower hgirthUpper (D.toOneVertexSplice G)

end WrittenOnTheWallII.GraphConjecture141GirthSeven
