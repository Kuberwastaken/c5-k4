import GraphConjecture40Baseline

/-!
# WOWII 61: bridge-block induced-forest composition

This file gives an exact certificate API for the block-additive induced-forest
computations used by the clique, cycle, and theta bead trials.  It deliberately
separates two obligations:

* every ambient induced forest restricts to the declared block maxima;
* chosen block-maximizing witnesses remain acyclic when combined.

The second obligation is automatic for a genuine bridge join, but is retained
explicitly because the current graph API has no ready-made theorem transporting
acyclicity across a unique cross edge.
-/

namespace WrittenOnTheWallII.GraphConjecture61BridgeForestAdditivity

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture40Baseline

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- An exact two-block induced-forest composition certificate.

`leftBound` and `rightBound` are stated directly on restrictions of an
arbitrary ambient induced forest.  This is the strongest API-neutral form of
the fact that a forest cannot exceed either block maximum. -/
structure ForestBlockCompositionCertificate (G : SimpleGraph V) where
  left : Finset V
  right : Finset V
  blocks_disjoint : Disjoint left right
  blocks_cover : left ∪ right = Finset.univ
  leftMaximum : ℕ
  rightMaximum : ℕ
  leftBound : ∀ S : Finset V,
    (G.induce (S : Set V)).IsAcyclic → (S ∩ left).card ≤ leftMaximum
  rightBound : ∀ S : Finset V,
    (G.induce (S : Set V)).IsAcyclic → (S ∩ right).card ≤ rightMaximum
  leftWitness : Finset V
  rightWitness : Finset V
  leftWitness_subset : leftWitness ⊆ left
  rightWitness_subset : rightWitness ⊆ right
  leftWitness_card : leftWitness.card = leftMaximum
  rightWitness_card : rightWitness.card = rightMaximum
  combinedWitness_acyclic :
    (G.induce (↑(leftWitness ∪ rightWitness) : Set V)).IsAcyclic

/-- Bridge metadata layered over the exact composition certificate.  The only
cross-block adjacency is the declared attachment edge. -/
structure BridgeAttachedForestCertificate (G : SimpleGraph V)
    extends ForestBlockCompositionCertificate G where
  leftRoot : V
  rightRoot : V
  leftRoot_mem : leftRoot ∈ left
  rightRoot_mem : rightRoot ∈ right
  bridge_adj : G.Adj leftRoot rightRoot
  cross_adj_only : ∀ {x y : V}, x ∈ left → y ∈ right → G.Adj x y →
    x = leftRoot ∧ y = rightRoot

omit [DecidableEq V] in
/-- The finite `sSup` defining maximum induced-forest order is attained. -/
lemma exists_largestInducedForestSize_witness (G : SimpleGraph V) :
    ∃ S : Finset V,
      (G.induce (S : Set V)).IsAcyclic ∧
      S.card = G.largestInducedForestSize := by
  let A : Set ℕ :=
    {n | ∃ S : Finset V, (G.induce (S : Set V)).IsAcyclic ∧ S.card = n}
  have hAne : A.Nonempty := by
    refine ⟨0, ∅, ?_, rfl⟩
    intro v
    exact (by simpa using v.property : False).elim
  have hAbdd : BddAbove A := by
    exact ⟨Fintype.card V, fun n hn ↦ by
      obtain ⟨S, -, rfl⟩ := hn
      exact S.card_le_univ⟩
  obtain ⟨S, hS, hcard⟩ := Nat.sSup_mem hAne hAbdd
  exact ⟨S, hS, by
    simpa [largestInducedForestSize, A] using hcard⟩

