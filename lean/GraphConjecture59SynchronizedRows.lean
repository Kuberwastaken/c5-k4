import GraphConjecture59ManyOutside

/-!
# WOWII 59: synchronizing the two color sides

A dense full attachment row is a pair of side types.  Each side type is one of
the four subsets of a three-set having order at least two.  Hence there are at
most sixteen full row types: seventeen outside vertices force a repeated full
row.  More locally, any five *distinct* full row types force a triple aligned
on both color sides; the sharpness and finite proof of that threshold are
recorded in the accompanying audit, while this file formalizes the reusable
full-row encoding and the unconditional repetition theorem.
-/

namespace WrittenOnTheWallII.GraphConjecture59SynchronizedRows

open SimpleGraph Finset

universe u

variable {V W : Type u} [Fintype V] [DecidableEq V]

/-- The full two-sided attachment row of one outside vertex. -/
def fullAttachmentRow (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2) : Finset V × Finset V :=
  (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
    G S x c 0,
   _root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
    G S x c 1)

omit [Fintype V] in
/-- A dense full row lies in the Cartesian product of the two four-element
families of large side subsets. -/
theorem fullAttachmentRow_mem_product
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2)
    (hclass : ∀ k : Fin 2,
      (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
        S c k).card = 3)
    (hdense : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card) :
    fullAttachmentRow G S x c ∈
      ((_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
          S c 0).powersetCard 2 ∪
       (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
          S c 0).powersetCard 3).product
      ((_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
          S c 1).powersetCard 2 ∪
       (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
          S c 1).powersetCard 3) := by
  have hcases :=
    _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.each_color_attachment_count_eq_two_or_three
      G S x c hclass hdense
  apply mem_product.mpr
  constructor
  · rcases hcases 0 with h2 | h3
    · apply mem_union_left
      exact mem_powersetCard.mpr ⟨
        _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
          G S x c 0, h2⟩
    · apply mem_union_right
      exact mem_powersetCard.mpr ⟨
        _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
          G S x c 0, h3⟩
  · rcases hcases 1 with h2 | h3
    · apply mem_union_left
      exact mem_powersetCard.mpr ⟨
        _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
          G S x c 1, h2⟩
    · apply mem_union_right
      exact mem_powersetCard.mpr ⟨
        _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
          G S x c 1, h3⟩

omit [Fintype V] in
/-- Each color side has exactly four admissible dense attachment types. -/
theorem card_large_side_types
    (U : Finset V) (hU : U.card = 3) :
    (U.powersetCard 2 ∪ U.powersetCard 3).card = 4 := by
  have hdisj : Disjoint (U.powersetCard 2) (U.powersetCard 3) := by
    rw [Finset.disjoint_left]
    intro A hA2 hA3
    have h2 := (mem_powersetCard.mp hA2).2
    have h3 := (mem_powersetCard.mp hA3).2
    omega
  rw [card_union_of_disjoint hdisj, card_powersetCard, card_powersetCard, hU]
  norm_num

omit [Fintype V] in
/-- Therefore a `3+3` core admits exactly sixteen dense full row types. -/
theorem card_dense_full_row_types
    (U0 U1 : Finset V) (h0 : U0.card = 3) (h1 : U1.card = 3) :
    ((U0.powersetCard 2 ∪ U0.powersetCard 3).product
      (U1.powersetCard 2 ∪ U1.powersetCard 3)).card = 16 := by
  rw [show ((U0.powersetCard 2 ∪ U0.powersetCard 3).product
      (U1.powersetCard 2 ∪ U1.powersetCard 3)).card =
      (U0.powersetCard 2 ∪ U0.powersetCard 3).card *
        (U1.powersetCard 2 ∪ U1.powersetCard 3).card by
        exact Finset.card_product _ _,
    card_large_side_types U0 h0,
    card_large_side_types U1 h1]

omit [Fintype V] in
/-- **Synchronized repetition theorem.** Among seventeen dense outside
vertices, two distinct vertices have the same full two-sided attachment row. -/
theorem seventeen_dense_vertices_force_repeated_full_row
    [DecidableEq W] (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (X : Finset W) (vertex : W → V) (c : V → Fin 2)
    (hX : 17 ≤ X.card)
    (hclass : ∀ k : Fin 2,
      (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
        S c k).card = 3)
    (hdense : ∀ w ∈ X, ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S (vertex w) c k).card) :
    ∃ x ∈ X, ∃ y ∈ X, x ≠ y ∧
      fullAttachmentRow G S (vertex x) c =
        fullAttachmentRow G S (vertex y) c := by
  let U0 := _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
    S c 0
  let U1 := _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
    S c 1
  let T := (U0.powersetCard 2 ∪ U0.powersetCard 3).product
    (U1.powersetCard 2 ∪ U1.powersetCard 3)
  let row : W → Finset V × Finset V := fun w ↦
    fullAttachmentRow G S (vertex w) c
  have hTcard : T.card = 16 := by
    apply card_dense_full_row_types
    · exact hclass 0
    · exact hclass 1
  have hmaps : Set.MapsTo row (X : Set W) (T : Set (Finset V × Finset V)) := by
    intro w hw
    exact fullAttachmentRow_mem_product G S (vertex w) c hclass (hdense w hw)
  have hlt : T.card < X.card := by omega
  obtain ⟨x, hx, y, hy, hxy, hrow⟩ :=
    exists_ne_map_eq_of_card_lt_of_maps_to hlt hmaps
  exact ⟨x, hx, y, hy, hxy, hrow⟩

end WrittenOnTheWallII.GraphConjecture59SynchronizedRows
