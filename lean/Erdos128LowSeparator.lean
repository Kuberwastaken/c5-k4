import FormalConjecturesUtil

/-!
# Erdős 128: low-separator induced-density obstruction

The computational Hajós example is an instance of a general witness argument.
If an eligible vertex set is assembled from two disjoint local pieces, and
the two internal edge budgets plus the separator/crossing budget remain below
the global strict threshold, then that set refutes the universal premise in
the current formalization of Erdős Problem 128.

This file deliberately separates the graph-specific construction of the local
pieces from the finite-set arithmetic that makes low-separator compositions
directionally hostile to the conjecture's premise.
-/

namespace Erdos128.LowSeparator

open SimpleGraph

universe u

/-- A single eligible induced subgraph whose certified edge upper bound is at
most the global threshold refutes the strict-density premise. -/
theorem strict_density_premise_fails_of_eligible_edge_bound
    {W : Type u} [Fintype W] (H : SimpleGraph W) (S : Set W) (q : ℕ)
    (heligible : 2 * S.ncard + 1 ≥ Fintype.card W)
    (hedges : (H.induce S).edgeSet.ncard ≤ q)
    (hthreshold : 50 * q ≤ Fintype.card W ^ 2) :
    ¬(∀ T : Set W, 2 * T.ncard + 1 ≥ Fintype.card W →
        50 * (H.induce T).edgeSet.ncard > Fintype.card W ^ 2) := by
  intro hpremise
  have hstrict := hpremise S heligible
  have hscaled : 50 * (H.induce S).edgeSet.ncard ≤ 50 * q := by
    exact Nat.mul_le_mul_left 50 hedges
  omega

/-- Abstract low-separator composition lemma.  The local induced-edge bounds
and every edge crossing the separator are summarized by `eA`, `eB`, and `c`.
Once their sum is below the global threshold, the disjoint union of the local
witness sets refutes the strict-density premise. -/
theorem strict_density_premise_fails_of_low_separator_union
    {W : Type u} [Fintype W] [DecidableEq W]
    (H : SimpleGraph W) (A B : Finset W) (eA eB c : ℕ)
    (hdisjoint : Disjoint A B)
    (heligible : 2 * (A.card + B.card) + 1 ≥ Fintype.card W)
    (hedges :
      (H.induce (↑(A ∪ B) : Set W)).edgeSet.ncard ≤ eA + eB + c)
    (hthreshold : 50 * (eA + eB + c) ≤ Fintype.card W ^ 2) :
    ¬(∀ T : Set W, 2 * T.ncard + 1 ≥ Fintype.card W →
        50 * (H.induce T).edgeSet.ncard > Fintype.card W ^ 2) := by
  apply strict_density_premise_fails_of_eligible_edge_bound
    H (↑(A ∪ B) : Set W) (eA + eB + c)
  · have hunioncard : (↑(A ∪ B) : Set W).ncard = A.card + B.card := by
      rw [Set.ncard_coe_finset, Finset.card_union_of_disjoint hdisjoint]
    rw [hunioncard]
    exact heligible
  · exact hedges
  · exact hthreshold

/-- The exact arithmetic adapter for the recorded 19-vertex Hajós witness:
any nine-vertex induced subgraph with at most two edges already makes the
strict Erdős 128 premise false. -/
theorem order_nineteen_two_edge_witness_fails
    {W : Type u} [Fintype W] [DecidableEq W]
    (H : SimpleGraph W) (S : Finset W)
    (horder : Fintype.card W = 19)
    (hcard : S.card = 9)
    (hedges : (H.induce (↑S : Set W)).edgeSet.ncard ≤ 2) :
    ¬(∀ T : Set W, 2 * T.ncard + 1 ≥ Fintype.card W →
        50 * (H.induce T).edgeSet.ncard > Fintype.card W ^ 2) := by
  apply strict_density_premise_fails_of_eligible_edge_bound H (↑S : Set W) 2
  · norm_num [Set.ncard_coe_finset, hcard, horder]
  · exact hedges
  · norm_num [horder]

#print axioms strict_density_premise_fails_of_eligible_edge_bound
#print axioms strict_density_premise_fails_of_low_separator_union
#print axioms order_nineteen_two_edge_witness_fails

end Erdos128.LowSeparator
