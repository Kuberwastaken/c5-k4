import GraphConjecture183CorrectedFold

/-!
# WOWII 183: local trunks, including singleton outside components

A selected singleton component cannot afford both its vertex and its attachment
from its one-vertex bipartite budget.  The correct branch keeps only the
attachment, which dominates the omitted singleton.  This file exposes the
flexible local interface that handles that case and proves the final outside
certificate from purely component-local facts.
-/

namespace WrittenOnTheWallII.GraphConjecture183LocalTrunks

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183ComponentFold
open WrittenOnTheWallII.GraphConjecture183AttachmentSelection
open WrittenOnTheWallII.GraphConjecture183SelectionExistence
open WrittenOnTheWallII.GraphConjecture183CorrectedFold
open WrittenOnTheWallII.GraphConjecture183ComponentAssembly

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Flexible local data.  `branch c` is the ambient set joined to `x`; it may
be a rooted trunk plus attachment for a nontrivial component, or just the
attachment for a singleton component. -/
structure LocalBranchData (G : SimpleGraph V) (x : V) where
  selection : SelectedAttachmentData G x
  branch : (outsideGraph G x).ConnectedComponent → Finset V
  B : (outsideGraph G x).ConnectedComponent →
    Finset (outsideVertices G x)
  attach_mem : ∀ c ∈ selection.C, selection.attach c ∈ branch c
  branch_connected : ∀ c ∈ selection.C,
    (G.induce (↑(branch c) : Set V)).Connected
  local_dominates : ∀ c ∈ selection.C, ∀ y, y ∈ c.supp →
    y.1 ∈ branch c ∨ ∃ z ∈ branch c, G.Adj y.1 z
  witness_supported : ∀ c, (↑(B c) : Set _) ⊆ c.supp
  witness_bipartite : ∀ c,
    ((outsideGraph G x).induce (↑(B c) : Set _)).IsBipartite
  local_budget : ∀ c ∈ selection.C, (branch c).card ≤ (B c).card
  root_budget : 1 ≤ (B (rootOutsideComponent G x)).card

/-- `x` and all flexible local branches. -/
def localSelectedSet (G : SimpleGraph V) (x : V)
    (A : LocalBranchData G x) : Finset V :=
  insert x (A.selection.C.biUnion A.branch)

omit [Fintype V] in
theorem localSelectedSet_isDominating (G : SimpleGraph V) (x : V)
    (A : LocalBranchData G x) :
    G.IsDominating (↑(localSelectedSet G x A) : Set V) := by
  intro v
  by_cases hvx : v = x
  · exact Or.inl (by simp [localSelectedSet, hvx])
  by_cases hxv : G.Adj x v
  · exact Or.inr ⟨x, by simp [localSelectedSet], hxv.symm⟩
  let y : outsideVertices G x := ⟨v, hxv⟩
  let c := (outsideGraph G x).connectedComponentMk y
  have hc : c ∈ A.selection.C := A.selection.covers y hvx
  rcases A.local_dominates c hc y ConnectedComponent.connectedComponentMk_mem with
    hy | ⟨z, hz, hyz⟩
  · exact Or.inl (by
      change v ∈ localSelectedSet G x A
      simp only [localSelectedSet, mem_insert, mem_biUnion]
      exact Or.inr ⟨c, hc, hy⟩)
  · exact Or.inr ⟨z, by
      change z ∈ localSelectedSet G x A
      simp only [localSelectedSet, mem_insert, mem_biUnion]
      exact Or.inr ⟨c, hc, hz⟩, hyz⟩

omit [Fintype V] in
lemma localSelectedSet_connected_aux (G : SimpleGraph V) (x : V)
    (A : LocalBranchData G x)
    (C : Finset (outsideGraph G x).ConnectedComponent)
    (hC : C ⊆ A.selection.C) :
    (G.induce (↑(insert x (C.biUnion A.branch)) : Set V)).Connected := by
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
      have hcsel : c ∈ A.selection.C := hC (Finset.mem_insert_self c C)
      have hCsel : C ⊆ A.selection.C :=
        fun d hd => hC (Finset.mem_insert_of_mem hd)
      have hglue := connected_induce_union (ih hCsel).preconnected
        (A.branch_connected c hcsel).preconnected
        (show x ∈ (↑(insert x (C.biUnion A.branch)) : Set V) by simp)
        (A.attach_mem c hcsel) (A.selection.attach_adj_x c hcsel)
      have heq :
          (↑(insert x ((insert c C).biUnion A.branch)) : Set V) =
          (↑(insert x (C.biUnion A.branch)) : Set V) ∪
            (↑(A.branch c) : Set V) := by
        ext v
        simp [Finset.biUnion_insert]
        aesop
      rw [heq]
      exact hglue

