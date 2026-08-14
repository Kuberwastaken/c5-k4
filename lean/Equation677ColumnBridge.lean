import Mathlib.Data.Fintype.Card

/-!
A target-free formalization of the finite column reduction used when searching
for models of Equation 677 that fail Equation 255.
-/

namespace Equation677ColumnBridge

class Magma (α : Type*) where
  op : α → α → α

infix:65 " ◇ " => Magma.op

def Equation677 (α : Type*) [Magma α] : Prop :=
  ∀ x y : α, x = y ◇ (x ◇ ((y ◇ x) ◇ y))

def Equation255At {α : Type*} [Magma α] (x : α) : Prop :=
  x = ((x ◇ x) ◇ x) ◇ x

def leftTranslation {α : Type*} [Magma α] (y : α) : α → α :=
  fun x ↦ y ◇ x

theorem leftTranslation_surjective {α : Type*} [Magma α]
    (h677 : Equation677 α) (y : α) :
    Function.Surjective (leftTranslation y) := by
  intro x
  exact ⟨x ◇ ((y ◇ x) ◇ y), (h677 x y).symm⟩

theorem leftTranslation_injective {α : Type*} [Magma α] [Finite α]
    (h677 : Equation677 α) (y : α) :
    Function.Injective (leftTranslation y) :=
  (Finite.injective_iff_surjective).2 (leftTranslation_surjective h677 y)

theorem fixed_column_implies_equation255At {α : Type*} [Magma α] [Finite α]
    (h677 : Equation677 α) {x y : α} (hy : y ◇ x = x) :
    Equation255At x := by
  have hinj_y := leftTranslation_injective h677 y
  have hinj_x := leftTranslation_injective h677 x
  have hxy : x = x ◇ (x ◇ y) := by
    apply hinj_y
    simpa only [leftTranslation, hy] using h677 x y
  have hxx : x = x ◇ (x ◇ ((x ◇ x) ◇ x)) := h677 x x
  have hinner : x ◇ y = x ◇ ((x ◇ x) ◇ x) := by
    apply hinj_x
    exact hxy.symm.trans hxx
  have hy_unique : y = (x ◇ x) ◇ x := by
    apply hinj_x
    exact hinner
  unfold Equation255At
  rw [← hy_unique]
  exact hy.symm

theorem equation255At_iff_exists_fixed_column {α : Type*} [Magma α] [Finite α]
    (h677 : Equation677 α) (x : α) :
    Equation255At x ↔ ∃ y : α, y ◇ x = x := by
  constructor
  · intro h255
    exact ⟨(x ◇ x) ◇ x, h255.symm⟩
  · rintro ⟨y, hy⟩
    exact fixed_column_implies_equation255At h677 hy

theorem not_equation255At_iff_all_columns_move {α : Type*} [Magma α] [Finite α]
    (h677 : Equation677 α) (x : α) :
    ¬ Equation255At x ↔ ∀ y : α, y ◇ x ≠ x := by
  rw [equation255At_iff_exists_fixed_column h677 x]
  simp only [not_exists]

#print axioms leftTranslation_injective
#print axioms equation255At_iff_exists_fixed_column
#print axioms not_equation255At_iff_all_columns_move

end Equation677ColumnBridge
