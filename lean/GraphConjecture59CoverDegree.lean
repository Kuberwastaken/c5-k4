import GraphConjecture59CompatibilityExchange

/-!
# WOWII 59: degree consequences of complete compatibility covers

When the compatibility exchange fails, three or two neighborhoods cover an
entire candidate pool.  This file converts those exact covers into degree-sum
and high-degree consequences without assuming a residue conclusion.
-/

namespace WrittenOnTheWallII.GraphConjecture59CoverDegree

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture59CompatibilityExchange

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- A three-neighborhood cover bounds the candidate pool by the sum of the
three target degrees. -/
theorem card_le_degree_sum_of_three_cover
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (P : Finset V) (x y z : V)
    (hcover : ∀ p ∈ P, G.Adj p x ∨ G.Adj p y ∨ G.Adj p z) :
    P.card ≤ G.degree x + G.degree y + G.degree z := by
  let X := G.neighborFinset x
  let Y := G.neighborFinset y
  let Z := G.neighborFinset z
  have hsub : P ⊆ (X ∪ Y) ∪ Z := by
    intro p hp
    rcases hcover p hp with hpx | hpy | hpz
    · exact mem_union_left Z
        (mem_union_left Y (by simpa [X, G.mem_neighborFinset, adj_comm] using hpx))
    · exact mem_union_left Z
        (mem_union_right X (by simpa [Y, G.mem_neighborFinset, adj_comm] using hpy))
    · exact mem_union_right (X ∪ Y)
        (by simpa [Z, G.mem_neighborFinset, adj_comm] using hpz)
  calc
    P.card ≤ ((X ∪ Y) ∪ Z).card := card_le_card hsub
    _ ≤ (X ∪ Y).card + Z.card := card_union_le (X ∪ Y) Z
    _ ≤ (X.card + Y.card) + Z.card :=
      Nat.add_le_add_right (card_union_le X Y) Z.card
    _ = G.degree x + G.degree y + G.degree z := by
      simp [X, Y, Z, G.card_neighborFinset_eq_degree]

/-- A two-neighborhood cover gives the analogous sharper degree-sum bound. -/
theorem card_le_degree_sum_of_two_cover
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (Q : Finset V) (a b : V)
    (hcover : ∀ q ∈ Q, G.Adj q a ∨ G.Adj q b) :
    Q.card ≤ G.degree a + G.degree b := by
  let A := G.neighborFinset a
  let B := G.neighborFinset b
  have hsub : Q ⊆ A ∪ B := by
    intro q hq
    rcases hcover q hq with hqa | hqb
    · exact mem_union_left _ (by simpa [A, G.mem_neighborFinset, adj_comm] using hqa)
    · exact mem_union_right _ (by simpa [B, G.mem_neighborFinset, adj_comm] using hqb)
  calc
    Q.card ≤ (A ∪ B).card := card_le_card hsub
    _ ≤ A.card + B.card := card_union_le A B
    _ = G.degree a + G.degree b := by
      simp [A, B, G.card_neighborFinset_eq_degree]

/-- The exact failed outside-side selection from v22 implies the three-degree
sum bound. -/
theorem degree_sum_of_outside_selection_failure
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (P : Finset V) (x y z : V)
    (hfail : outsideSideBlocked G P x y z = P) :
    P.card ≤ G.degree x + G.degree y + G.degree z := by
  apply card_le_degree_sum_of_three_cover G P x y z
  intro p hp
  have : p ∈ outsideSideBlocked G P x y z := by simpa [hfail] using hp
  have hblocked : p ∈ P ∧ (G.Adj p x ∨ G.Adj p y ∨ G.Adj p z) := by
    simpa [outsideSideBlocked] using this
  exact hblocked.2

/-- The exact failed core-side selection implies the two-degree sum bound. -/
theorem degree_sum_of_core_selection_failure
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (Q : Finset V) (a b : V)
    (hfail : coreSideBlocked G Q a b = Q) :
    Q.card ≤ G.degree a + G.degree b := by
  apply card_le_degree_sum_of_two_cover G Q a b
  intro q hq
  have : q ∈ coreSideBlocked G Q a b := by simpa [hfail] using hq
  have hblocked : q ∈ Q ∧ (G.Adj q a ∨ G.Adj q b) := by
    simpa [coreSideBlocked] using this
  exact hblocked.2

/-- Quantitative pigeonhole form: a three-cover of more than `3d` candidates
forces one target degree above `d`. -/
theorem one_degree_gt_of_three_cover
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (P : Finset V) (x y z : V) (d : ℕ)
    (hcover : ∀ p ∈ P, G.Adj p x ∨ G.Adj p y ∨ G.Adj p z)
    (hlarge : 3 * d < P.card) :
    d < G.degree x ∨ d < G.degree y ∨ d < G.degree z := by
  have hsum := card_le_degree_sum_of_three_cover G P x y z hcover
  omega

/-- Quantitative pigeonhole form for the two-cover branch. -/
theorem one_degree_gt_of_two_cover
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (Q : Finset V) (a b : V) (d : ℕ)
    (hcover : ∀ q ∈ Q, G.Adj q a ∨ G.Adj q b)
    (hlarge : 2 * d < Q.card) :
    d < G.degree a ∨ d < G.degree b := by
  have hsum := card_le_degree_sum_of_two_cover G Q a b hcover
  omega

end WrittenOnTheWallII.GraphConjecture59CoverDegree