omit [Fintype V] in
theorem localSelectedSet_isConnectedDominating (G : SimpleGraph V) (x : V)
    (A : LocalBranchData G x) :
    G.IsConnectedDominating (↑(localSelectedSet G x A) : Set V) :=
  ⟨localSelectedSet_isDominating G x A,
    localSelectedSet_connected_aux G x A A.selection.C (by rfl)⟩

omit [Fintype V] in
theorem localSelectedSet_card_le (G : SimpleGraph V) (x : V)
    (A : LocalBranchData G x) :
    (localSelectedSet G x A).card ≤ 1 + ∑ c ∈ A.selection.C, (A.branch c).card := by
  calc
    (localSelectedSet G x A).card ≤ 1 + (A.selection.C.biUnion A.branch).card := by
      unfold localSelectedSet
      simpa [Nat.add_comm] using
        (Finset.card_insert_le x (A.selection.C.biUnion A.branch))
    _ ≤ 1 + ∑ c ∈ A.selection.C, (A.branch c).card :=
      Nat.add_le_add_left Finset.card_biUnion_le 1

omit [Fintype V] in
/-- All aggregate accounting follows from the local branch budgets and the
one-unit root witness. -/
theorem localSelectedSet_card_le_witness_sum (G : SimpleGraph V) (x : V)
    (A : LocalBranchData G x) :
    (localSelectedSet G x A).card ≤
      ∑ c ∈ correctedWitnessComponents G x A.selection, (A.B c).card := by
  classical
  have hlocal : ∑ c ∈ A.selection.C, (A.branch c).card ≤
      ∑ c ∈ A.selection.C, (A.B c).card :=
    sum_le_sum fun c hc => A.local_budget c hc
  have hroot := A.root_budget
  unfold correctedWitnessComponents
  rw [Finset.sum_insert A.selection.excludes_root]
  exact (localSelectedSet_card_le G x A).trans (by omega)

/-- Final component-fold input from the flexible local interface. -/
noncomputable def componentFoldInputOfLocalBranches (G : SimpleGraph V) (x : V)
    (A : LocalBranchData G x) : ComponentFoldInput G x where
  D := localSelectedSet G x A
  C := correctedWitnessComponents G x A.selection
  B := A.B
  supported := A.witness_supported
  bipartite := A.witness_bipartite
  dominating := localSelectedSet_isConnectedDominating G x A
  card_le_sum := localSelectedSet_card_le_witness_sum G x A

/-- Final outside-budget certificate under component-local hypotheses only. -/
noncomputable def outsideBudgetCertificateOfLocalBranches (G : SimpleGraph V)
    (x : V) (A : LocalBranchData G x) : OutsideBudgetCertificate G x :=
  outsideBudgetCertificate_of_componentFoldInput G x
    (componentFoldInputOfLocalBranches G x A)

/-- Exact singleton-component construction: retain only the attachment in the
ambient dominating branch and retain only the singleton root in the bipartite
witness.  Both sides cost one. -/
def singletonBranch (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent) : Finset V :=
  {S.attach c}

def singletonWitness (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent) :
    Finset (outsideVertices G x) :=
  {S.root c}

