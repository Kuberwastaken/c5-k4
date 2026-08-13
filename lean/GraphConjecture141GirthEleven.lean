import GraphConjecture141GirthNineClosure

/-!
# WOWII 141: reusable third-leaf assembly for girth ten and eleven
-/

namespace WrittenOnTheWallII.GraphConjecture141GirthEleven

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture141GirthNine
open WrittenOnTheWallII.GraphConjecture141GirthSeven
open WrittenOnTheWallII.GraphConjecture141RadiusGirth
open WrittenOnTheWallII.GraphConjecture141RadiusTwoAcyclic
open WrittenOnTheWallII.GraphConjecture141Extraction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V] [Nonempty V]

/-- A maximum local star with three genuine tail vertices. -/
structure ThreeVertexTailSplice (G : SimpleGraph V) [DecidableRel G.Adj] where
  center : V
  localSet : Finset V
  first : V
  second : V
  third : V
  localIndependent : G.IsIndepSet (localSet : Set V)
  localSubset : localSet ⊆ G.neighborFinset center
  localCard : localSet.card = indepNeighborsCard G center
  centerMaximal : indepNeighborsCard G center =
    Finset.univ.sup (indepNeighborsCard G)
  first_not_mem : first ∉ insert center localSet
  second_not_mem : second ∉ insert first (insert center localSet)
  third_not_mem : third ∉
    insert second (insert first (insert center localSet))
  inducedTree :
    (G.induce (↑(insert third
      (insert second (insert first (insert center localSet)))) : Set V)).IsTree

omit [Nonempty V] in
/-- Exact cardinality of the maximum local star with a three-vertex tail. -/
lemma card_threeVertexTail
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (W : ThreeVertexTailSplice G) :
    (insert W.third
      (insert W.second (insert W.first (insert W.center W.localSet)))).card =
      Finset.univ.sup (indepNeighborsCard G) + 4 := by
  have hcenter : W.center ∉ W.localSet := by
    intro hc
    exact G.loopless W.center (by
      rw [← mem_neighborFinset]
      exact W.localSubset hc)
  rw [Finset.card_insert_of_notMem W.third_not_mem,
    Finset.card_insert_of_notMem W.second_not_mem,
    Finset.card_insert_of_notMem W.first_not_mem,
    Finset.card_insert_of_notMem hcenter, W.localCard, W.centerMaximal]

omit [Nonempty V] in
/-- The three-tail certificate pays the four vertices beyond maximum local
independence required at girth ten and eleven. -/
theorem localIndependenceMax_add_four_le_largestInducedTreeSize
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (W : ThreeVertexTailSplice G) :
    Finset.univ.sup (indepNeighborsCard G) + 4 ≤
      G.largestInducedTreeSize := by
  rw [← card_threeVertexTail G W]
  exact card_le_largestInducedTreeSize G _ W.inducedTree

