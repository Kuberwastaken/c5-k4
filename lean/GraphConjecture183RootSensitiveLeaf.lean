import GraphConjecture183TreeTrunkExistence

/-!
# WOWII 183: a leaf distinct from a prescribed root

The missing root-sensitive leaf lemma is proved by degree counting.  If the
root were the only leaf, every other vertex would have degree at least two,
contradicting the tree degree sum `2(n-1)`.
-/

namespace WrittenOnTheWallII.GraphConjecture183RootSensitiveLeaf

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture183OutsideBudget
open WrittenOnTheWallII.GraphConjecture183SelectionExistence
open WrittenOnTheWallII.GraphConjecture183NontrivialTrunk
open WrittenOnTheWallII.GraphConjecture183TreeTrunkExistence

universe u

variable {W : Type u} [Fintype W] [DecidableEq W]

/-- Every finite nontrivial tree has a leaf different from any prescribed
root. -/
theorem IsTree.exists_degree_one_ne [Nontrivial W] (H : SimpleGraph W)
    [DecidableRel H.Adj] (htree : H.IsTree) (r : W) :
    ∃ q : W, q ≠ r ∧ H.degree q = 1 := by
  by_contra h
  push_neg at h
  have hdeg_r : H.degree r = 1 := by
    obtain ⟨q, hq⟩ := htree.exists_vert_degree_one_of_nontrivial
    by_cases hqr : q = r
    · subst q
      exact hq
    · exact ((h q hqr) hq).elim
  have htwo : ∀ v ∈ Finset.univ.erase r, 2 ≤ H.degree v := by
    intro v hv
    have hvr : v ≠ r := (Finset.mem_erase.mp hv).1
    have hpos : 0 < H.degree v :=
      htree.isConnected.preconnected.degree_pos_of_nontrivial v
    have hne : H.degree v ≠ 1 := h v hvr
    omega
  have hsum_erase : 2 * (Finset.univ.erase r).card ≤
      ∑ v ∈ Finset.univ.erase r, H.degree v := by
    calc
      2 * (Finset.univ.erase r).card =
          ∑ _v ∈ Finset.univ.erase r, 2 := by simp [Nat.mul_comm]
      _ ≤ ∑ v ∈ Finset.univ.erase r, H.degree v :=
        Finset.sum_le_sum fun v hv => htwo v hv
  have hsplit : ∑ v : W, H.degree v =
      H.degree r + ∑ v ∈ Finset.univ.erase r, H.degree v := by
    rw [← Finset.sum_erase_add _ _ (Finset.mem_univ r)]
    omega
  have hcard_erase : (Finset.univ.erase r).card + 1 = Fintype.card W := by
    simp [Nat.sub_add_cancel (Fintype.card_pos : 1 ≤ Fintype.card W)]
  have hlarge : 2 * Fintype.card W - 1 ≤ ∑ v : W, H.degree v := by
    rw [hsplit, hdeg_r]
    omega
  have hedge := htree.card_edgeFinset
  have hsum := H.sum_degrees_eq_twice_card_edges
  have hcard : 2 ≤ Fintype.card W := by
    exact (Fintype.one_lt_card_iff_nontrivial.mpr inferInstance)
  omega

/-- The root-sensitive leaf theorem immediately supplies the abstract rooted
leaf-deletion trunk. -/
theorem IsTree.exists_rooted_deleteLeaf_trunk [Nontrivial W]
    (H : SimpleGraph W) [DecidableRel H.Adj] (htree : H.IsTree) (r : W) :
    ∃ q : W,
      r ∈ deleteVertexFinset q ∧
      H.IsConnectedDominating (↑(deleteVertexFinset q) : Set W) ∧
      (deleteVertexFinset q).card + 1 = Fintype.card W := by
  obtain ⟨q, hqr, hdeg⟩ := IsTree.exists_degree_one_ne H htree r
  exact ⟨q,
    rooted_deleteLeaf_trunk H htree.isConnected r q hqr.symm hdeg⟩

end WrittenOnTheWallII.GraphConjecture183RootSensitiveLeaf
