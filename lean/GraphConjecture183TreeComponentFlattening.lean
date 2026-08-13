import GraphConjecture183RootSensitiveLeaf

/-!
# WOWII 183: typed tree-component flattening boundary

This file maps the leaf-deleted component-subtype finset to outside vertices
and proves the exact membership/cardinality/domination facts.  Ambient
connectedness is isolated as the sole remaining coercion lemma.
-/

namespace WrittenOnTheWallII.GraphConjecture183TreeComponentFlattening

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183AttachmentSelection
open WrittenOnTheWallII.GraphConjecture183SelectionExistence
open WrittenOnTheWallII.GraphConjecture183NontrivialTrunk
open WrittenOnTheWallII.GraphConjecture183TreeTrunkExistence
open WrittenOnTheWallII.GraphConjecture183RootSensitiveLeaf

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Map `c-{q}` from the component subtype to outside vertices. -/
def flattenedDeleteLeaf (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) [Fintype c.supp]
    (q : c.supp) : Finset (outsideVertices G x) :=
  (deleteVertexFinset q).image Subtype.val

omit [Fintype V] in
lemma mem_flattenedDeleteLeaf_iff (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) [Fintype c.supp]
    (q : c.supp) (y : outsideVertices G x) :
    y ∈ flattenedDeleteLeaf G x c q ↔ y ∈ c.supp ∧ y ≠ q.1 := by
  unfold flattenedDeleteLeaf
  constructor
  · intro hy
    obtain ⟨z, hz, hzy⟩ := Finset.mem_image.mp hy
    rw [← hzy]
    exact ⟨z.property, fun h => (mem_deleteVertexFinset_iff.mp hz)
      (Subtype.ext h)⟩
  · rintro ⟨hyc, hyq⟩
    apply Finset.mem_image.mpr
    refine ⟨⟨y, hyc⟩, mem_deleteVertexFinset_iff.mpr ?_, rfl⟩
    intro h
    exact hyq (congrArg Subtype.val h)

omit [Fintype V] in
lemma card_flattenedDeleteLeaf (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) [Fintype c.supp]
    (q : c.supp) :
    (flattenedDeleteLeaf G x c q).card = (deleteVertexFinset q).card := by
  unfold flattenedDeleteLeaf
  exact Finset.card_image_of_injective _ Subtype.val_injective

omit [Fintype V] in
/-- The flattened leaf-deleted trunk dominates its outside component. -/
theorem flattenedDeleteLeaf_dominates_component (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) [Fintype c.supp]
    (q : c.supp) [Fintype (c.toSimpleGraph.neighborSet q)]
    (hqdeg : c.toSimpleGraph.degree q = 1) :
    ∀ y, y ∈ c.supp →
      y ∈ flattenedDeleteLeaf G x c q ∨
        ∃ z ∈ flattenedDeleteLeaf G x c q, (outsideGraph G x).Adj y z := by
  intro y hyc
  let yC : c.supp := ⟨y, hyc⟩
  rcases deleteLeaf_isDominating c.toSimpleGraph hqdeg yC with hy | ⟨z, hz, hyz⟩
  · left
    exact (mem_flattenedDeleteLeaf_iff G x c q y).mpr
      ⟨hyc, fun h => (mem_deleteVertexFinset_iff.mp hy) (Subtype.ext h)⟩
  · right
    refine ⟨z.1, (mem_flattenedDeleteLeaf_iff G x c q z.1).mpr
      ⟨z.property, ?_⟩, hyz⟩
    intro hzq
    exact (mem_deleteVertexFinset_iff.mp hz) (Subtype.ext hzq)

/-- The only remaining transport field: connectedness of the subtype
leaf-deletion after both subtype forgetful maps into the ambient graph. -/
def LeafDeletionAmbientConnected (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) [Fintype c.supp]
    (q : c.supp) : Prop :=
  (G.induce (↑(trunkVertices G x
    (flattenedDeleteLeaf G x c q)) : Set V)).Connected

/-- Strongest typed tree-component adapter: leaf choice, cardinality, root
membership, and domination are all derived; only the named ambient-connectivity
transport fact remains explicit. -/
theorem exists_treeComponent_local_package_of_flattening
    (G : SimpleGraph V) (x : V) (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent) (hc : c ∈ S.C)
    [Fintype c.supp] [DecidableRel c.toSimpleGraph.Adj]
    (hnontrivial : Nontrivial c.supp) (htree : c.toSimpleGraph.IsTree)
    (hflatten : ∀ q : c.supp, c.toSimpleGraph.degree q = 1 →
      LeafDeletionAmbientConnected G x c q) :
    ∃ T : Finset (outsideVertices G x),
      IsComponentSupportLocalPackage G x S c T := by
  letI : Nontrivial c.supp := hnontrivial
  let rootC : c.supp := ⟨S.root c, S.root_supported c hc⟩
  obtain ⟨q, hqroot, hqdeg⟩ := IsTree.exists_degree_one_ne c.toSimpleGraph htree rootC
  let T := flattenedDeleteLeaf G x c q
  refine ⟨T, treeComponent_package_of_leaf G x S c hc q ?_ hqdeg T ?_ ?_ ?_ ?_ htree⟩
  · intro h
    exact hqroot (Subtype.ext h.symm)
  · exact card_flattenedDeleteLeaf G x c q
  · intro _
    exact (mem_flattenedDeleteLeaf_iff G x c q (S.root c)).mpr
      ⟨S.root_supported c hc, fun h => hqroot (Subtype.ext h.symm)⟩
  · exact hflatten q hqdeg
  · exact flattenedDeleteLeaf_dominates_component G x c q hqdeg

end WrittenOnTheWallII.GraphConjecture183TreeComponentFlattening
