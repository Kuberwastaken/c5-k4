import GraphConjecture183ComponentFold
import GraphConjecture183Attachment

/-!
# WOWII 183: attachment selection and ambient connected domination

For each non-root component of `G-N(x)`, choose one neighbor of `x`, one
attachment root in the component, and a rooted trunk.  This file proves that
the union of those branches with `x` is connected dominating in `G`.
-/

namespace WrittenOnTheWallII.GraphConjecture183AttachmentSelection

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183ComponentFold
open WrittenOnTheWallII.GraphConjecture183Attachment
open WrittenOnTheWallII.GraphConjecture183ComponentAssembly

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Forget the outside-vertex subtype on a finite trunk. -/
def trunkVertices (G : SimpleGraph V) (x : V)
    (T : Finset (↥(outsideVertices G x))) : Finset V :=
  T.image Subtype.val

/-- One attachment vertex together with its rooted trunk. -/
def attachmentBranch (G : SimpleGraph V) (x : V) (p : V)
    (T : Finset (↥(outsideVertices G x))) : Finset V :=
  insert p (trunkVertices G x T)

/-- Exact local choices used by the component construction.

`C` lists every outside component except the isolated component containing
`x`.  Each listed component receives an attachment neighbor `p`, an outside
root `r`, and a trunk `T`.  The trunk domination condition is stated inside
the outside graph; its connectedness is stated after forgetting the subtype,
which is the form needed by the ambient union theorem. -/
structure AttachmentSelectionInput (G : SimpleGraph V) (x : V) where
  C : Finset (outsideGraph G x).ConnectedComponent
  root : (outsideGraph G x).ConnectedComponent → ↥(outsideVertices G x)
  attach : (outsideGraph G x).ConnectedComponent → V
  trunk : (outsideGraph G x).ConnectedComponent →
    Finset (↥(outsideVertices G x))
  covers : ∀ y : ↥(outsideVertices G x), y.1 ≠ x →
    (outsideGraph G x).connectedComponentMk y ∈ C
  root_ne_x : ∀ c ∈ C, (root c).1 ≠ x
  root_supported : ∀ c, root c ∈ c.supp
  root_mem : ∀ c, root c ∈ trunk c
  trunk_supported : ∀ c, (↑(trunk c) : Set _) ⊆ c.supp
  trunk_dominates : ∀ c y, y ∈ c.supp →
    y ∈ trunk c ∨ ∃ z ∈ trunk c, (outsideGraph G x).Adj y z
  trunk_connected : ∀ c,
    (G.induce (↑(trunkVertices G x (trunk c)) : Set V)).Connected
  attach_adj_x : ∀ c, G.Adj x (attach c)
  attach_adj_root : ∀ c, G.Adj (attach c) (root c).1

/-- The ambient candidate: `x` plus all selected attachment/trunk branches. -/
def selectedDominatingSet (G : SimpleGraph V) (x : V)
    (A : AttachmentSelectionInput G x) : Finset V :=
  insert x (A.C.biUnion fun c => attachmentBranch G x (A.attach c) (A.trunk c))

omit [Fintype V] in
lemma root_mem_trunkVertices (G : SimpleGraph V) (x : V)
    (A : AttachmentSelectionInput G x) (c) :
    (A.root c).1 ∈ trunkVertices G x (A.trunk c) := by
  exact Finset.mem_image.mpr ⟨A.root c, A.root_mem c, rfl⟩

omit [Fintype V] in
/-- Each attachment plus rooted trunk is connected in the ambient graph. -/
theorem attachmentBranch_connected (G : SimpleGraph V) (x : V)
    (A : AttachmentSelectionInput G x) (c) :
    (G.induce (↑(attachmentBranch G x (A.attach c) (A.trunk c)) : Set V)).Connected := by
  have hpair := connected_induce_union
    (A.trunk_connected c).preconnected
    (induce_singleton_connected G (A.attach c)).preconnected
    (root_mem_trunkVertices G x A c) (Set.mem_singleton (A.attach c))
    (A.attach_adj_root c).symm
  have heq :
      (↑(attachmentBranch G x (A.attach c) (A.trunk c)) : Set V) =
        (↑(trunkVertices G x (A.trunk c)) : Set V) ∪ {A.attach c} := by
    ext v
    simp [attachmentBranch]
  rw [heq]
  exact hpair

