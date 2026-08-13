import FormalConjecturesUtil

/-!
# WOWII 183: the universal outside-neighborhood budget

This file formalizes the invariant-transfer layer of the universal theorem

`gamma_c(G) <= b(G - N_G(x))`.

The classical rooted trunk theorem and its componentwise assembly are exposed
as named propositions, not installed as axioms.  From an assembly certificate,
the actual repository invariants and the exact odd-transversal budget follow.
-/

namespace WrittenOnTheWallII.GraphConjecture183OutsideBudget

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Vertices outside the open neighborhood of `x`.  This includes `x`. -/
def outsideVertices (G : SimpleGraph V) (x : V) : Set V :=
  (G.neighborSet x)ᶜ

noncomputable instance outsideVerticesFintype (G : SimpleGraph V) (x : V) :
    Fintype (↥(outsideVertices G x)) :=
  Fintype.ofFinite _

/-- The induced graph `G - N_G(x)`, represented on its natural subtype. -/
abbrev outsideGraph (G : SimpleGraph V) (x : V) :
    SimpleGraph (↥(outsideVertices G x)) :=
  G.induce (outsideVertices G x)

/-- The odd-cycle-transversal number of `G - N_G(x)`, expressed as
`order - largest induced bipartite order`. -/
noncomputable def outsideOddTransversalNumber (G : SimpleGraph V) (x : V) : ℕ :=
  Fintype.card (↥(outsideVertices G x)) -
    (outsideGraph G x).largestInducedBipartiteSubgraphSize

/-- The connected-domination slack available outside the open neighborhood. -/
noncomputable def outsideSlack (G : SimpleGraph V) (x : V) : ℕ :=
  Fintype.card (↥(outsideVertices G x)) -
    G.connectedDominationNumber

/-- Rooted form of the DeLaViña--Waller trunk theorem, restricted to induced
subgraphs of the ambient finite graph.  The paper proof supplies this
statement; this file deliberately records it as a hypothesis rather than an
environment-level assumption while the greedy trunk construction is not yet in Mathlib. -/
def RootedTrunkPrinciple (G : SimpleGraph V) : Prop :=
  ∀ (S : Set V) (r : S), (G.induce S).Connected →
    ∃ D : Finset S,
      r ∈ D ∧
      (G.induce S).IsConnectedDominating (↑D : Set S) ∧
      D.card + 1 ≤ (G.induce S).largestInducedBipartiteSubgraphSize

/-- Finite output of the componentwise rooted-trunk construction.

`D` is the assembled connected dominating set in the ambient graph, while
`B` is its size-dominating induced-bipartite witness inside `G-N(x)`. -/
structure OutsideBudgetCertificate (G : SimpleGraph V) (x : V) where
  D : Finset V
  B : Finset (↥(outsideVertices G x))
  dominating : G.IsConnectedDominating (↑D : Set V)
  bipartite : ((outsideGraph G x).induce (↑B : Set _)).IsBipartite
  card_le : D.card ≤ B.card

/-- Explicit interface for the still-unformalized component-additivity step:
rooted trunks on every induced component assemble into an outside-budget
certificate. -/
def RootedComponentAssembly (G : SimpleGraph V) (x : V) : Prop :=
  RootedTrunkPrinciple G → Nonempty (OutsideBudgetCertificate G x)

omit [Fintype V] [DecidableEq V] in
/-- Any connected dominating witness bounds the repository's `sInf`
definition of connected domination number. -/
lemma connectedDominationNumber_le_card
    (G : SimpleGraph V) (D : Finset V)
    (hD : G.IsConnectedDominating (↑D : Set V)) :
    G.connectedDominationNumber ≤ D.card := by
  unfold connectedDominationNumber
  apply csInf_le
  · exact ⟨0, fun n _hn ↦ Nat.zero_le n⟩
  · exact ⟨D, hD, rfl⟩

