import GraphConjecture40BlockTreeRecurrence

/-!
# WOWII 40: ambient/subtype state bridges

The one-vertex separator states were defined using ambient finsets constrained
to a side. This file identifies them with the ordinary induced-forest states
of the recursively typed induced side graph.
-/

namespace WrittenOnTheWallII.GraphConjecture40InducedStateBridge

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
open WrittenOnTheWallII.GraphConjecture40SharedCutUnion

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Inducing first on `A` and then on a subtype finset is isomorphic to
inducing the ambient graph on the image of that finset. -/
def induceSubtypeFinsetIso (G : SimpleGraph V) (A : Finset V)
    (T : Finset ↥(↑A : Set V)) :
    (G.induce (↑A : Set V)).induce (↑T : Set ↥(↑A : Set V)) ≃g
      G.induce (↑(T.map (Function.Embedding.subtype _)) : Set V) where
  toEquiv :=
    { toFun := fun x => ⟨x.1.1, mem_map.mpr ⟨x.1, x.2, rfl⟩⟩
      invFun := fun x =>
        ⟨⟨x.1, (T.map_subtype_subset x.2)⟩, by
          rcases mem_map.mp x.2 with ⟨z, hz, hzx⟩
          have heq : z = ⟨x.1, T.map_subtype_subset x.2⟩ := by
            apply Subtype.ext
            simpa using hzx
          simpa [← heq] using hz⟩
      left_inv := fun x => by exact Subtype.ext (Subtype.ext rfl)
      right_inv := fun x => by exact Subtype.ext rfl }
  map_rel_iff' := by
    intro x y
    rfl

omit [Fintype V] [DecidableEq V] in
/-- Ambient acyclicity and recursively typed acyclicity agree for a subtype
finset and its ambient image. -/
lemma induceSubtypeFinset_isAcyclic_iff
    (G : SimpleGraph V) (A : Finset V) (T : Finset ↥(↑A : Set V)) :
    ((G.induce (↑A : Set V)).induce (↑T : Set ↥(↑A : Set V))).IsAcyclic ↔
      (G.induce (↑(T.map (Function.Embedding.subtype _)) : Set V)).IsAcyclic :=
  (induceSubtypeFinsetIso G A T).isAcyclic_iff

omit [Fintype V] in
/-- A constrained ambient maximum induced forest is exactly the ordinary
maximum induced forest of the induced side graph. -/
theorem forestOrderWithin_eq_induce_largestInducedForestSize
    (G : SimpleGraph V) (A : Finset V) :
    forestOrderWithin G A =
      (G.induce (↑A : Set V)).largestInducedForestSize := by
  apply le_antisymm
  · obtain ⟨S, hSA, hS, hcard⟩ :=
      exists_forestOrderWithin_witness G A
    let T : Finset ↥(↑A : Set V) := S.subtype (fun x => x ∈ A)
    have hmap : T.map (Function.Embedding.subtype _) = S := by
      exact subtype_map_of_mem hSA
    have hTacyc :
        ((G.induce (↑A : Set V)).induce
          (↑T : Set ↥(↑A : Set V))).IsAcyclic := by
      apply (induceSubtypeFinset_isAcyclic_iff G A T).mpr
      rw [hmap]
      exact hS
    have hbound := GraphConjecture40Baseline.card_le_largestInducedForestSize
      (G.induce (↑A : Set V)) T hTacyc
    have hcardT : T.card = S.card := by
      simpa using congrArg Finset.card hmap
    omega
  · obtain ⟨T, hTacyc, hTcard⟩ :=
      GraphConjecture40CactusFeedbackUnit.exists_largestInducedForestSize_witness
        (G.induce (↑A : Set V))
    let S : Finset V := T.map (Function.Embedding.subtype _)
    have hSA : S ⊆ A := by
      intro x hx
      exact T.property_of_mem_map_subtype hx
    have hSacyc : (G.induce (↑S : Set V)).IsAcyclic := by
      apply (induceSubtypeFinset_isAcyclic_iff G A T).mp
      exact hTacyc
    have hbound := card_le_forestOrderWithin G A S hSA hSacyc
    have hcardS : S.card = T.card := by simp [S]
    omega

