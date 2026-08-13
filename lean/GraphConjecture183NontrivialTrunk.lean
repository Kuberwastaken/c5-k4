import GraphConjecture183LocalTrunks

/-!
# WOWII 183: nontrivial bipartite-component trunks

For a bipartite outside component, its entire support is the optimal local
induced-bipartite witness.  Consequently any rooted connected dominating trunk
that omits at least one component vertex has exactly the local budget needed
by the final v0.14 branch interface.  Trees are an immediate specialization.
-/

namespace WrittenOnTheWallII.GraphConjecture183NontrivialTrunk

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183AttachmentSelection
open WrittenOnTheWallII.GraphConjecture183SelectionExistence
open WrittenOnTheWallII.GraphConjecture183LocalTrunks

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The full finite support of an outside component. -/
noncomputable def componentSupportWitness (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) :
    Finset (outsideVertices G x) :=
  c.supp.toFinite.toFinset

omit [DecidableEq V] in
lemma componentSupportWitness_coe (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) :
    (↑(componentSupportWitness G x c) : Set _) = c.supp := by
  classical
  ext y
  simp [componentSupportWitness]

omit [DecidableEq V] in
lemma componentSupportWitness_card (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent) :
    (componentSupportWitness G x c).card = c.supp.ncard := by
  classical
  let W : Set (outsideVertices G x) :=
    ↑(componentSupportWitness G x c)
  calc
    (componentSupportWitness G x c).card =
        W.ncard :=
      (Set.ncard_coe_finset _).symm
    _ = c.supp.ncard := by
      rw [show W = c.supp from componentSupportWitness_coe G x c]

omit [DecidableEq V] in
/-- A bipartite component is witnessed locally by its complete support. -/
theorem componentSupportWitness_isBipartite (G : SimpleGraph V) (x : V)
    (c : (outsideGraph G x).ConnectedComponent)
    (hbip : ((outsideGraph G x).induce c.supp).IsBipartite) :
    ((outsideGraph G x).induce
      (↑(componentSupportWitness G x c) : Set _)).IsBipartite := by
  rw [componentSupportWitness_coe]
  exact hbip

/-- The exact v0.14 local-package proposition for the whole-support witness. -/
def IsComponentSupportLocalPackage (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent)
    (T : Finset (outsideVertices G x)) : Prop :=
  S.attach c ∈ attachmentBranch G x (S.attach c) T ∧
  (G.induce (↑(attachmentBranch G x (S.attach c) T) : Set V)).Connected ∧
  (∀ y, y ∈ c.supp → y.1 ∈ attachmentBranch G x (S.attach c) T ∨
    ∃ z ∈ attachmentBranch G x (S.attach c) T, G.Adj y.1 z) ∧
  (↑(componentSupportWitness G x c) : Set _) ⊆ c.supp ∧
  ((outsideGraph G x).induce
    (↑(componentSupportWitness G x c) : Set _)).IsBipartite ∧
  (attachmentBranch G x (S.attach c) T).card ≤
    (componentSupportWitness G x c).card

/-- Adapter for every nontrivial bipartite component.  The remaining trunk
input is the classical rooted connected-dominating construction, expressed in
the exact ambient form consumed by v0.14; the induced-bipartite witness and its
budget are derived here. -/
theorem bipartiteComponent_rootedTrunk_local_package
    (G : SimpleGraph V) (x : V) (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent) (hc : c ∈ S.C)
    (T : Finset (outsideVertices G x))
    (hroot : S.root c ∈ T)
    (hconn : (G.induce (↑(trunkVertices G x T) : Set V)).Connected)
    (hdom : ∀ y, y ∈ c.supp →
      y ∈ T ∨ ∃ z ∈ T, (outsideGraph G x).Adj y z)
    (hbip : ((outsideGraph G x).induce c.supp).IsBipartite)
    (homit : T.card + 1 ≤ c.supp.ncard) :
    IsComponentSupportLocalPackage G x S c T := by
  apply nontrivial_rootedTrunk_local_package G x S c hc T
    (componentSupportWitness G x c) hroot hconn hdom
  · rw [componentSupportWitness_coe]
  · exact componentSupportWitness_isBipartite G x c hbip
  · rwa [componentSupportWitness_card]

/-- Tree components expose the promised named specialization: their
bipartiteness is supplied by Mathlib and all remaining work is delegated to
the bipartite-component adapter above. -/
theorem treeComponent_rootedTrunk_local_package
    (G : SimpleGraph V) (x : V) (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent) (hc : c ∈ S.C)
    (T : Finset (outsideVertices G x))
    (hroot : S.root c ∈ T)
    (hconn : (G.induce (↑(trunkVertices G x T) : Set V)).Connected)
    (hdom : ∀ y, y ∈ c.supp →
      y ∈ T ∨ ∃ z ∈ T, (outsideGraph G x).Adj y z)
    (htree : ((outsideGraph G x).induce c.supp).IsTree)
    (homit : T.card + 1 ≤ c.supp.ncard) :
    IsComponentSupportLocalPackage G x S c T := by
  exact bipartiteComponent_rootedTrunk_local_package G x S c hc T hroot
    hconn hdom htree.isBipartite homit

/-- A local branch assignment already assembled from singleton packages and
the nontrivial adapters above immediately yields the final certificate.  This
names the end-to-end endpoint for mixed outside-component types. -/
noncomputable def outsideBudgetCertificate_of_mixedLocalPackages
    (G : SimpleGraph V) (x : V) (A : LocalBranchData G x) :
    OutsideBudgetCertificate G x :=
  outsideBudgetCertificateOfLocalBranches G x A

end WrittenOnTheWallII.GraphConjecture183NontrivialTrunk
