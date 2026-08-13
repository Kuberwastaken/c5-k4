import GraphConjecture100Extraction

/-!
# WOWII 100: connected finite-residue extraction

This file continues the exact `degreeL2Norm Gᶜ` Lean reading, not the
complement-diameter reading described in the upstream module prose.

When both `G` and `Gᶜ` are connected, `G` contains an induced three-vertex
path.  Its center has two independent neighbors, so the maximum local
independence correction is at least two.  Combining that correction with the
complement-energy lower bound closes the formalized conjecture for
`indepNum G ≥ 14`.
-/

namespace WrittenOnTheWallII.GraphConjecture100FiniteRange

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture100Extraction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The endpoints of an induced length-two path give two independent vertices
in the induced open neighborhood of its center. -/
lemma two_le_indepNeighborsCard_of_induced_path
    (G : SimpleGraph V) (x a b : V)
    (hxa : G.Adj x a) (hab : G.Adj a b)
    (hxb : ¬G.Adj x b) (hneq : x ≠ b) :
    2 ≤ indepNeighborsCard G a := by
  let x' : G.neighborSet a := ⟨x, hxa.symm⟩
  let b' : G.neighborSet a := ⟨b, hab⟩
  have hne' : x' ≠ b' := by
    intro h
    exact hneq (congrArg Subtype.val h)
  have hpair : (G.induce (G.neighborSet a)).IsIndepSet
      (insert x' {b'} : Finset _) := by
    intro u hu v hv huv hadj
    simp at hu hv
    rcases hu with rfl | rfl <;> rcases hv with rfl | rfl
    · exact (huv rfl).elim
    · exact hxb (induce_adj.mp hadj)
    · exact hxb (induce_adj.mp hadj).symm
    · exact (huv rfl).elim
  have hcard := hpair.card_le_indepNum
  simpa [indepNeighborsCard, hne'] using hcard

/-- Connectedness of both a finite nontrivial graph and its complement forces
an induced `P₃`, hence maximum local independence at least two. -/
theorem two_le_max_indepNeighborsCard
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (hGc : Gᶜ.Connected) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    2 ≤ maxL := by
  let x : V := Classical.choice (inferInstance : Nonempty V)
  obtain ⟨z, hxzC⟩ := hGc.preconnected.exists_adj_of_nontrivial x
  have hxzparts : x ≠ z ∧ ¬G.Adj x z := by
    simpa only [compl_adj] using hxzC
  have hxz : ¬G.Adj x z := hxzparts.2
  have hxzne : x ≠ z := hxzC.ne
  have hdist0 : G.dist x z ≠ 0 := by
    intro hzero
    exact hxzne ((hG.dist_eq_zero_iff).mp hzero)
  have hdist1 : G.dist x z ≠ 1 := by
    exact fun hone ↦ hxz (dist_eq_one_iff_adj.mp hone)
  have hdist : 1 < G.dist x z := by omega
  obtain ⟨p, hp⟩ := hG.exists_walk_length_eq_dist x z
  obtain ⟨u, a, b, hua, hab, hub, hubne⟩ :=
    p.exists_adj_adj_not_adj_ne hp hdist
  have hlocal : 2 ≤ indepNeighborsCard G a :=
    two_le_indepNeighborsCard_of_induced_path G u a b hua hab hub hubne
  dsimp
  exact hlocal.trans
    ((Finset.univ.image (indepNeighborsCard G)).le_max'
      (indepNeighborsCard G a) (mem_image_of_mem _ (mem_univ a)))

omit [Fintype V] [DecidableEq V] in
/-- From independence number fourteen onward, the complement-energy lower
bound is within four of the exact residual wall. -/
lemma four_mul_sub_four_lt_sqrt_energy_of_ge_fourteen
    (G : SimpleGraph V) (h14 : 14 ≤ G.indepNum) :
    4 * ((G.indepNum : ℝ) - 1) - 4 <
      Real.sqrt
        ((G.indepNum : ℝ) * ((G.indepNum : ℝ) - 1) ^ 2) := by
  by_cases ha14 : G.indepNum = 14
  · rw [ha14]
    norm_num
    apply (Real.lt_sqrt (by norm_num : (0 : ℝ) ≤ 48)).2
    norm_num
  by_cases ha15 : G.indepNum = 15
  · rw [ha15]
    norm_num
    apply (Real.lt_sqrt (by norm_num : (0 : ℝ) ≤ 52)).2
    norm_num
  have ha16N : 16 ≤ G.indepNum := by omega
  have ha16R : (16 : ℝ) ≤ G.indepNum := by exact_mod_cast ha16N
  have hx : (0 : ℝ) ≤ (G.indepNum : ℝ) - 1 := by linarith
  have henergy : (0 : ℝ) ≤
      (G.indepNum : ℝ) * ((G.indepNum : ℝ) - 1) ^ 2 :=
    mul_nonneg (Nat.cast_nonneg _) (sq_nonneg _)
  have hsqrt : 4 * ((G.indepNum : ℝ) - 1) ≤
      Real.sqrt
        ((G.indepNum : ℝ) * ((G.indepNum : ℝ) - 1) ^ 2) := by
    apply (Real.le_sqrt (mul_nonneg (by norm_num) hx) henergy).2
    have hfactor : (0 : ℝ) ≤
        ((G.indepNum : ℝ) - 16) * ((G.indepNum : ℝ) - 1) ^ 2 :=
      mul_nonneg (sub_nonneg.mpr ha16R) (sq_nonneg _)
    nlinarith
  linarith

omit [Fintype V] [DecidableEq V] in
/-- The other component of the energy-plus-local-correction range: at
independence number two, the residual left after the forced `2L ≥ 4`
correction is zero, while the complement energy is strictly positive. -/
lemma four_mul_sub_four_lt_sqrt_energy_of_eq_two
    (G : SimpleGraph V) (h2 : G.indepNum = 2) :
    4 * ((G.indepNum : ℝ) - 1) - 4 <
      Real.sqrt
        ((G.indepNum : ℝ) * ((G.indepNum : ℝ) - 1) ^ 2) := by
  rw [h2]
  norm_num

/-- The exact formalized WOWII 100 conclusion for the connected finite
residue `indepNum G ≥ 14`.  This strengthens the unconditional `≥ 17`
specialization by using the local correction forced by connectedness of both
graphs. -/
theorem conjecture100_of_connected_of_indepNum_ge_fourteen
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (hGc : Gᶜ.Connected)
    (h14 : 14 ≤ G.indepNum) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  apply conjecture100_of_residual G
  dsimp
  have hlocalN := two_le_max_indepNeighborsCard G hG hGc
  dsimp at hlocalN
  have hlocalR : (2 : ℝ) ≤
      ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
    exact_mod_cast hlocalN
  have hnear := four_mul_sub_four_lt_sqrt_energy_of_ge_fourteen G h14
  have hnorm := sqrt_indep_energy_le_degreeL2Norm_compl G
  linarith

/-- The strongest class obtained from the sharp universal local bound
`maxL ≥ 2` together with complement energy: the exact formalized conjecture
holds when `indepNum G = 2` or `indepNum G ≥ 14`. -/
theorem conjecture100_of_connected_of_indepNum_eq_two_or_ge_fourteen
    (G : SimpleGraph V) [DecidableRel G.Adj] [Nontrivial V]
    (hG : G.Connected) (hGc : Gᶜ.Connected)
    (hrange : G.indepNum = 2 ∨ 14 ≤ G.indepNum) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * degreeL2Norm Gᶜ) / 2⌉ := by
  rcases hrange with h2 | h14
  · apply conjecture100_of_residual G
    dsimp
    have hlocalN := two_le_max_indepNeighborsCard G hG hGc
    dsimp at hlocalN
    have hlocalR : (2 : ℝ) ≤
        ((Finset.univ.image (indepNeighborsCard G)).max' (by simp) : ℝ) := by
      exact_mod_cast hlocalN
    have hnear := four_mul_sub_four_lt_sqrt_energy_of_eq_two G h2
    have hnorm := sqrt_indep_energy_le_degreeL2Norm_compl G
    linarith
  · exact conjecture100_of_connected_of_indepNum_ge_fourteen G hG hGc h14

end WrittenOnTheWallII.GraphConjecture100FiniteRange
