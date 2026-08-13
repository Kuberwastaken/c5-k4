import GraphConjecture59ThreeOutside

/-!
# WOWII 59: four or more dense outside rows

There are only four subsets of a three-set having cardinality at least two:
the three two-subsets and the full set.  Consequently four dense attachment
rows either repeat, or three of them share a common core vertex.  This is the
sharp replacement for the false assertion that all four rows must have a
common attachment.
-/

namespace WrittenOnTheWallII.GraphConjecture59ManyOutside

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The exact four-row outcome: a repeated row, or an aligned triple. -/
def RepeatedOrTripleAligned (A B C D : Finset V) : Prop :=
  A = B ∨ A = C ∨ A = D ∨ B = C ∨ B = D ∨ C = D ∨
  (A ∩ B ∩ C).Nonempty ∨ (A ∩ B ∩ D).Nonempty ∨
  (A ∩ C ∩ D).Nonempty ∨ (B ∩ C ∩ D).Nonempty

omit [Fintype V] in
/-- **Four-row pigeonhole theorem.** Four subsets of a three-set, each of size
at least two, either repeat or contain an aligned triple. -/
theorem four_large_subsets_of_three_repeat_or_align
    (U A B C D : Finset V) (hU : U.card = 3)
    (hAU : A ⊆ U) (hBU : B ⊆ U) (hCU : C ⊆ U) (hDU : D ⊆ U)
    (hA : 2 ≤ A.card) (hB : 2 ≤ B.card)
    (hC : 2 ≤ C.card) (hD : 2 ≤ D.card) :
    RepeatedOrTripleAligned A B C D := by
  have habc :=
    _root_.WrittenOnTheWallII.GraphConjecture59ThreeOutside.three_large_subsets_of_three_classification
      U A B C hU hAU hBU hCU hA hB hC
  rcases habc with habc | habc
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl habc))))))
  · obtain ⟨hA2, hB2, hC2, hAB, hAC, hBC⟩ := habc
    have hDupper : D.card ≤ 3 := by
      rw [← hU]
      exact card_le_card hDU
    by_cases hD3 : D.card = 3
    · have hDUeq : D = U := eq_of_subset_of_card_le hDU (by omega)
      have hABinter :=
        _root_.WrittenOnTheWallII.GraphConjecture59ThreeOutside.two_large_subsets_of_three_inter_nonempty
          U A B hU hAU hBU hA hB
      obtain ⟨v, hv⟩ := hABinter
      obtain ⟨hvA, hvB⟩ := mem_inter.mp hv
      have hvD : v ∈ D := by rw [hDUeq]; exact hAU hvA
      have halign : (A ∩ B ∩ D).Nonempty :=
        ⟨v, mem_inter.mpr ⟨mem_inter.mpr ⟨hvA, hvB⟩, hvD⟩⟩
      exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr
        (Or.inr (Or.inl halign)))))))
    · have hD2 : D.card = 2 := by omega
      by_cases hDA : D = A
      · exact Or.inr (Or.inr (Or.inl hDA.symm))
      by_cases hDB : D = B
      · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl hDB.symm))))
      by_cases hDC : D = C
      · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl hDC.symm)))))
      exfalso
      let Q : Finset (Finset V) := {A, B, C, D}
      have hQcard : Q.card = 4 := by
        have hAnot : A ∉ ({B, C, D} : Finset (Finset V)) := by
          simp only [mem_insert, mem_singleton]
          intro h
          rcases h with h | h | h
          · exact hAB h
          · exact hAC h
          · exact hDA h.symm
        have hBnot : B ∉ ({C, D} : Finset (Finset V)) := by
          simp only [mem_insert, mem_singleton]
          intro h
          rcases h with h | h
          · exact hBC h
          · exact hDB h.symm
        have hCnot : C ∉ ({D} : Finset (Finset V)) := by
          simpa only [mem_singleton] using (fun h ↦ hDC h.symm)
        rw [show Q = insert A (insert B (insert C {D})) by rfl,
          card_insert_of_notMem hAnot, card_insert_of_notMem hBnot,
          card_insert_of_notMem hCnot]
        simp
      have hQsub : Q ⊆ U.powersetCard 2 := by
        intro X hX
        simp only [Q, mem_insert, mem_singleton] at hX
        rcases hX with rfl | rfl | rfl | rfl
        · exact mem_powersetCard.mpr ⟨hAU, hA2⟩
        · exact mem_powersetCard.mpr ⟨hBU, hB2⟩
        · exact mem_powersetCard.mpr ⟨hCU, hC2⟩
        · exact mem_powersetCard.mpr ⟨hDU, hD2⟩
      have hQle := card_le_card hQsub
      rw [hQcard, card_powersetCard, hU] at hQle
      norm_num at hQle

omit [Fintype V] in
/-- Specialization to four exchange-resistant outside attachment rows on one
color side of a `3+3` core. -/
theorem four_dense_attachment_rows_repeat_or_align
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (S : Finset V) (w x y z : V) (c : V → Fin 2)
    (hclass : ∀ k : Fin 2,
      (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass
        S c k).card = 3)
    (hw : ∀ k : Fin 2, 2 ≤
      (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
        G S w c k).card)
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
      RepeatedOrTripleAligned
        (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
          G S w c k)
        (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
          G S x c k)
        (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
          G S y c k)
        (_root_.WrittenOnTheWallII.GraphConjecture59CoreExchange.colorAttachments
          G S z c k) := by
  intro k
  apply four_large_subsets_of_three_repeat_or_align
    (_root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorClass S c k)
  · exact hclass k
  · exact
      _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
        G S w c k
  · exact
      _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
        G S x c k
  · exact
      _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
        G S y c k
  · exact
      _root_.WrittenOnTheWallII.GraphConjecture59DenseAttachments.colorAttachments_subset_colorClass
        G S z c k
  · exact hw k
  · exact hx k
  · exact hy k
  · exact hz k

end WrittenOnTheWallII.GraphConjecture59ManyOutside
