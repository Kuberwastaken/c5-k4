import GraphConjecture59DenseAttachments

/-!
# WOWII 59: pairs of dense outside rows

On a three-by-three core, two dense outside attachment rows must overlap in
each color class: two subsets of a three-set, each of size at least two, cannot
be disjoint.  Hence every pair of exchange-resistant outside vertices has two
distinct common core neighbors, one of each color.  If the outside pair is an
edge, each common neighbor closes a triangle.
-/

namespace WrittenOnTheWallII.GraphConjecture59MultipleOutside

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- Two dense attachment rows overlap inside a three-vertex color class. -/
theorem color_attachment_inter_nonempty
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x y : V) (c : V → Fin 2) (k : Fin 2)
    (hclass : (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
      S c k).card = 3)
    (hx : 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card)
    (hy : 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S y c k).card) :
    (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
      G S x c k ∩
     _root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
      G S y c k).Nonempty := by
  let A := _root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
    G S x c k
  let B := _root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
    G S y c k
  let C := _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
    S c k
  have hAC : A ⊆ C :=
    _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
      G S x c k
  have hBC : B ⊆ C :=
    _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
      G S y c k
  have hunion : (A ∪ B).card ≤ 3 := by
    rw [← hclass]
    exact card_le_card (union_subset hAC hBC)
  have hinclusion := card_union_add_card_inter A B
  have hinter : 1 ≤ (A ∩ B).card := by
    change 2 ≤ A.card at hx
    change 2 ≤ B.card at hy
    omega
  exact card_pos.mp hinter

omit [Fintype V] in
/-- Every pair of dense outside rows has a common neighbor in each core color.
-/
theorem exists_common_neighbor_in_each_color
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x y : V) (c : V → Fin 2)
    (hclass : ∀ k : Fin 2,
      (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
        S c k).card = 3)
    (hx : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card)
    (hy : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S y c k).card) :
    ∀ k : Fin 2, ∃ v ∈ S,
      G.Adj x v ∧ G.Adj y v ∧ c v = k := by
  intro k
  obtain ⟨v, hv⟩ := color_attachment_inter_nonempty
    G S x y c k (hclass k) (hx k) (hy k)
  obtain ⟨hvx, hvy⟩ := mem_inter.mp hv
  have hvx' := mem_filter.mp hvx
  have hvy' := mem_filter.mp hvy
  have hvAttachX := mem_filter.mp hvx'.1
  have hvAttachY := mem_filter.mp hvy'.1
  exact ⟨v, hvAttachX.1, hvAttachX.2, hvAttachY.2, hvx'.2⟩

omit [Fintype V] in
/-- Pair-row structural certificate: there are distinct common neighbors of
opposite core colors. -/
theorem exists_two_distinct_opposite_color_common_neighbors
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x y : V) (c : V → Fin 2)
    (hclass : ∀ k : Fin 2,
      (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
        S c k).card = 3)
    (hx : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card)
    (hy : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S y c k).card) :
    ∃ a ∈ S, ∃ b ∈ S, a ≠ b ∧
      G.Adj x a ∧ G.Adj y a ∧
      G.Adj x b ∧ G.Adj y b ∧
      c a = 0 ∧ c b = 1 := by
  have hcommon := exists_common_neighbor_in_each_color
    G S x y c hclass hx hy
  obtain ⟨a, haS, hxa, hya, hca⟩ := hcommon 0
  obtain ⟨b, hbS, hxb, hyb, hcb⟩ := hcommon 1
  have hab : a ≠ b := by
    intro hab
    subst b
    simp [hca] at hcb
  exact ⟨a, haS, b, hbS, hab, hxa, hya, hxb, hyb, hca, hcb⟩

omit [Fintype V] in
/-- If the two outside vertices are adjacent, each of the opposite-color
common neighbors closes a triangle on that outside edge. -/
theorem adjacent_dense_rows_close_two_triangles
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (x y : V) (c : V → Fin 2)
    (hclass : ∀ k : Fin 2,
      (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
        S c k).card = 3)
    (hx : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S x c k).card)
    (hy : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S y c k).card)
    (hxy : G.Adj x y) :
    ∃ a ∈ S, ∃ b ∈ S, a ≠ b ∧ c a = 0 ∧ c b = 1 ∧
      G.IsClique ({x, y, a} : Finset V) ∧
      G.IsClique ({x, y, b} : Finset V) := by
  obtain ⟨a, haS, b, hbS, hab, hxa, hya, hxb, hyb, hca, hcb⟩ :=
    exists_two_distinct_opposite_color_common_neighbors
      G S x y c hclass hx hy
  refine ⟨a, haS, b, hbS, hab, hca, hcb, ?_, ?_⟩
  · simp only [isClique_iff, coe_insert, coe_singleton]
    intro u hu v hv huv
    simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hu hv
    rcases hu with rfl | rfl | rfl <;>
      rcases hv with rfl | rfl | rfl <;>
      simp_all [hxy.symm, hxa.symm, hya.symm]
  · simp only [isClique_iff, coe_insert, coe_singleton]
    intro u hu v hv huv
    simp only [Set.mem_insert_iff, Set.mem_singleton_iff] at hu hv
    rcases hu with rfl | rfl | rfl <;>
      rcases hv with rfl | rfl | rfl <;>
      simp_all [hxy.symm, hxb.symm, hyb.symm]

end WrittenOnTheWallII.GraphConjecture59MultipleOutside
