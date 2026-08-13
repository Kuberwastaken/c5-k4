import GraphConjecture183NontrivialTrunk

/-!
# WOWII 183: rooted trunks in tree components

Deleting a leaf distinct from the prescribed root gives the desired rooted
connected dominating trunk.  This file verifies the full construction and
feeds it into the named tree-component adapter.
-/

namespace WrittenOnTheWallII.GraphConjecture183TreeTrunkExistence

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183AttachmentSelection
open WrittenOnTheWallII.GraphConjecture183SelectionExistence
open WrittenOnTheWallII.GraphConjecture183NontrivialTrunk

universe u

variable {W : Type u} [Fintype W] [DecidableEq W]

/-- Delete one specified vertex from a finite graph. -/
def deleteVertexFinset (q : W) : Finset W := Finset.univ.erase q

lemma mem_deleteVertexFinset_iff {q v : W} :
    v ∈ deleteVertexFinset q ↔ v ≠ q := by
  simp [deleteVertexFinset]

/-- A leaf-deleted set dominates a connected nontrivial graph. -/
theorem deleteLeaf_isDominating (H : SimpleGraph W)
    {q : W} [Fintype (H.neighborSet q)] (hdeg : H.degree q = 1) :
    H.IsDominating (↑(deleteVertexFinset q) : Set W) := by
  intro v
  by_cases hvq : v = q
  · subst v
    obtain ⟨z, hqz, _⟩ := degree_eq_one_iff_existsUnique_adj.mp hdeg
    exact Or.inr ⟨z, by
      change z ∈ deleteVertexFinset q
      rw [mem_deleteVertexFinset_iff]
      exact hqz.ne.symm, hqz⟩
  · exact Or.inl (mem_deleteVertexFinset_iff.mpr hvq)

/-- Deleting a leaf gives a connected dominating set. -/
theorem deleteLeaf_isConnectedDominating (H : SimpleGraph W)
    (hconn : H.Connected) {q : W} [Fintype (H.neighborSet q)]
    (hdeg : H.degree q = 1) :
    H.IsConnectedDominating (↑(deleteVertexFinset q) : Set W) := by
  constructor
  · exact deleteLeaf_isDominating H hdeg
  · have hc := hconn.induce_compl_singleton_of_degree_eq_one hdeg
    have heq : (↑(deleteVertexFinset q) : Set W) = ({q} : Set W)ᶜ := by
      ext v
      simp [deleteVertexFinset]
    rw [heq]
    exact hc

/-- The deleted leaf pays exactly the one-unit omission budget. -/
lemma card_deleteVertexFinset_add_one [Nonempty W] (q : W) :
    (deleteVertexFinset q).card + 1 = Fintype.card W := by
  simp [deleteVertexFinset, Nat.sub_add_cancel (Fintype.card_pos : 1 ≤ Fintype.card W)]

/-- Rooted version: a leaf distinct from the prescribed root may be deleted. -/
theorem rooted_deleteLeaf_trunk (H : SimpleGraph W) (hconn : H.Connected)
    (r q : W) [Fintype (H.neighborSet q)]
    (hrq : r ≠ q) (hdeg : H.degree q = 1) :
    r ∈ deleteVertexFinset q ∧
    H.IsConnectedDominating (↑(deleteVertexFinset q) : Set W) ∧
    (deleteVertexFinset q).card + 1 = Fintype.card W := by
  letI : Nonempty W := ⟨r⟩
  exact ⟨mem_deleteVertexFinset_iff.mpr hrq,
    deleteLeaf_isConnectedDominating H hconn hdeg,
    card_deleteVertexFinset_add_one q⟩

universe v
variable {V : Type v} [Fintype V] [DecidableEq V]

/-- Tree-component endpoint with an explicit non-root leaf.  The deleted-leaf
trunk is built on the component subtype; the remaining hypotheses are only the
routine flattening facts connecting that subtype trunk to the ambient graph.
Those facts are stated explicitly rather than hidden in an axiom. -/
theorem treeComponent_package_of_leaf
    (G : SimpleGraph V) (x : V) (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent) (hc : c ∈ S.C)
    [Fintype c.supp]
    (q : c.supp) (hqroot : (S.root c : outsideVertices G x) ≠ q.1)
    [Fintype (c.toSimpleGraph.neighborSet q)]
    (hqdeg : c.toSimpleGraph.degree q = 1)
    (T : Finset (outsideVertices G x))
    (hTcard : T.card = (deleteVertexFinset q).card)
    (hroot_transport :
      (⟨S.root c, S.root_supported c hc⟩ : c.supp) ∈ deleteVertexFinset q →
        S.root c ∈ T)
    (hconn : (G.induce (↑(trunkVertices G x T) : Set V)).Connected)
    (hdom : ∀ y, y ∈ c.supp →
      y ∈ T ∨ ∃ z ∈ T, (outsideGraph G x).Adj y z)
    (htree : ((outsideGraph G x).induce c.supp).IsTree) :
    IsComponentSupportLocalPackage G x S c T := by
  letI : Nonempty c.supp := ⟨q⟩
  let rootC : c.supp := ⟨S.root c, S.root_supported c hc⟩
  have hrootq : rootC ≠ q := by
    intro h
    exact hqroot (congrArg (fun z : c.supp => (z.1 : outsideVertices G x)) h)
  have hleaf := rooted_deleteLeaf_trunk c.toSimpleGraph htree.isConnected
    rootC q hrootq hqdeg
  have hroot : S.root c ∈ T := hroot_transport hleaf.1
  have hcomponentCard : Fintype.card c.supp = c.supp.ncard := by
    rw [← Nat.card_coe_set_eq, Nat.card_eq_fintype_card]
  have homit0 := card_deleteVertexFinset_add_one q
  have homit : T.card + 1 ≤ c.supp.ncard := by
    rw [hTcard, homit0, hcomponentCard]
  exact treeComponent_rootedTrunk_local_package G x S c hc T hroot hconn
    hdom htree homit

end WrittenOnTheWallII.GraphConjecture183TreeTrunkExistence
