import GraphConjecture183CorrectedAssembly

/-!
# WOWII 183: finite connected-component fold

This file closes the purely additive part of the corrected outside-component
construction.  Witnesses supported in distinct connected components are
automatically disjoint and anticomplete, so their union is induced bipartite
and its cardinality is the sum of the component cardinalities.
-/

namespace WrittenOnTheWallII.GraphConjecture183ComponentFold

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183CorrectedAssembly

universe u

variable {W : Type u} [Fintype W] [DecidableEq W]

omit [Fintype W] [DecidableEq W] in
/-- Connected-component supports form a genuine partition of the vertex set:
they are pairwise disjoint and cover every vertex. -/
theorem connectedComponent_support_partition (H : SimpleGraph W) :
    (Pairwise fun c d : H.ConnectedComponent => Disjoint c.supp d.supp) ∧
      (⋃ c : H.ConnectedComponent, c.supp) = Set.univ := by
  exact ⟨pairwise_disjoint_supp_connectedComponent H,
    iUnion_connectedComponentSupp H⟩

/-- A finite witness carried by each connected component of `H`. -/
def componentWitnessUnion (H : SimpleGraph W)
    (C : Finset H.ConnectedComponent)
    (B : H.ConnectedComponent → Finset W) : Finset W :=
  C.biUnion B

omit [Fintype W] [DecidableEq W] in
/-- Witnesses contained in distinct connected-component supports are
disjoint. -/
lemma componentWitness_disjoint (H : SimpleGraph W)
    (B : H.ConnectedComponent → Finset W)
    (hsub : ∀ c, (↑(B c) : Set W) ⊆ c.supp)
    {c d : H.ConnectedComponent} (hcd : c ≠ d) :
    Disjoint (B c) (B d) := by
  rw [Finset.disjoint_left]
  intro v hvc hvd
  exact hcd (ConnectedComponent.eq_of_common_vertex (hsub c hvc) (hsub d hvd))

omit [Fintype W] [DecidableEq W] in
/-- Distinct connected components are anticomplete.  This is the exact graph
fact that makes independent component colorings patch without conflicts. -/
lemma componentWitness_anticomplete (H : SimpleGraph W)
    (B : H.ConnectedComponent → Finset W)
    (hsub : ∀ c, (↑(B c) : Set W) ⊆ c.supp)
    {c d : H.ConnectedComponent} (hcd : c ≠ d) :
    ∀ a ∈ B c, ∀ b ∈ B d, ¬H.Adj a b := by
  intro a ha b hb hab
  have hac : a ∈ c.supp := hsub c ha
  have hbc : b ∈ c.supp := (c.mem_supp_congr_adj hab).mp hac
  exact hcd (ConnectedComponent.eq_of_common_vertex hbc (hsub d hb))

omit [Fintype W] in
/-- One component witness is disjoint from the union of any finite collection
of other components. -/
lemma componentWitness_disjoint_biUnion (H : SimpleGraph W)
    (B : H.ConnectedComponent → Finset W)
    (hsub : ∀ c, (↑(B c) : Set W) ⊆ c.supp)
    (c : H.ConnectedComponent) (C : Finset H.ConnectedComponent)
    (hc : c ∉ C) :
    Disjoint (B c) (componentWitnessUnion H C B) := by
  rw [Finset.disjoint_left]
  intro v hvc hvU
  obtain ⟨d, hdC, hvd⟩ := Finset.mem_biUnion.mp hvU
  have hcd : c ≠ d := fun h => hc (h ▸ hdC)
  exact Finset.disjoint_left.mp (componentWitness_disjoint H B hsub hcd) hvc hvd

omit [Fintype W] in
/-- One component witness is anticomplete to the union of any finite
collection of other components. -/
lemma componentWitness_anticomplete_biUnion (H : SimpleGraph W)
    (B : H.ConnectedComponent → Finset W)
    (hsub : ∀ c, (↑(B c) : Set W) ⊆ c.supp)
    (c : H.ConnectedComponent) (C : Finset H.ConnectedComponent)
    (hc : c ∉ C) :
    ∀ a ∈ B c, ∀ b ∈ componentWitnessUnion H C B, ¬H.Adj a b := by
  intro a ha b hb
  obtain ⟨d, hdC, hbd⟩ := Finset.mem_biUnion.mp hb
  have hcd : c ≠ d := fun h => hc (h ▸ hdC)
  exact componentWitness_anticomplete H B hsub hcd a ha b hbd

