import GraphConjecture40CutVertexSum

/-!
# WOWII 40: one-vertex separation, restriction half

This file defines an explicit one-vertex separation and proves the complete
restriction inequality for the exclude-cut forest state.  The reverse
inequality is isolated as the remaining cycle-localization lemma.
-/

namespace WrittenOnTheWallII.GraphConjecture40OneVertexSeparation

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

structure OneVertexSeparation (G : SimpleGraph V) where
  left : Finset V
  right : Finset V
  cut : V
  cover : left ∪ right = Finset.univ
  inter : left ∩ right = {cut}
  no_cross : ∀ x ∈ left, x ≠ cut → ∀ y ∈ right, y ≠ cut →
    ¬G.Adj x y

noncomputable def forestOrderWithin (G : SimpleGraph V) (A : Finset V) : ℕ :=
  sSup {n | ∃ S : Finset V, S ⊆ A ∧
    (G.induce (S : Set V)).IsAcyclic ∧ S.card = n}

omit [Fintype V] [DecidableEq V] in
lemma exists_forestOrderWithin_witness (G : SimpleGraph V) (A : Finset V) :
    ∃ S : Finset V, S ⊆ A ∧ (G.induce (S : Set V)).IsAcyclic ∧
      S.card = forestOrderWithin G A := by
  let X : Set ℕ := {n | ∃ S : Finset V, S ⊆ A ∧
    (G.induce (S : Set V)).IsAcyclic ∧ S.card = n}
  have hne : X.Nonempty := by
    refine ⟨0, ∅, by simp, ?_, rfl⟩
    intro v
    have hv : False := by simpa using v.property
    exact hv.elim
  have hbdd : BddAbove X := ⟨A.card, fun n hn ↦ by
    obtain ⟨S, hSA, -, rfl⟩ := hn
    exact Finset.card_le_card hSA⟩
  obtain ⟨S, hSA, hS, hc⟩ := Nat.sSup_mem hne hbdd
  exact ⟨S, hSA, hS, by simpa [forestOrderWithin, X] using hc⟩

omit [Fintype V] [DecidableEq V] in
lemma card_le_forestOrderWithin (G : SimpleGraph V) (A S : Finset V)
    (hSA : S ⊆ A) (hS : (G.induce (S : Set V)).IsAcyclic) :
    S.card ≤ forestOrderWithin G A := by
  unfold forestOrderWithin
  apply le_csSup
  · exact ⟨A.card, fun n hn ↦ by
      obtain ⟨T, hTA, -, rfl⟩ := hn
      exact Finset.card_le_card hTA⟩
  · exact ⟨S, hSA, hS, rfl⟩

namespace OneVertexSeparation

variable {G : SimpleGraph V}

lemma cut_mem_left (D : OneVertexSeparation G) : D.cut ∈ D.left := by
  have : D.cut ∈ D.left ∩ D.right := by rw [D.inter]; simp
  exact (mem_inter.mp this).1

lemma cut_mem_right (D : OneVertexSeparation G) : D.cut ∈ D.right := by
  have : D.cut ∈ D.left ∩ D.right := by rw [D.inter]; simp
  exact (mem_inter.mp this).2

/-- A set excluding the cut splits cardinally across the two sides. -/
lemma card_inter_left_add_inter_right
    (D : OneVertexSeparation G) (S : Finset V) (hc : D.cut ∉ S) :
    (S ∩ D.left).card + (S ∩ D.right).card = S.card := by
  have hcover : S ∩ (D.left ∪ D.right) = S := by rw [D.cover]; simp
  have hdisj : Disjoint (S ∩ D.left) (S ∩ D.right) := by
    rw [Finset.disjoint_left]
    intro x hxL hxR
    have hxinter : x ∈ D.left ∩ D.right :=
      mem_inter.mpr ⟨(mem_inter.mp hxL).2, (mem_inter.mp hxR).2⟩
    have hxc : x = D.cut := by simpa [D.inter] using hxinter
    exact hc (hxc ▸ (mem_inter.mp hxL).1)
  rw [← card_union_of_disjoint hdisj]
  congr 1
  ext x
  simp only [mem_union, mem_inter]
  constructor
  · rintro (⟨hx, -⟩ | ⟨hx, -⟩) <;> exact hx
  · intro hx
    have : x ∈ D.left ∪ D.right := by rw [D.cover]; simp
    rcases mem_union.mp this with hxL | hxR
    · exact Or.inl ⟨hx, hxL⟩
    · exact Or.inr ⟨hx, hxR⟩

/-- Complete restriction half of the exclude-cut formula. Every global
excluding forest restricts to forests on both sides, so its order is at most
the sum of the two side optima. -/
theorem forestOrderExcluding_le_sum_within_erase
    (D : OneVertexSeparation G) :
    GraphConjecture40CutVertexSum.forestOrderExcluding G D.cut ≤
      forestOrderWithin G (D.left.erase D.cut) +
        forestOrderWithin G (D.right.erase D.cut) := by
  obtain ⟨S, hS, hc, hcard⟩ :=
    GraphConjecture40CutVertexSum.exists_forestOrderExcluding_witness G D.cut
  rw [← hcard]
  let SL := S ∩ D.left
  let SR := S ∩ D.right
  have hSLsub : SL ⊆ D.left.erase D.cut := by
    intro x hx
    exact mem_erase.mpr ⟨fun hxc ↦ hc (hxc ▸ (mem_inter.mp hx).1),
      (mem_inter.mp hx).2⟩
  have hSRsub : SR ⊆ D.right.erase D.cut := by
    intro x hx
    exact mem_erase.mpr ⟨fun hxc ↦ hc (hxc ▸ (mem_inter.mp hx).1),
      (mem_inter.mp hx).2⟩
  have hSLacyc : (G.induce (SL : Set V)).IsAcyclic := by
    have hsub : (SL : Set V) ⊆ (S : Set V) := by
      intro x hx
      exact (mem_inter.mp hx).1
    exact hS.embedding (G.induceHomOfLE hsub)
  have hSRacyc : (G.induce (SR : Set V)).IsAcyclic := by
    have hsub : (SR : Set V) ⊆ (S : Set V) := by
      intro x hx
      exact (mem_inter.mp hx).1
    exact hS.embedding (G.induceHomOfLE hsub)
  have hleft := card_le_forestOrderWithin G _ SL hSLsub hSLacyc
  have hright := card_le_forestOrderWithin G _ SR hSRsub hSRacyc
  have hcardSplit := D.card_inter_left_add_inter_right S hc
  change SL.card + SR.card = S.card at hcardSplit
  omega

end OneVertexSeparation

end WrittenOnTheWallII.GraphConjecture40OneVertexSeparation