/-- Any explicit bipartite induced witness bounds the repository's `sSup`
definition of largest induced bipartite order. -/
lemma card_le_largestInducedBipartiteSubgraphSize
    {W : Type*} [Fintype W] [DecidableEq W]
    (H : SimpleGraph W) (B : Finset W)
    (hB : (H.induce (↑B : Set W)).IsBipartite) :
    B.card ≤ H.largestInducedBipartiteSubgraphSize := by
  unfold largestInducedBipartiteSubgraphSize
  apply le_csSup
  · exact ⟨Fintype.card W, fun n ⟨T, _hT, hn⟩ ↦ hn ▸ T.card_le_univ⟩
  · exact ⟨B, hB, rfl⟩

/-- The complete repository-invariant theorem extracted from one assembled
outside-budget certificate. -/
theorem connectedDominationNumber_le_outside_bipartiteSize_of_certificate
    (G : SimpleGraph V) (x : V) (C : OutsideBudgetCertificate G x) :
    G.connectedDominationNumber ≤
      (outsideGraph G x).largestInducedBipartiteSubgraphSize := by
  exact (connectedDominationNumber_le_card G C.D C.dominating).trans
    (C.card_le.trans
      (card_le_largestInducedBipartiteSubgraphSize
        (outsideGraph G x) C.B C.bipartite))

/-- Conditional universal theorem with the two missing classical interfaces
made explicit.  Neither interface is an axiom. -/
theorem connectedDominationNumber_le_outside_bipartiteSize
    (G : SimpleGraph V) (x : V)
    (htrunk : RootedTrunkPrinciple G)
    (hassembly : RootedComponentAssembly G x) :
    G.connectedDominationNumber ≤
      (outsideGraph G x).largestInducedBipartiteSubgraphSize := by
  exact connectedDominationNumber_le_outside_bipartiteSize_of_certificate
    G x (hassembly htrunk).some

/-- The same conditional theorem in the repository's real-valued `b` notation:
`gamma_c(G) <= b(G-N(x))`. -/
theorem connectedDominationNumber_cast_le_b
    (G : SimpleGraph V) (x : V)
    (htrunk : RootedTrunkPrinciple G)
    (hassembly : RootedComponentAssembly G x) :
    (G.connectedDominationNumber : ℝ) ≤ SimpleGraph.b (outsideGraph G x) := by
  unfold SimpleGraph.b
  exact_mod_cast
    connectedDominationNumber_le_outside_bipartiteSize G x htrunk hassembly

omit [DecidableEq V] in
/-- Exact natural-number implication from the outside-budget theorem to the
odd-cycle-transversal/slack inequality. -/
theorem outsideOddTransversalNumber_le_outsideSlack_of_budget
    (G : SimpleGraph V) (x : V)
    (hbudget : G.connectedDominationNumber ≤
      (outsideGraph G x).largestInducedBipartiteSubgraphSize) :
    outsideOddTransversalNumber G x ≤ outsideSlack G x := by
  unfold outsideOddTransversalNumber outsideSlack
  omega

/-- Conditional end-to-end form: rooted trunks plus component assembly imply
the exact outside odd-transversal budget. -/
theorem outsideOddTransversalNumber_le_outsideSlack
    (G : SimpleGraph V) (x : V)
    (htrunk : RootedTrunkPrinciple G)
    (hassembly : RootedComponentAssembly G x) :
    outsideOddTransversalNumber G x ≤ outsideSlack G x := by
  apply outsideOddTransversalNumber_le_outsideSlack_of_budget G x
  exact connectedDominationNumber_le_outside_bipartiteSize G x htrunk hassembly

omit [DecidableEq V] in
/-- The outside subtype has the expected order `n-deg(x)`. -/
theorem card_outsideVertices (G : SimpleGraph V) [DecidableRel G.Adj] (x : V) :
    Fintype.card (↥(outsideVertices G x)) =
      Fintype.card V - G.degree x := by
  unfold outsideVertices
  rw [Fintype.card_compl_set, G.card_neighborSet_eq_degree]

omit [DecidableEq V] in
/-- Rewrites the formal slack in the paper's ambient-order notation. -/
theorem outsideSlack_eq (G : SimpleGraph V) [DecidableRel G.Adj] (x : V) :
    outsideSlack G x =
      (Fintype.card V - G.degree x) - G.connectedDominationNumber := by
  unfold outsideSlack
  rw [card_outsideVertices]

end WrittenOnTheWallII.GraphConjecture183OutsideBudget
