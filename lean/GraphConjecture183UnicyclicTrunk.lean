import GraphConjecture183AmbientConnectivity

/-!
# WOWII 183: cycle-breaking local packages

The useful nonbipartite step is not unicyclicity by itself but an explicit
cycle-breaking vertex `q`: deleting `q` leaves a connected bipartite graph and
`q` is dominated from the deletion.  If `q` differs from the prescribed root,
the deletion is an exact rooted trunk and its full order supplies the local
budget.  This covers odd cycles and the non-cut vertices of their attached
cycle core; cut-vertex attachments require a different branch.
-/

namespace WrittenOnTheWallII.GraphConjecture183UnicyclicTrunk

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183AttachmentSelection
open WrittenOnTheWallII.GraphConjecture183SelectionExistence
open WrittenOnTheWallII.GraphConjecture183NontrivialTrunk
open WrittenOnTheWallII.GraphConjecture183TreeTrunkExistence

universe u

variable {W : Type u} [Fintype W] [DecidableEq W]

/-- A vertex whose deletion is connected bipartite and which has a neighbor in
the deletion.  This is the exact structural condition needed for the one-
vertex cycle-breaking trunk. -/
def IsGoodCycleBreak (H : SimpleGraph W) (q : W) : Prop :=
  (H.induce ({q} : Set W)ᶜ).Connected ∧
  (H.induce ({q} : Set W)ᶜ).IsBipartite ∧
  ∃ z : W, z ≠ q ∧ H.Adj q z

/-- Deleting a good cycle-breaking vertex gives a connected dominating set. -/
theorem deleteCycleBreak_isConnectedDominating (H : SimpleGraph W) (q : W)
    (hq : IsGoodCycleBreak H q) :
    H.IsConnectedDominating (↑(deleteVertexFinset q) : Set W) := by
  constructor
  · intro v
    by_cases hvq : v = q
    · subst v
      obtain ⟨z, hzq, hqz⟩ := hq.2.2
      exact Or.inr ⟨z, by
        change z ∈ deleteVertexFinset q
        exact mem_deleteVertexFinset_iff.mpr hzq, hqz⟩
    · exact Or.inl (mem_deleteVertexFinset_iff.mpr hvq)
  · have heq : (↑(deleteVertexFinset q) : Set W) = ({q} : Set W)ᶜ := by
      ext v
      simp [deleteVertexFinset]
    rw [heq]
    exact hq.1

/-- The deletion itself is an induced-bipartite witness. -/
theorem deleteCycleBreak_isBipartite (H : SimpleGraph W) (q : W)
    (hq : IsGoodCycleBreak H q) :
    (H.induce (↑(deleteVertexFinset q) : Set W)).IsBipartite := by
  have heq : (↑(deleteVertexFinset q) : Set W) = ({q} : Set W)ᶜ := by
    ext v
    simp [deleteVertexFinset]
  rw [heq]
  exact hq.2.1

/-- Exact abstract rooted cycle-breaking package. -/
theorem rooted_deleteCycleBreak_package [Nonempty W]
    (H : SimpleGraph W) (r q : W) (hrq : r ≠ q)
    (hq : IsGoodCycleBreak H q) :
    r ∈ deleteVertexFinset q ∧
    H.IsConnectedDominating (↑(deleteVertexFinset q) : Set W) ∧
    (H.induce (↑(deleteVertexFinset q) : Set W)).IsBipartite ∧
    (deleteVertexFinset q).card + 1 = Fintype.card W := by
  exact ⟨mem_deleteVertexFinset_iff.mpr hrq,
    deleteCycleBreak_isConnectedDominating H q hq,
    deleteCycleBreak_isBipartite H q hq,
    card_deleteVertexFinset_add_one q⟩

universe v
variable {V : Type v} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- The attachment vertex is never among the flattened outside trunk vertices:
it is adjacent to `x`, whereas every outside vertex is a nonneighbor of `x`. -/
lemma attach_not_mem_trunkVertices (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x) (c) (hc : c ∈ S.C)
    (T : Finset (outsideVertices G x)) :
    S.attach c ∉ trunkVertices G x T := by
  intro hp
  obtain ⟨p, _hpT, hpv⟩ := Finset.mem_image.mp hp
  have houtside : ¬G.Adj x p.1 := p.property
  exact houtside (hpv ▸ S.attach_adj_x c hc)

omit [Fintype V] in
/-- Therefore an attachment plus a trunk really costs one more vertex. -/
theorem card_attachmentBranch (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x) (c) (hc : c ∈ S.C)
    (T : Finset (outsideVertices G x)) :
    (attachmentBranch G x (S.attach c) T).card = T.card + 1 := by
  unfold attachmentBranch trunkVertices
  rw [Finset.card_insert_of_notMem]
  · rw [Finset.card_image_of_injective _ Subtype.val_injective]
  · exact attach_not_mem_trunkVertices G x S c hc T

omit [Fintype V] in
/-- **Exact obstruction.** A trunk obtained by deleting only one component
vertex cannot be paid for by a proper induced-bipartite witness after the
mandatory attachment vertex is added. -/
theorem oneDeletion_budget_impossible (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x) (c) (hc : c ∈ S.C)
    (T B : Finset (outsideVertices G x)) (n : ℕ)
    (hT : T.card + 1 = n) (hB : B.card < n) :
    ¬(attachmentBranch G x (S.attach c) T).card ≤ B.card := by
  rw [card_attachmentBranch G x S c hc T, hT]
  omega

end WrittenOnTheWallII.GraphConjecture183UnicyclicTrunk