/-- Every induced forest has size at most the sum of the two certified block
maxima. -/
theorem ForestBlockCompositionCertificate.forest_card_le_sum
    {G : SimpleGraph V} (C : ForestBlockCompositionCertificate G)
    (S : Finset V) (hS : (G.induce (S : Set V)).IsAcyclic) :
    S.card ≤ C.leftMaximum + C.rightMaximum := by
  have hsplit : (S ∩ C.left) ∪ (S ∩ C.right) = S := by
    ext x
    have hxcover : x ∈ C.left ∨ x ∈ C.right := by
      have : x ∈ C.left ∪ C.right := by rw [C.blocks_cover]; simp
      simpa using this
    simp only [Finset.mem_union, Finset.mem_inter]
    constructor
    · rintro (⟨hxS, -⟩ | ⟨hxS, -⟩)
      · exact hxS
      · exact hxS
    · intro hxS
      exact hxcover.elim (fun hxL ↦ Or.inl ⟨hxS, hxL⟩)
        (fun hxR ↦ Or.inr ⟨hxS, hxR⟩)
  have hdisj : Disjoint (S ∩ C.left) (S ∩ C.right) := by
    rw [Finset.disjoint_left]
    intro x hxL hxR
    have hxL' := (Finset.mem_inter.mp hxL).2
    have hxR' := (Finset.mem_inter.mp hxR).2
    exact Finset.disjoint_left.mp C.blocks_disjoint hxL' hxR'
  have hcard : S.card = (S ∩ C.left).card + (S ∩ C.right).card := by
    calc
      S.card = ((S ∩ C.left) ∪ (S ∩ C.right)).card :=
        congrArg Finset.card hsplit.symm
      _ = (S ∩ C.left).card + (S ∩ C.right).card :=
        card_union_of_disjoint hdisj
  rw [hcard]
  exact Nat.add_le_add (C.leftBound S hS) (C.rightBound S hS)

/-- The compatible block witnesses give the matching lower bound. -/
theorem ForestBlockCompositionCertificate.sum_le_largestInducedForestSize
    {G : SimpleGraph V} (C : ForestBlockCompositionCertificate G) :
    C.leftMaximum + C.rightMaximum ≤ G.largestInducedForestSize := by
  have hwdisj : Disjoint C.leftWitness C.rightWitness := by
    rw [Finset.disjoint_left]
    intro x hxL hxR
    exact Finset.disjoint_left.mp C.blocks_disjoint
      (C.leftWitness_subset hxL) (C.rightWitness_subset hxR)
  have hcard : (C.leftWitness ∪ C.rightWitness).card =
      C.leftMaximum + C.rightMaximum := by
    rw [card_union_of_disjoint hwdisj, C.leftWitness_card, C.rightWitness_card]
  rw [← hcard]
  exact card_le_largestInducedForestSize G
    (C.leftWitness ∪ C.rightWitness) C.combinedWitness_acyclic

/-- Exact additivity from the block restriction bounds and compatible maximum
witnesses. -/
theorem ForestBlockCompositionCertificate.largestInducedForestSize_eq_sum
    {G : SimpleGraph V} (C : ForestBlockCompositionCertificate G) :
    G.largestInducedForestSize = C.leftMaximum + C.rightMaximum := by
  apply Nat.le_antisymm
  · obtain ⟨S, hS, hcard⟩ := exists_largestInducedForestSize_witness G
    rw [← hcard]
    exact C.forest_card_le_sum S hS
  · exact C.sum_le_largestInducedForestSize

/-- The bridge-attached wrapper exposes the same exact block sum. -/
theorem BridgeAttachedForestCertificate.largestInducedForestSize_eq_sum
    {G : SimpleGraph V} (C : BridgeAttachedForestCertificate G) :
    G.largestInducedForestSize = C.leftMaximum + C.rightMaximum :=
  C.toForestBlockCompositionCertificate.largestInducedForestSize_eq_sum

/-- Iteration-friendly arithmetic form: attaching a certified bead adds its
exact forest contribution to the previously certified block. -/
theorem BridgeAttachedForestCertificate.largestInducedForestSize_sub_left
    {G : SimpleGraph V} (C : BridgeAttachedForestCertificate G) :
    G.largestInducedForestSize - C.leftMaximum = C.rightMaximum := by
  rw [C.largestInducedForestSize_eq_sum, Nat.add_sub_cancel_left]

end WrittenOnTheWallII.GraphConjecture61BridgeForestAdditivity