omit [Nonempty V] in
/-- Exact upstream-shaped WOWII 141 at girth ten or eleven from a
three-vertex-tail certificate. -/
theorem conjecture141_of_girth_ten_or_eleven_of_threeVertexTailSplice
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 10 ≤ G.girth) (hgirthUpper : G.girth ≤ 11)
    (W : ThreeVertexTailSplice G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  have htail := localIndependenceMax_add_four_le_largestInducedTreeSize G W
  have hhalf : G.girth / 2 ≤ 5 := by omega
  have htailZ :
      ((Finset.univ.sup (indepNeighborsCard G) + 4 : ℕ) : ℤ) ≤
        (largestInducedTreeSize G : ℤ) := by exact_mod_cast htail
  have hhalfZ : ((G.girth / 2 : ℕ) : ℤ) ≤ 5 := by exact_mod_cast hhalf
  omega

/-- A third leaf attached uniquely to the end of an already verified
two-vertex tail. -/
structure ThirdLeafData (G : SimpleGraph V) [DecidableRel G.Adj] where
  base : TwoVertexTailSplice G
  third : V
  third_not_mem : third ∉ insert base.second
    (insert base.first (insert base.center base.localSet))
  third_unique_base :
    ∀ z ∈ insert base.second
      (insert base.first (insert base.center base.localSet)),
      G.Adj third z ↔ z = base.second

omit [Nonempty V] in
/-- Reusable leaf extension on top of an arbitrary verified two-tail tree. -/
lemma thirdLeaf_inducedTree
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (D : ThirdLeafData G) :
    (G.induce (↑(insert D.third (insert D.base.second
      (insert D.base.first (insert D.base.center D.base.localSet)))) : Set V)).IsTree := by
  let B : Finset V := insert D.base.second
    (insert D.base.first (insert D.base.center D.base.localSet))
  let S : Finset V := insert D.third B
  let H := G.induce (↑S : Set V)
  let t : (S : Set V) := ⟨D.third, by simp [S]⟩
  have ht_unique : ∃! z : (S : Set V), H.Adj t z := by
    let q : (S : Set V) := ⟨D.base.second, by simp [S, B]⟩
    refine ⟨q, ?_, ?_⟩
    · apply SimpleGraph.induce_adj.mpr
      exact (D.third_unique_base D.base.second (by simp)).mpr rfl
    · intro z htz
      apply Subtype.ext
      have htzG : G.Adj D.third (z : V) := SimpleGraph.induce_adj.mp htz
      have hzS : (z : V) = D.third ∨ (z : V) ∈ B := by
        simpa [S] using z.property
      rcases hzS with hzt | hzB
      · exact (G.loopless D.third (hzt ▸ htzG)).elim
      · exact (D.third_unique_base z (by simpa [B] using hzB)).mp htzG
  have hbase : (H.induce ({t}ᶜ : Set (S : Set V))).IsTree := by
    let f : (↥({t}ᶜ : Set (S : Set V))) → (↥(↑B : Set V)) := fun z =>
      ⟨z.val.val, by
        have hzS : z.val.val = D.third ∨ z.val.val ∈ B := by
          simpa [S] using z.val.property
        rcases hzS with hzt | hzB
        · exfalso
          apply z.property
          apply Subtype.ext
          exact hzt
        · exact hzB⟩
    have hf_inj : Function.Injective f := by
      intro z w hzw
      apply Subtype.ext
      apply Subtype.ext
      simpa [f] using congrArg Subtype.val hzw
    have hf_surj : Function.Surjective f := by
      intro z
      let zs : (S : Set V) := ⟨z, by
        change (z : V) ∈ insert D.third B
        exact Finset.mem_insert_of_mem z.property⟩
      have hzst : zs ≠ t := by
        intro h
        apply D.third_not_mem
        have hzthird : (z : V) = D.third := congrArg Subtype.val h
        simpa [B, hzthird] using z.property
      let z' : (↥({t}ᶜ : Set (S : Set V))) := ⟨zs, by
        simpa only [Set.mem_compl_iff, Set.mem_singleton_iff] using hzst⟩
      refine ⟨z', ?_⟩
      apply Subtype.ext
      rfl
    let e : (↥({t}ᶜ : Set (S : Set V))) ≃ (↥(↑B : Set V)) :=
      Equiv.ofBijective f ⟨hf_inj, hf_surj⟩
    let iso : H.induce ({t}ᶜ : Set (S : Set V)) ≃g
        G.induce (↑B : Set V) := {
      toEquiv := e
      map_rel_iff' := by intro z w; rfl
    }
    apply iso.isTree_iff.mpr
    exact D.base.inducedTree
  simpa [H, S, B] using
    isTree_of_induce_compl_singleton_isTree_of_existsUnique_adj
      H t hbase ht_unique

/-- Third-leaf data constructs the abstract three-tail certificate. -/
def ThirdLeafData.toThreeVertexTailSplice
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (D : ThirdLeafData G) : ThreeVertexTailSplice G where
  center := D.base.center
  localSet := D.base.localSet
  first := D.base.first
  second := D.base.second
  third := D.third
  localIndependent := D.base.localIndependent
  localSubset := D.base.localSubset
  localCard := D.base.localCard
  centerMaximal := D.base.centerMaximal
  first_not_mem := D.base.first_not_mem
  second_not_mem := D.base.second_not_mem
  third_not_mem := D.third_not_mem
  inducedTree := thirdLeaf_inducedTree G D

omit [Nonempty V] in
/-- Exact girth-ten/eleven theorem from explicit third-leaf adjacency data. -/
theorem conjecture141_of_girth_ten_or_eleven_of_thirdLeafData
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hgirthLower : 10 ≤ G.girth) (hgirthUpper : G.girth ≤ 11)
    (D : ThirdLeafData G) :
    (G.girth / 2 : ℤ) - 1 +
        ((Finset.univ.sup (indepNeighborsCard G) : ℕ) : ℤ) ≤
      (largestInducedTreeSize G : ℤ) := by
  exact conjecture141_of_girth_ten_or_eleven_of_threeVertexTailSplice
    G hgirthLower hgirthUpper (D.toThreeVertexTailSplice G)

end WrittenOnTheWallII.GraphConjecture141GirthEleven
