import GraphConjecture59CoreExchange

/-!
# WOWII 59: dense attachment-pattern classification

For a three-by-three bipartite core, the exchange-resistant regime from v0.13
has exactly the four advertised attachment patterns: `2+2`, `2+3`, `3+2`, or
`3+3`.  This file proves that classification symbolically, including the exact
total-size refinement.
-/

namespace WrittenOnTheWallII.GraphConjecture59DenseAttachments

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Vertices of `S` in one color class. -/
def colorClass (S : Finset V) (c : V → Fin 2) (k : Fin 2) : Finset V :=
  S.filter fun y ↦ c y = k

omit [Fintype V] [DecidableEq V] in
/-- Colored attachments are contained in the corresponding core color class.
-/
theorem colorAttachments_subset_colorClass
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2) (k : Fin 2) :
    _root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
      G S x c k ⊆ colorClass S c k := by
  intro y hy
  have hy' := mem_filter.mp hy
  exact mem_filter.mpr ⟨(mem_filter.mp hy'.1).1, hy'.2⟩

omit [Fintype V] [DecidableEq V] in
/-- The two colored attachment sets partition the full attachment set. -/
theorem card_colorAttachments_zero_add_one
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2) :
    (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
      G S x c 0).card +
    (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
      G S x c 1).card =
    (_root_.WrittenOnTheWallII.GraphConjecture59CornerExclusion.attachments
      G S x).card := by
  let A := _root_.WrittenOnTheWallII.GraphConjecture59CornerExclusion.attachments
    G S x
  have hpartition := card_filter_add_card_filter_not
    (s := A) (p := fun y ↦ c y = 0)
  have hone : A.filter (fun y ↦ c y ≠ 0) = A.filter (fun y ↦ c y = 1) := by
    ext y
    simp only [mem_filter]
    constructor
    · rintro ⟨hy, hzero⟩
      exact ⟨hy, Fin.eq_one_of_ne_zero (c y) hzero⟩
    · rintro ⟨hy, hone⟩
      exact ⟨hy, by simp [hone]⟩
  rw [hone] at hpartition
  simpa [A,
    _root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments]
    using hpartition

omit [Fintype V] [DecidableEq V] in
/-- On a `3+3` core, exchange resistance forces each color-side attachment
count to be exactly two or exactly three. -/
theorem each_color_attachment_count_eq_two_or_three
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2)
    (hclass : ∀ k : Fin 2, (colorClass S c k).card = 3)
    (hdense : ∀ k : Fin 2,
      2 ≤ (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card) :
    ∀ k : Fin 2,
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card = 2 ∨
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card = 3 := by
  intro k
  have hupper :
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card ≤ 3 := by
    rw [← hclass k]
    exact card_le_card (colorAttachments_subset_colorClass G S x c k)
  have hlower := hdense k
  omega

omit [Fintype V] [DecidableEq V] in
/-- Exact total-size classification of the dense regime. -/
theorem dense_attachment_pattern_by_total
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x : V) (c : V → Fin 2)
    (hclass : ∀ k : Fin 2, (colorClass S c k).card = 3)
    (hdense : ∀ k : Fin 2,
      2 ≤ (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card) :
    let a := (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
      G S x c 0).card
    let b := (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
      G S x c 1).card
    let t := (_root_.WrittenOnTheWallII.GraphConjecture59CornerExclusion.attachments
      G S x).card
    (t = 4 → a = 2 ∧ b = 2) ∧
    (t = 5 → (a = 2 ∧ b = 3) ∨ (a = 3 ∧ b = 2)) ∧
    (t = 6 → a = 3 ∧ b = 3) ∧
    4 ≤ t ∧ t ≤ 6 := by
  dsimp
  have hcases := each_color_attachment_count_eq_two_or_three
    G S x c hclass hdense
  have hzero := hcases 0
  have hone := hcases 1
  have hsum := card_colorAttachments_zero_add_one G S x c
  omega

end WrittenOnTheWallII.GraphConjecture59DenseAttachments