omit [Fintype V] in
/-- The constrained ambient include-cut state is exactly the ordinary
include-cut state of the induced side graph at the subtype cut vertex. -/
theorem forestOrderWithinIncluding_eq_induce_forestOrderIncluding
    (G : SimpleGraph V) (A : Finset V) (c : V) (hcA : c ∈ A) :
    forestOrderWithinIncluding G A c =
      GraphConjecture40CutVertexSum.forestOrderIncluding
        (G.induce (↑A : Set V)) ⟨c, hcA⟩ := by
  apply le_antisymm
  · obtain ⟨S, hSA, hS, hcS, hcard⟩ :=
      exists_forestOrderWithinIncluding_witness G A c hcA
    let T : Finset ↥(↑A : Set V) := S.subtype (fun x => x ∈ A)
    have hmap : T.map (Function.Embedding.subtype _) = S := by
      exact subtype_map_of_mem hSA
    have hTacyc :
        ((G.induce (↑A : Set V)).induce
          (↑T : Set ↥(↑A : Set V))).IsAcyclic := by
      apply (induceSubtypeFinset_isAcyclic_iff G A T).mpr
      rw [hmap]
      exact hS
    have hcT : (⟨c, hcA⟩ : ↥(↑A : Set V)) ∈ T := by
      exact mem_subtype.mpr hcS
    have hbound := GraphConjecture40CutVertexSum.card_le_forestOrderIncluding
      (G.induce (↑A : Set V)) ⟨c, hcA⟩ T hTacyc hcT
    have hcardT : T.card = S.card := by
      simpa using congrArg Finset.card hmap
    omega
  · obtain ⟨T, hTacyc, hcT, hTcard⟩ :=
      GraphConjecture40CutVertexSum.exists_forestOrderIncluding_witness
        (G.induce (↑A : Set V)) ⟨c, hcA⟩
    let S : Finset V := T.map (Function.Embedding.subtype _)
    have hSA : S ⊆ A := by
      intro x hx
      exact T.property_of_mem_map_subtype hx
    have hSacyc : (G.induce (↑S : Set V)).IsAcyclic := by
      apply (induceSubtypeFinset_isAcyclic_iff G A T).mp
      exact hTacyc
    have hcS : c ∈ S := by
      exact mem_map.mpr ⟨⟨c, hcA⟩, hcT, rfl⟩
    have hbound := card_le_forestOrderWithinIncluding G A c S
      hSA hSacyc hcS
    have hcardS : S.card = T.card := by simp [S]
    omega

open WrittenOnTheWallII.GraphConjecture40BlockTreeRecurrence

/-- Fully subtype-typed form of the local block-tree rank. Each term is now
an invariant of a recursively smaller induced side graph. -/
theorem blockTreeForestRank_eq_max_induced_side_states
    {G : SimpleGraph V} (D : OneVertexSeparation G) :
    blockTreeForestRank D =
      max
        (GraphConjecture40CutVertexSum.forestOrderIncluding
            (G.induce (↑D.left : Set V)) ⟨D.cut, D.cut_mem_left⟩ +
          GraphConjecture40CutVertexSum.forestOrderIncluding
            (G.induce (↑D.right : Set V)) ⟨D.cut, D.cut_mem_right⟩)
        ((G.induce (↑(D.left.erase D.cut) : Set V)).largestInducedForestSize +
          (G.induce (↑(D.right.erase D.cut) : Set V)).largestInducedForestSize +
          1) := by
  unfold blockTreeForestRank includeStateSum excludeStateSum
  rw [forestOrderWithinIncluding_eq_induce_forestOrderIncluding
      G D.left D.cut D.cut_mem_left,
    forestOrderWithinIncluding_eq_induce_forestOrderIncluding
      G D.right D.cut D.cut_mem_right,
    forestOrderWithin_eq_induce_largestInducedForestSize
      G (D.left.erase D.cut),
    forestOrderWithin_eq_induce_largestInducedForestSize
      G (D.right.erase D.cut)]

end WrittenOnTheWallII.GraphConjecture40InducedStateBridge
