import GraphConjecture183TreeComponentFlattening

/-!
# WOWII 183: ambient connectivity of flattened component trunks

Walks in a connected induced subgraph of a connected-component subtype are
mapped through the two forgetful subtype layers into the ambient induced graph.
-/

namespace WrittenOnTheWallII.GraphConjecture183AmbientConnectivity

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183AttachmentSelection
open WrittenOnTheWallII.GraphConjecture183SelectionExistence
open WrittenOnTheWallII.GraphConjecture183NontrivialTrunk
open WrittenOnTheWallII.GraphConjecture183TreeTrunkExistence
open WrittenOnTheWallII.GraphConjecture183RootSensitiveLeaf
open WrittenOnTheWallII.GraphConjecture183TreeComponentFlattening

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The nested-subtype forgetful map is a graph homomorphism from the induced
leaf-deleted component graph to the ambient induced flattened trunk. -/
def leafDeletionToAmbientHom (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) [Fintype c.supp]
    (q : c.supp) :
    (c.toSimpleGraph.induce ({q} : Set c.supp)ᶜ) →g
      G.induce (↑(trunkVertices G x
        (flattenedDeleteLeaf G x c q)) : Set V) where
  toFun z := ⟨z.1.1.1, by
    unfold trunkVertices
    apply Finset.mem_image.mpr
    refine ⟨z.1.1, ?_, rfl⟩
    apply (mem_flattenedDeleteLeaf_iff G x c q z.1.1).mpr
    exact ⟨z.1.property, by
      intro h
      exact z.2 (by simpa [Set.mem_compl_iff, Set.mem_singleton_iff] using
        (show z.1 = q from Subtype.ext h))⟩⟩
  map_rel' := fun hadj => hadj

omit [Fintype V] in
/-- The forgetful homomorphism is injective, so endpoints remain distinct only
as dictated by their original component-subtype values. -/
lemma leafDeletionToAmbientHom_injective (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) [Fintype c.supp]
    (q : c.supp) : Function.Injective (leafDeletionToAmbientHom G x c q) := by
  intro a b h
  have h' := congrArg Subtype.val h
  change a.1.1.1 = b.1.1.1 at h'
  apply Subtype.ext
  apply Subtype.ext
  exact Subtype.ext h'

omit [Fintype V] in
/-- Actual transport theorem: the flattened leaf-deleted component is
connected in the ambient graph. -/
theorem leafDeletionAmbientConnected (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) [Fintype c.supp]
    (q : c.supp) [Fintype (c.toSimpleGraph.neighborSet q)]
    (htree : c.toSimpleGraph.IsTree) (hqdeg : c.toSimpleGraph.degree q = 1) :
    LeafDeletionAmbientConnected G x c q := by
  have hsource := htree.isConnected.induce_compl_singleton_of_degree_eq_one hqdeg
  let f := leafDeletionToAmbientHom G x c q
  unfold LeafDeletionAmbientConnected
  rw [connected_iff]
  constructor
  · intro a b
    obtain ⟨aOut, haOut, haEq⟩ := Finset.mem_image.mp a.property
    have haFacts := (mem_flattenedDeleteLeaf_iff G x c q aOut).mp haOut
    obtain ⟨haSupp, haNe⟩ := haFacts
    obtain ⟨bOut, hbOut, hbEq⟩ := Finset.mem_image.mp b.property
    have hbFacts := (mem_flattenedDeleteLeaf_iff G x c q bOut).mp hbOut
    obtain ⟨hbSupp, hbNe⟩ := hbFacts
    let aa : ↥(({q} : Set c.supp)ᶜ) := ⟨⟨aOut, haSupp⟩, by
      intro h
      exact haNe (congrArg Subtype.val h)⟩
    let bb : ↥(({q} : Set c.supp)ᶜ) := ⟨⟨bOut, hbSupp⟩, by
      intro h
      exact hbNe (congrArg Subtype.val h)⟩
    obtain ⟨p⟩ := hsource.preconnected aa bb
    have hp := p.map f
    have hfa : f aa = a := by
      apply Subtype.ext
      exact haEq
    have hfb : f bb = b := by
      apply Subtype.ext
      exact hbEq
    exact ⟨hfa ▸ hfb ▸ hp⟩
  · obtain ⟨z⟩ := hsource.nonempty
    exact ⟨f z⟩

/-- Full unconditional tree-component local package. -/
theorem exists_treeComponent_local_package
    (G : SimpleGraph V) (x : V) (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent) (hc : c ∈ S.C)
    [Fintype c.supp] [DecidableRel c.toSimpleGraph.Adj]
    (hnontrivial : Nontrivial c.supp) (htree : c.toSimpleGraph.IsTree) :
    ∃ T : Finset (outsideVertices G x),
      IsComponentSupportLocalPackage G x S c T := by
  apply exists_treeComponent_local_package_of_flattening G x S c hc
    hnontrivial htree
  intro q hqdeg
  exact leafDeletionAmbientConnected G x c q htree hqdeg

end WrittenOnTheWallII.GraphConjecture183AmbientConnectivity