omit [Fintype V] in
/-- **Claw-free attachment injection.** Distinct selected outside components
cannot use the same neighbor of `x`.  Otherwise that common neighbor together
with `x` and the two component roots would induce a claw: the two roots are
nonneighbors of `x`, while an edge between the roots would merge their outside
components.  This is the key cardinality fact for paying one attachment vertex
per component. -/
theorem attach_injective_on_selected_components
    (G : SimpleGraph V) (x : V) (hclaw : IsClawFree G)
    (A : AttachmentSelectionInput G x) {c d}
    (hc : c ∈ A.C) (hd : d ∈ A.C)
    (hattach : A.attach c = A.attach d) : c = d := by
  by_contra hcd
  have hpd : G.Adj (A.attach c) (A.root d).1 := by
    rw [hattach]
    exact A.attach_adj_root d
  have hxu : x ≠ (A.root c).1 := (A.root_ne_x c hc).symm
  have hxv : x ≠ (A.root d).1 := (A.root_ne_x d hd).symm
  have huv : (A.root c).1 ≠ (A.root d).1 := by
    intro huv
    apply hcd
    have huvsub : A.root c = A.root d := Subtype.ext huv
    have hrdc : A.root c ∈ d.supp := by
      rw [huvsub]
      exact A.root_supported d
    exact ConnectedComponent.eq_of_common_vertex (A.root_supported c)
      hrdc
  rcases hclaw (A.attach_adj_x c).symm (A.attach_adj_root c) hpd
      hxu hxv huv with hxr | hxr | hrr
  · exact (A.root c).property hxr
  · exact (A.root d).property hxr
  · apply hcd
    have hcomp := ConnectedComponent.connectedComponentMk_eq_of_adj
      (G := outsideGraph G x) hrr
    have hrc := (ConnectedComponent.mem_supp_iff c (A.root c)).mp
      (A.root_supported c)
    have hrd := (ConnectedComponent.mem_supp_iff d (A.root d)).mp
      (A.root_supported d)
    exact hrc.symm.trans (hcomp.trans hrd)

omit [Fintype V] in
/-- Consequently the selected attachment vertices have exactly one element per
selected outside component. -/
theorem card_image_attach_eq_card_components
    (G : SimpleGraph V) (x : V) (hclaw : IsClawFree G)
    (A : AttachmentSelectionInput G x) :
    (A.C.image A.attach).card = A.C.card := by
  rw [Finset.card_image_iff]
  intro c hc d hd h
  exact attach_injective_on_selected_components G x hclaw A hc hd h

omit [Fintype V] in
/-- The selected set dominates every ambient vertex.  Neighbors of `x` are
paid for by `x`; every other vertex lies in a covered outside component and is
paid for by that component's rooted trunk. -/
theorem selectedDominatingSet_isDominating (G : SimpleGraph V) (x : V)
    (A : AttachmentSelectionInput G x) :
    G.IsDominating (↑(selectedDominatingSet G x A) : Set V) := by
  intro v
  by_cases hvx : v = x
  · exact Or.inl (by simp [selectedDominatingSet, hvx])
  by_cases hxv : G.Adj x v
  · exact Or.inr ⟨x, by simp [selectedDominatingSet], hxv.symm⟩
  let y : outsideVertices G x := ⟨v, hxv⟩
  let c := (outsideGraph G x).connectedComponentMk y
  have hc : c ∈ A.C := A.covers y hvx
  rcases A.trunk_dominates c y (ConnectedComponent.connectedComponentMk_mem) with
    hyT | ⟨z, hzT, hyz⟩
  · exact Or.inl (by
      change v ∈ selectedDominatingSet G x A
      apply Finset.mem_insert.mpr
      right
      apply Finset.mem_biUnion.mpr
      exact ⟨c, hc, Finset.mem_insert_of_mem
        (Finset.mem_image.mpr ⟨y, hyT, rfl⟩)⟩)
  · exact Or.inr ⟨z.1, by
      change z.1 ∈ selectedDominatingSet G x A
      apply Finset.mem_insert.mpr
      right
      apply Finset.mem_biUnion.mpr
      exact ⟨c, hc, Finset.mem_insert_of_mem
        (Finset.mem_image.mpr ⟨z, hzT, rfl⟩)⟩, hyz⟩

