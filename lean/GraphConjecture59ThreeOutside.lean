import GraphConjecture59MultipleOutside

/-!
# WOWII 59: three dense outside rows

Three subsets of a three-set, each of size at least two, have an exact
dichotomy.  Either all three share a common element, or all three are distinct
two-subsets.  This is the incidence classification governing three
exchange-resistant outside attachment rows on either color side of a `3+3`
core.
-/

namespace WrittenOnTheWallII.GraphConjecture59ThreeOutside

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- Two subsets of a three-set, both of order at least two, intersect. -/
theorem two_large_subsets_of_three_inter_nonempty
    (U A B : Finset V) (hU : U.card = 3)
    (hAU : A ⊆ U) (hBU : B ⊆ U)
    (hA : 2 ≤ A.card) (hB : 2 ≤ B.card) :
    (A ∩ B).Nonempty := by
  have hunion : (A ∪ B).card ≤ 3 := by
    rw [← hU]
    exact card_le_card (union_subset hAU hBU)
  have hinclusion := card_union_add_card_inter A B
  have hinter : 1 ≤ (A ∩ B).card := by omega
  exact card_pos.mp hinter

omit [Fintype V] in
/-- Exact three-row classification on one three-vertex color side. -/
theorem three_large_subsets_of_three_classification
    (U A B C : Finset V) (hU : U.card = 3)
    (hAU : A ⊆ U) (hBU : B ⊆ U) (hCU : C ⊆ U)
    (hA : 2 ≤ A.card) (hB : 2 ≤ B.card) (hC : 2 ≤ C.card) :
    (A ∩ B ∩ C).Nonempty ∨
      (A.card = 2 ∧ B.card = 2 ∧ C.card = 2 ∧
        A ≠ B ∧ A ≠ C ∧ B ≠ C) := by
  by_cases htriple : (A ∩ B ∩ C).Nonempty
  · exact Or.inl htriple
  · right
    have hAupper : A.card ≤ 3 := by
      rw [← hU]
      exact card_le_card hAU
    have hBupper : B.card ≤ 3 := by
      rw [← hU]
      exact card_le_card hBU
    have hCupper : C.card ≤ 3 := by
      rw [← hU]
      exact card_le_card hCU
    have hAne3 : A.card ≠ 3 := by
      intro hA3
      have hAUeq : A = U := eq_of_subset_of_card_le hAU (by omega)
      have hBC := two_large_subsets_of_three_inter_nonempty
        U B C hU hBU hCU hB hC
      apply htriple
      obtain ⟨v, hv⟩ := hBC
      obtain ⟨hvB, hvC⟩ := mem_inter.mp hv
      have hvA : v ∈ A := by rw [hAUeq]; exact hBU hvB
      exact ⟨v, mem_inter.mpr ⟨mem_inter.mpr ⟨hvA, hvB⟩, hvC⟩⟩
    have hBne3 : B.card ≠ 3 := by
      intro hB3
      have hBUeq : B = U := eq_of_subset_of_card_le hBU (by omega)
      have hAC := two_large_subsets_of_three_inter_nonempty
        U A C hU hAU hCU hA hC
      apply htriple
      obtain ⟨v, hv⟩ := hAC
      obtain ⟨hvA, hvC⟩ := mem_inter.mp hv
      have hvB : v ∈ B := by rw [hBUeq]; exact hAU hvA
      exact ⟨v, mem_inter.mpr ⟨mem_inter.mpr ⟨hvA, hvB⟩, hvC⟩⟩
    have hCne3 : C.card ≠ 3 := by
      intro hC3
      have hCUeq : C = U := eq_of_subset_of_card_le hCU (by omega)
      have hAB := two_large_subsets_of_three_inter_nonempty
        U A B hU hAU hBU hA hB
      apply htriple
      obtain ⟨v, hv⟩ := hAB
      obtain ⟨hvA, hvB⟩ := mem_inter.mp hv
      have hvC : v ∈ C := by rw [hCUeq]; exact hAU hvA
      exact ⟨v, mem_inter.mpr ⟨mem_inter.mpr ⟨hvA, hvB⟩, hvC⟩⟩
    have hA2 : A.card = 2 := by omega
    have hB2 : B.card = 2 := by omega
    have hC2 : C.card = 2 := by omega
    have hABne : A ≠ B := by
      intro hABeq
      have hAC := two_large_subsets_of_three_inter_nonempty
        U A C hU hAU hCU hA hC
      apply htriple
      obtain ⟨v, hv⟩ := hAC
      obtain ⟨hvA, hvC⟩ := mem_inter.mp hv
      exact ⟨v, mem_inter.mpr ⟨
        mem_inter.mpr ⟨hvA, by simpa [hABeq] using hvA⟩, hvC⟩⟩
    have hACne : A ≠ C := by
      intro hACeq
      have hAB := two_large_subsets_of_three_inter_nonempty
        U A B hU hAU hBU hA hB
      apply htriple
      obtain ⟨v, hv⟩ := hAB
      obtain ⟨hvA, hvB⟩ := mem_inter.mp hv
      exact ⟨v, mem_inter.mpr ⟨
        mem_inter.mpr ⟨hvA, hvB⟩, by simpa [← hACeq] using hvA⟩⟩
    have hBCne : B ≠ C := by
      intro hBCeq
      have hAB := two_large_subsets_of_three_inter_nonempty
        U A B hU hAU hBU hA hB
      apply htriple
      obtain ⟨v, hv⟩ := hAB
      obtain ⟨hvA, hvB⟩ := mem_inter.mp hv
      exact ⟨v, mem_inter.mpr ⟨
        mem_inter.mpr ⟨hvA, hvB⟩, by simpa [← hBCeq] using hvB⟩⟩
    exact ⟨hA2, hB2, hC2, hABne, hACne, hBCne⟩

omit [Fintype V] in
/-- Specialized three-outside-row dichotomy on each color side of a `3+3`
core. -/
theorem three_dense_attachment_rows_classification
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x y z : V) (c : V → Fin 2)
    (hclass : ∀ k : Fin 2,
      (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
        S c k).card = 3)
    (hx : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card)
    (hy : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S y c k).card)
    (hz : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S z c k).card) :
    ∀ k : Fin 2,
      let A := _root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k
      let B := _root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S y c k
      let C := _root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S z c k
      (A ∩ B ∩ C).Nonempty ∨
        (A.card = 2 ∧ B.card = 2 ∧ C.card = 2 ∧
          A ≠ B ∧ A ≠ C ∧ B ≠ C) := by
  intro k
  dsimp
  apply three_large_subsets_of_three_classification
    (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass S c k)
  · exact hclass k
  · exact
      _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
        G S x c k
  · exact
      _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
        G S y c k
  · exact
      _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
        G S z c k
  · exact hx k
  · exact hy k
  · exact hz k

end WrittenOnTheWallII.GraphConjecture59ThreeOutside
