import FormalConjecturesUtil

/-!
# Optimal-coloring shape at the Reed carrier boundary

The prospective color-blocker search relies on a small but rigid counting
fact.  On fifteen vertices, an eight-coloring whose color classes have size at
most two must consist of seven pairs and one singleton, provided every color
is used.  This file isolates that fact and then derives the graph-theoretic
version from `α(G) ≤ 2` and `χ(G) = 8`.
-/

namespace ReedOptimalColoringShape

open Function SimpleGraph
open scoped BigOperators

/-- The vertices assigned color `i`, as a finite set. -/
def colorClassFinset {V : Type*} [Fintype V] [DecidableEq V]
    {G : SimpleGraph V} (C : G.Coloring (Fin 8)) (i : Fin 8) : Finset V :=
  Finset.univ.filter fun v ↦ C v = i

/-- Pure eight-bin counting lemma: eight nonempty bins of capacity two and
total size fifteen are seven pairs plus one singleton. -/
lemma eight_bins_of_total_fifteen (s : Fin 8 → ℕ)
    (hpos : ∀ i, 1 ≤ s i) (hcap : ∀ i, s i ≤ 2)
    (hsum : ∑ i, s i = 15) :
    ∃ i, s i = 1 ∧ ∀ j, j ≠ i → s j = 2 := by
  have hp0 := hpos 0
  have hp1 := hpos 1
  have hp2 := hpos 2
  have hp3 := hpos 3
  have hp4 := hpos 4
  have hp5 := hpos 5
  have hp6 := hpos 6
  have hp7 := hpos 7
  have hc0 := hcap 0
  have hc1 := hcap 1
  have hc2 := hcap 2
  have hc3 := hcap 3
  have hc4 := hcap 4
  have hc5 := hcap 5
  have hc6 := hcap 6
  have hc7 := hcap 7
  have hs :
      s 0 + (s 1 + (s 2 + (s 3 + (s 4 + (s 5 + (s 6 + s 7)))))) = 15 := by
    simpa [Fin.sum_univ_succ] using hsum
  have hone : s 0 = 1 ∨ s 1 = 1 ∨ s 2 = 1 ∨ s 3 = 1 ∨
      s 4 = 1 ∨ s 5 = 1 ∨ s 6 = 1 ∨ s 7 = 1 := by
    omega
  rcases hone with h | h | h | h | h | h | h | h
  · refine ⟨0, h, ?_⟩
    have hall : s 1 = 2 ∧ s 2 = 2 ∧ s 3 = 2 ∧ s 4 = 2 ∧
        s 5 = 2 ∧ s 6 = 2 ∧ s 7 = 2 := by omega
    intro j hj
    fin_cases j <;> simp_all
  · refine ⟨1, h, ?_⟩
    have hall : s 0 = 2 ∧ s 2 = 2 ∧ s 3 = 2 ∧ s 4 = 2 ∧
        s 5 = 2 ∧ s 6 = 2 ∧ s 7 = 2 := by omega
    intro j hj
    fin_cases j <;> simp_all
  · refine ⟨2, h, ?_⟩
    have hall : s 0 = 2 ∧ s 1 = 2 ∧ s 3 = 2 ∧ s 4 = 2 ∧
        s 5 = 2 ∧ s 6 = 2 ∧ s 7 = 2 := by omega
    intro j hj
    fin_cases j <;> simp_all
  · refine ⟨3, h, ?_⟩
    have hall : s 0 = 2 ∧ s 1 = 2 ∧ s 2 = 2 ∧ s 4 = 2 ∧
        s 5 = 2 ∧ s 6 = 2 ∧ s 7 = 2 := by omega
    intro j hj
    fin_cases j <;> simp_all
  · refine ⟨4, h, ?_⟩
    have hall : s 0 = 2 ∧ s 1 = 2 ∧ s 2 = 2 ∧ s 3 = 2 ∧
        s 5 = 2 ∧ s 6 = 2 ∧ s 7 = 2 := by omega
    intro j hj
    fin_cases j <;> simp_all
  · refine ⟨5, h, ?_⟩
    have hall : s 0 = 2 ∧ s 1 = 2 ∧ s 2 = 2 ∧ s 3 = 2 ∧
        s 4 = 2 ∧ s 6 = 2 ∧ s 7 = 2 := by omega
    intro j hj
    fin_cases j <;> simp_all
  · refine ⟨6, h, ?_⟩
    have hall : s 0 = 2 ∧ s 1 = 2 ∧ s 2 = 2 ∧ s 3 = 2 ∧
        s 4 = 2 ∧ s 5 = 2 ∧ s 7 = 2 := by omega
    intro j hj
    fin_cases j <;> simp_all
  · refine ⟨7, h, ?_⟩
    have hall : s 0 = 2 ∧ s 1 = 2 ∧ s 2 = 2 ∧ s 3 = 2 ∧
        s 4 = 2 ∧ s 5 = 2 ∧ s 6 = 2 := by omega
    intro j hj
    fin_cases j <;> simp_all

