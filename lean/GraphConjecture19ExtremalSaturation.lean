import GraphConjecture19FundamentalCycle

/-!
# WOWII 19/13: extremal saturation in the diameter--degree count
-/

namespace WrittenOnTheWallII.GraphConjecture19ExtremalSaturation

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19FundamentalCycle

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Equality in the on-path diameter--degree count forces exact two-vertex
intersection and saturation of the whole vertex set. -/
lemma on_path_extremal_saturation
    (P N : Finset V) (d Delta : ℕ)
    (hP : P.card = d + 1) (hN : N.card = Delta)
    (hinter : (P ∩ N).card ≤ 2)
    (heq : d + Delta = Fintype.card V + 1) :
    (P ∩ N).card = 2 ∧ P ∪ N = Finset.univ := by
  have hunion : (P ∪ N).card ≤ Fintype.card V := (P ∪ N).card_le_univ
  have hcardUnion : (P ∪ N).card =
      d + 1 + Delta - (P ∩ N).card := by
    rw [Finset.card_union, hP, hN]
  have hinterGe : 2 ≤ (P ∩ N).card := by
    rw [hcardUnion] at hunion
    omega
  have hinterEq : (P ∩ N).card = 2 := Nat.le_antisymm hinter hinterGe
  refine ⟨hinterEq, ?_⟩
  apply Finset.eq_univ_of_card
  rw [hcardUnion, hinterEq]
  omega

/-- Equality in the off-path count forces exact three-vertex intersection and
saturation after adjoining the off-path maximum-degree vertex. -/
lemma off_path_extremal_saturation
    (P N : Finset V) (c : V) (d Delta : ℕ)
    (hP : P.card = d + 1) (hN : N.card = Delta)
    (hcP : c ∉ P) (hcN : c ∉ N)
    (hinter : (P ∩ N).card ≤ 3)
    (heq : d + Delta = Fintype.card V + 1) :
    (P ∩ N).card = 3 ∧ insert c (P ∪ N) = Finset.univ := by
  have hcUnion : c ∉ P ∪ N := by simp [hcP, hcN]
  have hunion : (insert c (P ∪ N)).card ≤ Fintype.card V :=
    (insert c (P ∪ N)).card_le_univ
  have hcardUnion : (insert c (P ∪ N)).card =
      1 + (d + 1 + Delta - (P ∩ N).card) := by
    rw [card_insert_of_notMem hcUnion, Finset.card_union, hP, hN]
    omega
  have hinterGe : 3 ≤ (P ∩ N).card := by
    rw [hcardUnion] at hunion
    omega
  have hinterEq : (P ∩ N).card = 3 := Nat.le_antisymm hinter hinterGe
  refine ⟨hinterEq, ?_⟩
  apply Finset.eq_univ_of_card
  rw [hcardUnion, hinterEq]
  omega

/-- Under on-path saturation, both endpoints of the added edge are forced
into the diametral path or the maximum-degree neighborhood. -/
theorem fundamental_endpoints_classified_of_on_path_saturation
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    (P N : Finset V) (hsat : P ∪ N = Finset.univ) :
    (D.extraLeft ∈ P ∨ D.extraLeft ∈ N) ∧
    (D.extraRight ∈ P ∨ D.extraRight ∈ N) := by
  constructor
  · have : D.extraLeft ∈ P ∪ N := by rw [hsat]; simp
    exact Finset.mem_union.mp this
  · have : D.extraRight ∈ P ∪ N := by rw [hsat]; simp
    exact Finset.mem_union.mp this

/-- Under off-path saturation, both endpoints of the added edge are forced
to be the maximum-degree vertex, a path vertex, or its neighbor. -/
theorem fundamental_endpoints_classified_of_off_path_saturation
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    (P N : Finset V) (c : V)
    (hsat : insert c (P ∪ N) = Finset.univ) :
    (D.extraLeft = c ∨ D.extraLeft ∈ P ∨ D.extraLeft ∈ N) ∧
    (D.extraRight = c ∨ D.extraRight ∈ P ∨ D.extraRight ∈ N) := by
  constructor
  · have : D.extraLeft ∈ insert c (P ∪ N) := by rw [hsat]; simp
    simpa [or_assoc] using this
  · have : D.extraRight ∈ insert c (P ∪ N) := by rw [hsat]; simp
    simpa [or_assoc] using this

end WrittenOnTheWallII.GraphConjecture19ExtremalSaturation
