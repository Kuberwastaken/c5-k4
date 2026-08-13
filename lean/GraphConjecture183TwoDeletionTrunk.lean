import GraphConjecture183UnicyclicTrunk

/-!
# WOWII 183: two-deletion nonbipartite trunks

The exact numerical threshold is formalized.  A trunk omitting two vertices
and a bipartite witness omitting one has equal local branch/witness order after
the mandatory attachment is added.  The graph-theoretic conditions are exposed
as a corrected structural package and fed through the final local interface.
-/

namespace WrittenOnTheWallII.GraphConjecture183TwoDeletionTrunk

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183AttachmentSelection
open WrittenOnTheWallII.GraphConjecture183SelectionExistence
open WrittenOnTheWallII.GraphConjecture183LocalTrunks
open WrittenOnTheWallII.GraphConjecture183UnicyclicTrunk

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Corrected nonbipartite local structure: the trunk is two vertices below
the component order, while the induced-bipartite witness is at most one vertex
below it.  Connectivity and domination are stated in the exact ambient/outside
forms consumed by the fold. -/
structure TwoDeletionComponentData (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent) where
  T : Finset (outsideVertices G x)
  B : Finset (outsideVertices G x)
  root_mem : S.root c ∈ T
  trunk_connected :
    (G.induce (↑(trunkVertices G x T) : Set V)).Connected
  trunk_dominates : ∀ y, y ∈ c.supp →
    y ∈ T ∨ ∃ z ∈ T, (outsideGraph G x).Adj y z
  witness_supported : (↑B : Set _) ⊆ c.supp
  witness_bipartite :
    ((outsideGraph G x).induce (↑B : Set _)).IsBipartite
  trunk_two_below : T.card + 2 ≤ c.supp.ncard
  witness_one_below : c.supp.ncard ≤ B.card + 1

omit [Fintype V] in
/-- Pure arithmetic heart of the corrected construction. -/
lemma twoDeletion_budget (t b n : ℕ)
    (ht : t + 2 ≤ n) (hb : n ≤ b + 1) : t + 1 ≤ b := by
  omega

omit [Fintype V] in
/-- A corrected two-deletion component supplies the exact v0.14 local branch
package. -/
theorem twoDeletionComponent_local_package (G : SimpleGraph V) (x : V)
    (S : SelectedAttachmentData G x)
    (c : (outsideGraph G x).ConnectedComponent) (hc : c ∈ S.C)
    (A : TwoDeletionComponentData G x S c) :
    S.attach c ∈ attachmentBranch G x (S.attach c) A.T ∧
    (G.induce (↑(attachmentBranch G x (S.attach c) A.T) : Set V)).Connected ∧
    (∀ y, y ∈ c.supp → y.1 ∈ attachmentBranch G x (S.attach c) A.T ∨
      ∃ z ∈ attachmentBranch G x (S.attach c) A.T, G.Adj y.1 z) ∧
    (↑A.B : Set _) ⊆ c.supp ∧
    ((outsideGraph G x).induce (↑A.B : Set _)).IsBipartite ∧
    (attachmentBranch G x (S.attach c) A.T).card ≤ A.B.card := by
  apply nontrivial_rootedTrunk_local_package G x S c hc A.T A.B
    A.root_mem A.trunk_connected A.trunk_dominates
    A.witness_supported A.witness_bipartite
  exact twoDeletion_budget A.T.card A.B.card c.supp.ncard
    A.trunk_two_below A.witness_one_below

/-- On an odd cycle, an adjacent two-vertex deletion is the wrong geometry:
the remaining vertices form a path and hence are connected, but the deleted
pair can be dominated only if each endpoint has a retained neighbor.  This
predicate records precisely the good adjacent-pair configuration, allowing
root-sensitive cycle constructions to target it without another global
interface change. -/
def IsGoodTwoDeletion (H : SimpleGraph V) (q₁ q₂ : V) : Prop :=
  q₁ ≠ q₂ ∧ H.Adj q₁ q₂ ∧
  (H.induce ({q₁, q₂} : Set V)ᶜ).Connected ∧
  (H.induce ({q₁, q₂} : Set V)ᶜ).IsBipartite ∧
  (∃ z ∉ ({q₁, q₂} : Set V), H.Adj q₁ z) ∧
  (∃ z ∉ ({q₁, q₂} : Set V), H.Adj q₂ z)

omit [Fintype V] in
/-- The complement of a good deleted pair dominates the original graph. -/
theorem goodTwoDeletion_isConnectedDominating (H : SimpleGraph V) (q₁ q₂ : V)
    (h : IsGoodTwoDeletion H q₁ q₂) :
    H.IsConnectedDominating (({q₁, q₂} : Set V)ᶜ) := by
  constructor
  · intro v
    by_cases hv : v ∈ ({q₁, q₂} : Set V)ᶜ
    · exact Or.inl hv
    · have hvpair : v = q₁ ∨ v = q₂ := by
        by_cases hv1 : v = q₁
        · exact Or.inl hv1
        · exact Or.inr (by
            by_contra hv2
            exact hv (by simp [hv1, hv2]))
      rcases hvpair with rfl | rfl
      · obtain ⟨z, hz, hqz⟩ := h.2.2.2.2.1
        exact Or.inr ⟨z, hz, hqz⟩
      · obtain ⟨z, hz, hqz⟩ := h.2.2.2.2.2
        exact Or.inr ⟨z, hz, hqz⟩
  · exact h.2.2.1

omit [Fintype V] [DecidableEq V] in
/-- The good-pair predicate also supplies the desired bipartite witness on the
same retained vertex set. -/
theorem goodTwoDeletion_isBipartite (H : SimpleGraph V) (q₁ q₂ : V)
    (h : IsGoodTwoDeletion H q₁ q₂) :
    (H.induce (({q₁, q₂} : Set V)ᶜ)).IsBipartite :=
  h.2.2.2.1

end WrittenOnTheWallII.GraphConjecture183TwoDeletionTrunk
