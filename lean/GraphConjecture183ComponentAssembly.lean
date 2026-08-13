import GraphConjecture183OutsideBudget

/-!
# WOWII 183: audit of the component-assembly interface

The first extraction encoded the rooted trunk estimate for every connected
induced subgraph.  That quantification includes singleton subgraphs, on which
the requested estimate `|D| + 1 ≤ b` is impossible: the root forces `|D| ≥ 1`
while the largest induced bipartite order is at most one.

Consequently the original `RootedTrunkPrinciple` is inconsistent on every
inhabited graph, and `RootedComponentAssembly` follows only vacuously.  This
file proves that diagnosis without axioms and records a corrected nontrivial-
component interface for the next construction pass.
-/

namespace WrittenOnTheWallII.GraphConjecture183ComponentAssembly

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The largest induced bipartite order never exceeds the ambient order. -/
lemma largestInducedBipartiteSubgraphSize_le_card
    {W : Type*} [Fintype W] [DecidableEq W] (H : SimpleGraph W) :
    H.largestInducedBipartiteSubgraphSize ≤ Fintype.card W := by
  unfold largestInducedBipartiteSubgraphSize
  apply csSup_le
  · refine ⟨0, ∅, ?_, rfl⟩
    rw [induce_isBipartite_iff_exists_coloring]
    exact ⟨fun _ ↦ 0, by simp⟩
  rintro n ⟨T, _hT, rfl⟩
  exact T.card_le_univ

omit [Fintype V] [DecidableEq V] in
/-- Every graph induced on a singleton vertex set is connected. -/
lemma induce_singleton_connected (G : SimpleGraph V) (v : V) :
    (G.induce ({v} : Set V)).Connected := by
  rw [connected_iff]
  exact ⟨Preconnected.of_subsingleton, ⟨⟨v, Set.mem_singleton v⟩⟩⟩

omit [Fintype V] in
/-- The singleton case contradicts the `+1` estimate in the original rooted
trunk interface. -/
theorem not_rootedTrunkPrinciple (G : SimpleGraph V) [Nonempty V] :
    ¬ RootedTrunkPrinciple G := by
  intro htrunk
  let v : V := Classical.choice (inferInstance : Nonempty V)
  let r : ({v} : Set V) := ⟨v, Set.mem_singleton v⟩
  obtain ⟨D, hr, _hdom, hcard⟩ :=
    htrunk ({v} : Set V) r (induce_singleton_connected G v)
  have hone : 1 ≤ D.card := Finset.one_le_card.mpr ⟨r, hr⟩
  have hb : (G.induce ({v} : Set V)).largestInducedBipartiteSubgraphSize ≤ 1 := by
    exact (largestInducedBipartiteSubgraphSize_le_card
      (G.induce ({v} : Set V))).trans_eq (by simp)
  omega

omit [Fintype V] in
/-- The previously exposed assembly proposition is provable, but only because
its rooted premise is contradictory.  This theorem must not be mistaken for
the desired component construction. -/
theorem rootedComponentAssembly_vacuous
    (G : SimpleGraph V) [Nonempty V] (x : V) :
    RootedComponentAssembly G x := by
  intro htrunk
  exact (not_rootedTrunkPrinciple G htrunk).elim

/-- Corrected rooted trunk interface: the `|D|+1` estimate is requested only
for induced connected sets having at least two vertices.  Singleton outside
components (in particular the component containing `x`) must be paid for
separately in the component assembly. -/
def NontrivialRootedTrunkPrinciple (G : SimpleGraph V) : Prop :=
  ∀ (S : Set V) (r : S), (G.induce S).Connected → 2 ≤ S.ncard →
    ∃ D : Finset S,
      r ∈ D ∧
      (G.induce S).IsConnectedDominating (↑D : Set S) ∧
      D.card + 1 ≤ (G.induce S).largestInducedBipartiteSubgraphSize

/-- Exact remaining construction lemma after repairing the singleton bug.

It packages the finite-component decomposition, attachment-neighbor choices,
rooted trunk union, and patching of componentwise bipartite witnesses.  Keeping
this as a proposition-valued hypothesis makes the unformalized mathematical
step explicit and does not add an environment axiom. -/
def NontrivialComponentConstruction (G : SimpleGraph V) (x : V) : Prop :=
  G.Connected → NontrivialRootedTrunkPrinciple G →
    Nonempty (OutsideBudgetCertificate G x)

omit [Fintype V] [DecidableEq V] in
/-- A corrected component construction immediately supplies the non-vacuous
certificate needed by the invariant-transfer theorem. -/
theorem certificate_of_nontrivialComponentConstruction
    (G : SimpleGraph V) (x : V)
    (hconnected : G.Connected)
    (htrunk : NontrivialRootedTrunkPrinciple G)
    (hassembly : NontrivialComponentConstruction G x) :
    Nonempty (OutsideBudgetCertificate G x) :=
  hassembly hconnected htrunk

end WrittenOnTheWallII.GraphConjecture183ComponentAssembly
