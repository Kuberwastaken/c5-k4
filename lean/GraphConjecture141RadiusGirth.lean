import GraphConjecture141EccentricityThree

/-!
# WOWII 141: certified second-leaf assembly
-/

namespace WrittenOnTheWallII.GraphConjecture141RadiusGirth

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141GirthSeven
open WrittenOnTheWallII.GraphConjecture141GirthNine

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- A verified one-leaf star together with a second vertex whose unique
neighbor in the retained first-stage tree is the first leaf. -/
structure SecondLeafData (G : SimpleGraph V) [DecidableRel G.Adj] where
  base : DistanceTwoLeafData G
  second : V
  second_not_mem : second ∉ insert base.extra (insert base.center base.localSet)
  second_unique_base :
    ∀ z ∈ insert base.extra (insert base.center base.localSet),
      G.Adj second z ↔ z = base.extra

omit [Nonempty V] in
/-- Adjoining the certified second leaf preserves the induced-tree property.
This discharges the representation-sensitive assembly left after v0.14. -/
lemma secondLeaf_inducedTree
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (D : SecondLeafData G) :
    (G.induce
      (↑(insert D.second
        (insert D.base.extra (insert D.base.center D.base.localSet))) : Set V)).IsTree := by
  let B : Finset V := insert D.base.extra (insert D.base.center D.base.localSet)
  let S : Finset V := insert D.second B
  let H := G.induce (↑S : Set V)
  let y : (S : Set V) := ⟨D.second, by simp [S]⟩
  have hy_unique : ∃! z : (S : Set V), H.Adj y z := by
    let x : (S : Set V) := ⟨D.base.extra, by simp [S, B]⟩
    refine ⟨x, ?_, ?_⟩
    · apply SimpleGraph.induce_adj.mpr
      exact (D.second_unique_base D.base.extra (by simp)).mpr rfl
    · intro z hyz
      apply Subtype.ext
      have hyzG : G.Adj D.second (z : V) := SimpleGraph.induce_adj.mp hyz
      have hzS : (z : V) = D.second ∨ (z : V) ∈ B := by
        simpa [S] using z.property
      rcases hzS with hzy | hzB
      · exact (G.loopless D.second (hzy ▸ hyzG)).elim
      · exact (D.second_unique_base z (by simpa [B] using hzB)).mp hyzG
  have hbase : (H.induce ({y}ᶜ : Set (S : Set V))).IsTree := by
    let f : (↥({y}ᶜ : Set (S : Set V))) → (↥(↑B : Set V)) := fun z =>
      ⟨z.val.val, by
        have hzS : z.val.val = D.second ∨ z.val.val ∈ B := by
          simpa [S] using z.val.property
        rcases hzS with hze | hzB
        · exfalso
          apply z.property
          apply Subtype.ext
          exact hze
        · exact hzB⟩
    have hf_inj : Function.Injective f := by
      intro z w hzw
      apply Subtype.ext
      apply Subtype.ext
      simpa [f] using congrArg Subtype.val hzw
    have hf_surj : Function.Surjective f := by
      intro z
      let zs : (S : Set V) := ⟨z, by
        change (z : V) ∈ insert D.second B
        exact Finset.mem_insert_of_mem z.property⟩
      have hzsy : zs ≠ y := by
        intro h
        apply D.second_not_mem
        have hzsecond : (z : V) = D.second := congrArg Subtype.val h
        simpa [B, hzsecond] using z.property
      let z' : (↥({y}ᶜ : Set (S : Set V))) := ⟨zs, by
        simpa only [Set.mem_compl_iff, Set.mem_singleton_iff] using hzsy⟩
      refine ⟨z', ?_⟩
      apply Subtype.ext
      rfl
    let e : (↥({y}ᶜ : Set (S : Set V))) ≃ (↥(↑B : Set V)) :=
      Equiv.ofBijective f ⟨hf_inj, hf_surj⟩
    let iso : H.induce ({y}ᶜ : Set (S : Set V)) ≃g
        G.induce (↑B : Set V) := {
      toEquiv := e
      map_rel_iff' := by intro z w; rfl
    }
    apply iso.isTree_iff.mpr
    exact distanceTwoLeaf_inducedTree G D.base
  simpa [H, S, B] using
    isTree_of_induce_compl_singleton_isTree_of_existsUnique_adj H y hbase hy_unique

/-- Second-leaf data constructs the abstract two-tail splice with no assumed
tree field. -/
def SecondLeafData.toTwoVertexTailSplice
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (D : SecondLeafData G) : TwoVertexTailSplice G where
  center := D.base.center
  localSet := D.base.localSet
  first := D.base.extra
  second := D.second
  localIndependent := D.base.localIndependent
  localSubset := D.base.localSubset
  localCard := D.base.localCard
  centerMaximal := D.base.centerMaximal
  first_not_mem := D.base.extra_not_mem
  second_not_mem := D.second_not_mem
  inducedTree := secondLeaf_inducedTree G D

omit [Nonempty V] in
/-- Exact WOWII 141 at girth eight or nine from explicit second-leaf
adjacency data; the final tree property is now derived rather than assumed. -/
theorem conjecture141_of_girth_eight_or_nine_of_secondLeafData
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 8 ≤ G.girth) (hgirthUpper : G.girth ≤ 9)
    (D : SecondLeafData G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  exact conjecture141_of_girth_eight_or_nine_of_twoVertexTailSplice
    G hgirthLower hgirthUpper (D.toTwoVertexTailSplice G)

end WrittenOnTheWallII.GraphConjecture141RadiusGirth