omit [Fintype W] in
/-- A finite union of component-supported induced-bipartite witnesses remains
induced bipartite. -/
theorem componentWitnessUnion_isBipartite (H : SimpleGraph W)
    (B : H.ConnectedComponent → Finset W)
    (hsub : ∀ c, (↑(B c) : Set W) ⊆ c.supp)
    (hbip : ∀ c, (H.induce (↑(B c) : Set W)).IsBipartite)
    (C : Finset H.ConnectedComponent) :
    (H.induce (↑(componentWitnessUnion H C B) : Set W)).IsBipartite := by
  classical
  induction C using Finset.induction_on with
  | empty =>
      rw [induce_isBipartite_iff_exists_coloring]
      exact ⟨fun _ => 0, by simp [componentWitnessUnion]⟩
  | @insert c C hc ih =>
      rw [componentWitnessUnion, Finset.biUnion_insert]
      exact induce_union_isBipartite_of_anticomplete H (B c)
        (componentWitnessUnion H C B) (hbip c) ih
        (componentWitness_anticomplete_biUnion H B hsub c C hc)

omit [Fintype W] in
/-- The component fold loses no vertices: its order is the sum of the local
witness orders. -/
theorem card_componentWitnessUnion (H : SimpleGraph W)
    (B : H.ConnectedComponent → Finset W)
    (hsub : ∀ c, (↑(B c) : Set W) ⊆ c.supp)
    (C : Finset H.ConnectedComponent) :
    (componentWitnessUnion H C B).card = ∑ c ∈ C, (B c).card := by
  classical
  induction C using Finset.induction_on with
  | empty => simp [componentWitnessUnion]
  | @insert c C hc ih =>
      rw [componentWitnessUnion, Finset.biUnion_insert]
      calc
        #(B c ∪ C.biUnion B) = #(B c) + #(C.biUnion B) :=
          card_union_of_disjoint
            (componentWitness_disjoint_biUnion H B hsub c C hc)
        _ = #(B c) + ∑ d ∈ C, #(B d) := by
          rw [show C.biUnion B = componentWitnessUnion H C B from rfl, ih]
        _ = ∑ d ∈ insert c C, #(B d) := by simp [hc]

/-- Folding all connected-component witnesses gives their summed order as a
lower bound on the ambient largest induced bipartite order. -/
theorem sum_componentWitness_card_le_bipartiteSize (H : SimpleGraph W)
    (B : H.ConnectedComponent → Finset W)
    (hsub : ∀ c, (↑(B c) : Set W) ⊆ c.supp)
    (hbip : ∀ c, (H.induce (↑(B c) : Set W)).IsBipartite)
    (C : Finset H.ConnectedComponent) :
    (∑ c ∈ C, (B c).card) ≤
      H.largestInducedBipartiteSubgraphSize := by
  classical
  calc
    (∑ c ∈ C, (B c).card) = (componentWitnessUnion H C B).card :=
      (card_componentWitnessUnion H B hsub C).symm
    _ ≤ H.largestInducedBipartiteSubgraphSize :=
      card_le_largestInducedBipartiteSubgraphSize H
        (componentWitnessUnion H C B)
        (componentWitnessUnion_isBipartite H B hsub hbip C)

/-- Data remaining after the connected-component fold.  The local fields are
component-supported bipartite witnesses.  The only global graph field is the
assertion that the separately constructed `D` really is connected dominating;
the numerical field records the componentwise trunk/singleton budget. -/
structure ComponentFoldInput {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) (x : V) where
  D : Finset V
  C : Finset (outsideGraph G x).ConnectedComponent
  B : (outsideGraph G x).ConnectedComponent →
    Finset (↥(outsideVertices G x))
  supported : ∀ c, (↑(B c) : Set _) ⊆ c.supp
  bipartite : ∀ c,
    ((outsideGraph G x).induce (↑(B c) : Set _)).IsBipartite
  dominating : G.IsConnectedDominating (↑D : Set V)
  card_le_sum : D.card ≤ ∑ c ∈ C, (B c).card

/-- The arbitrary-graph component layer is now closed: a
`ComponentFoldInput` assembles to the exact certificate consumed by the v0.7
invariant transfer. -/
def outsideBudgetCertificate_of_componentFoldInput
    {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) (x : V) (F : ComponentFoldInput G x) :
    OutsideBudgetCertificate G x := by
  classical
  refine
    { D := F.D
      B := componentWitnessUnion (outsideGraph G x) F.C F.B
      dominating := F.dominating
      bipartite := componentWitnessUnion_isBipartite
        (outsideGraph G x) F.B F.supported F.bipartite F.C
      card_le := ?_ }
  rw [card_componentWitnessUnion (outsideGraph G x) F.B F.supported F.C]
  exact F.card_le_sum

end WrittenOnTheWallII.GraphConjecture183ComponentFold