/-- If all permutations of an eight-color palette occur equally often as the
singleton color across a finite family of colorings, then every color occurs
as singleton with frequency one eighth of the family size.

This is the honest symmetry boundary used by reuse arguments: the equality is
proved from the explicit equal-frequency premise, rather than inferred merely
from vertex transitivity. -/
lemma singleton_frequency_of_palette_symmetry
    {Ω : Type*} [Fintype Ω] (singleton : Ω → Fin 8)
    (hbalanced : ∀ i j,
      (Finset.univ.filter fun c ↦ singleton c = i).card =
        (Finset.univ.filter fun c ↦ singleton c = j).card) (i : Fin 8) :
    8 * (Finset.univ.filter fun c ↦ singleton c = i).card = Fintype.card Ω := by
  have hsum := Finset.card_eq_sum_card_fiberwise
    (s := (Finset.univ : Finset Ω)) (t := (Finset.univ : Finset (Fin 8)))
    (f := singleton) (by simp)
  rw [Finset.card_univ] at hsum
  calc
    8 * (Finset.univ.filter fun c ↦ singleton c = i).card =
        ∑ j : Fin 8, (Finset.univ.filter fun c ↦ singleton c = j).card := by
          symm
          calc
            (∑ j : Fin 8,
                (Finset.univ.filter fun c ↦ singleton c = j).card) =
                ∑ _j : Fin 8,
                  (Finset.univ.filter fun c ↦ singleton c = i).card := by
                    apply Finset.sum_congr rfl
                    intro j _hj
                    exact hbalanced j i
            _ = 8 * (Finset.univ.filter fun c ↦ singleton c = i).card := by
                  simp
    _ = Fintype.card Ω := hsum.symm

/-- Every optimal eight-coloring of a fifteen-vertex graph with independence
number at most two has exactly seven two-vertex color classes and one
singleton color class. -/
theorem optimal_eight_coloring_shape {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hcard : Fintype.card V = 15) (halpha : G.indepNum ≤ 2)
    (hchi : G.chromaticNumber = (8 : ℕ∞)) (C : G.Coloring (Fin 8)) :
    ∃ i, (colorClassFinset C i).card = 1 ∧
      ∀ j, j ≠ i → (colorClassFinset C j).card = 2 := by
  have hsurj : Surjective C := by
    apply (le_chromaticNumber_iff_forall_surjective (G := G) (n := 8)).mp
      (show (8 : ℕ∞) ≤ G.chromaticNumber by rw [hchi]) C
  have hpos : ∀ i, 1 ≤ (colorClassFinset C i).card := by
    intro i
    obtain ⟨v, hv⟩ := hsurj i
    exact Finset.one_le_card.mpr ⟨v, by simp [colorClassFinset, hv]⟩
  have hcap : ∀ i, (colorClassFinset C i).card ≤ 2 := by
    intro i
    have hindep : G.IsIndepSet (colorClassFinset C i) := by
      intro u hu v hv huv
      have hu' : C u = i := by simpa [colorClassFinset] using hu
      have hv' : C v = i := by simpa [colorClassFinset] using hv
      exact C.not_adj_of_mem_colorClass (c := i) hu' hv'
    exact hindep.card_le_indepNum.trans halpha
  have hsum : ∑ i, (colorClassFinset C i).card = 15 := by
    have hfib := Finset.card_eq_sum_card_fiberwise
      (s := (Finset.univ : Finset V)) (t := (Finset.univ : Finset (Fin 8)))
      (f := C) (by simp)
    change (∑ i : Fin 8,
      ((Finset.univ : Finset V).filter fun v ↦ C v = i).card) = 15
    rw [← hfib, Finset.card_univ, hcard]
  exact eight_bins_of_total_fifteen
    (fun i ↦ (colorClassFinset C i).card) hpos hcap hsum

end ReedOptimalColoringShape