omit [Fintype V] in
theorem singleton_local_package (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x) (c) (hc : c ∈ S.C)
    (hsingle : c.supp = {S.root c}) :
    S.attach c ∈ singletonBranch G x S c ∧
    (G.induce (↑(singletonBranch G x S c) : Set V)).Connected ∧
    (∀ y, y ∈ c.supp → y.1 ∈ singletonBranch G x S c ∨
      ∃ z ∈ singletonBranch G x S c, G.Adj y.1 z) ∧
    (↑(singletonWitness G x S c) : Set _) ⊆ c.supp ∧
    ((outsideGraph G x).induce
      (↑(singletonWitness G x S c) : Set _)).IsBipartite ∧
    (singletonBranch G x S c).card ≤ (singletonWitness G x S c).card := by
  constructor
  · simp [singletonBranch]
  constructor
  · letI : Subsingleton (↥(↑({S.attach c} : Finset V) : Set V)) :=
      ⟨fun a b => Subtype.ext
        ((Finset.mem_singleton.mp a.property).trans
          (Finset.mem_singleton.mp b.property).symm)⟩
    have hconn : (G.induce (↑({S.attach c} : Finset V) : Set V)).Connected := by
      rw [connected_iff]
      exact ⟨Preconnected.of_subsingleton, ⟨⟨S.attach c, by simp⟩⟩⟩
    simpa [singletonBranch] using hconn
  constructor
  · intro y hy
    right
    refine ⟨S.attach c, by simp [singletonBranch], ?_⟩
    have hyr : y = S.root c := by
      have : y ∈ ({S.root c} : Set _) := hsingle ▸ hy
      exact this
    rw [hyr]
    exact (S.attach_adj_root c hc).symm
  constructor
  · intro y hy
    have hyr : y = S.root c := by simpa [singletonWitness] using hy
    rw [hyr]
    exact hsingle.symm ▸ Set.mem_singleton (S.root c)
  constructor
  · rw [induce_isBipartite_iff_exists_coloring]
    refine ⟨fun _ => 0, ?_⟩
    intro a ha b hb hab
    have hab' : a = b := by
      have ha' : a = S.root c := by simpa [singletonWitness] using ha
      have hb' : b = S.root c := by simpa [singletonWitness] using hb
      exact ha'.trans hb'.symm
    exact (hab.ne hab').elim
  · simp [singletonBranch, singletonWitness]

omit [Fintype V] in
/-- A corrected rooted trunk with its `+1` witness budget produces exactly one
nontrivial flexible branch package.  This is the direct adapter from
`NontrivialRootedTrunkPrinciple` output to the final local interface. -/
theorem nontrivial_rootedTrunk_local_package (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x) (c) (hc : c ∈ S.C)
    (T B : Finset (outsideVertices G x))
    (hroot : S.root c ∈ T)
    (hconn : (G.induce (↑(trunkVertices G x T) : Set V)).Connected)
    (hdom : ∀ y, y ∈ c.supp →
      y ∈ T ∨ ∃ z ∈ T, (outsideGraph G x).Adj y z)
    (hBsub : (↑B : Set _) ⊆ c.supp)
    (hBbip : ((outsideGraph G x).induce (↑B : Set _)).IsBipartite)
    (hbudget : T.card + 1 ≤ B.card) :
    S.attach c ∈ attachmentBranch G x (S.attach c) T ∧
    (G.induce (↑(attachmentBranch G x (S.attach c) T) : Set V)).Connected ∧
    (∀ y, y ∈ c.supp → y.1 ∈ attachmentBranch G x (S.attach c) T ∨
      ∃ z ∈ attachmentBranch G x (S.attach c) T, G.Adj y.1 z) ∧
    (↑B : Set _) ⊆ c.supp ∧
    ((outsideGraph G x).induce (↑B : Set _)).IsBipartite ∧
    (attachmentBranch G x (S.attach c) T).card ≤ B.card := by
  constructor
  · simp [attachmentBranch]
  constructor
  · have hpair := connected_induce_union hconn.preconnected
      (induce_singleton_connected G (S.attach c)).preconnected
      (show (S.root c).1 ∈ (↑(trunkVertices G x T) : Set V) by
        exact Finset.mem_image.mpr ⟨S.root c, hroot, rfl⟩)
      (Set.mem_singleton (S.attach c)) (S.attach_adj_root c hc).symm
    have heq :
        (↑(attachmentBranch G x (S.attach c) T) : Set V) =
          (↑(trunkVertices G x T) : Set V) ∪ {S.attach c} := by
      ext v
      simp [attachmentBranch]
    rw [heq]
    exact hpair
  constructor
  · intro y hy
    rcases hdom y hy with hyT | ⟨z, hzT, hyz⟩
    · left
      exact Finset.mem_insert_of_mem (Finset.mem_image.mpr ⟨y, hyT, rfl⟩)
    · right
      exact ⟨z.1, Finset.mem_insert_of_mem
        (Finset.mem_image.mpr ⟨z, hzT, rfl⟩), hyz⟩
  constructor
  · exact hBsub
  constructor
  · exact hBbip
  · calc
      #(attachmentBranch G x (S.attach c) T) ≤
          #(trunkVertices G x T) + 1 := Finset.card_insert_le _ _
      _ ≤ T.card + 1 := Nat.add_le_add_right Finset.card_image_le 1
      _ ≤ B.card := hbudget

end WrittenOnTheWallII.GraphConjecture183LocalTrunks