omit [Fintype V] in
/-- Finite induction glues every connected attachment branch to the already
assembled set through the edge from `x` to its chosen attachment. -/
lemma selectedDominatingSet_connected_aux (G : SimpleGraph V) (x : V)
    (A : AttachmentSelectionInput G x)
    (C : Finset (outsideGraph G x).ConnectedComponent) :
    (G.induce (↑(insert x
      (C.biUnion fun c => attachmentBranch G x (A.attach c) (A.trunk c))) : Set V)).Connected := by
  classical
  induction C using Finset.induction_on with
  | empty =>
      letI : Subsingleton (↥(↑({x} : Finset V) : Set V)) :=
        ⟨fun a b => Subtype.ext
          ((Finset.mem_singleton.mp a.property).trans
            (Finset.mem_singleton.mp b.property).symm)⟩
      simp only [Finset.biUnion_empty, Finset.insert_empty]
      rw [connected_iff]
      exact ⟨Preconnected.of_subsingleton, ⟨⟨x, by simp⟩⟩⟩
  | @insert c C hc ih =>
      have hglue := connected_induce_union ih.preconnected
        (attachmentBranch_connected G x A c).preconnected
        (show x ∈ (↑(insert x
          (C.biUnion fun d => attachmentBranch G x (A.attach d) (A.trunk d))) : Set V) by simp)
        (show A.attach c ∈
          (↑(attachmentBranch G x (A.attach c) (A.trunk c)) : Set V) by
            simp [attachmentBranch])
        (A.attach_adj_x c)
      have heq :
          (↑(insert x ((insert c C).biUnion fun d =>
            attachmentBranch G x (A.attach d) (A.trunk d))) : Set V) =
          (↑(insert x (C.biUnion fun d =>
            attachmentBranch G x (A.attach d) (A.trunk d))) : Set V) ∪
          (↑(attachmentBranch G x (A.attach c) (A.trunk c)) : Set V) := by
        ext v
        simp [Finset.biUnion_insert]
        aesop
      rw [heq]
      exact hglue

omit [Fintype V] in
/-- The component selections and local rooted trunks assemble to an ambient
connected dominating set.  No global connectivity premise is assumed. -/
theorem selectedDominatingSet_isConnectedDominating
    (G : SimpleGraph V) (x : V) (A : AttachmentSelectionInput G x) :
    G.IsConnectedDominating (↑(selectedDominatingSet G x A) : Set V) := by
  exact ⟨selectedDominatingSet_isDominating G x A,
    selectedDominatingSet_connected_aux G x A A.C⟩

/-- The final local data needed to connect attachment selection to the v0.10
component fold.  All graph-global domination and connectivity are derived,
not assumed; only the componentwise bipartite witnesses and their numerical
budget remain as inputs. -/
structure AttachmentBudgetInput (G : SimpleGraph V) (x : V) where
  selection : AttachmentSelectionInput G x
  B : (outsideGraph G x).ConnectedComponent →
    Finset (↥(outsideVertices G x))
  supported : ∀ c, (↑(B c) : Set _) ⊆ c.supp
  bipartite : ∀ c,
    ((outsideGraph G x).induce (↑(B c) : Set _)).IsBipartite
  card_le_sum : (selectedDominatingSet G x selection).card ≤
    ∑ c ∈ selection.C, (B c).card

/-- Attachment choices plus their local witness budget instantiate exactly the
generic component-fold interface. -/
def componentFoldInput_of_attachmentBudget (G : SimpleGraph V) (x : V)
    (A : AttachmentBudgetInput G x) : ComponentFoldInput G x where
  D := selectedDominatingSet G x A.selection
  C := A.selection.C
  B := A.B
  supported := A.supported
  bipartite := A.bipartite
  dominating := selectedDominatingSet_isConnectedDominating G x A.selection
  card_le_sum := A.card_le_sum

/-- End-to-end certificate constructor after the now-formalized attachment and
component folds. -/
def outsideBudgetCertificate_of_attachmentBudget (G : SimpleGraph V) (x : V)
    (A : AttachmentBudgetInput G x) : OutsideBudgetCertificate G x :=
  outsideBudgetCertificate_of_componentFoldInput G x
    (componentFoldInput_of_attachmentBudget G x A)

end WrittenOnTheWallII.GraphConjecture183AttachmentSelection
