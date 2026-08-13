import GraphConjecture59Extraction

/-!
# WOWII 59: the residue-three frontier

The preceding extraction proves WOWII 59 whenever the Havel--Hakimi residue is
at most two.  This file pushes the same theorem shadow through residue three.

The WOWII 40 source baseline `b + 2 <= 2 f` pays the residue-three product as
soon as `f >= 5`.  Combining it with the graph-realizable inequality
`indepNum + 1 <= f` shows that, assuming the classical residue bound
`residue <= indepNum`, the only arithmetic corner not paid at residue at most
three is the exact triple `(residue,b,f) = (3,6,4)`.

The classical residue bound is deliberately an explicit hypothesis: its
general proof is not imported from an upstream declaration containing
`sorry`.
-/

namespace WrittenOnTheWallII.GraphConjecture59Extension

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- A maximum independent set plus one omitted vertex induces a forest. -/
theorem indepNum_add_one_le_largestInducedForestSize
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) :
    G.indepNum + 1 ≤ G.largestInducedForestSize := by
  obtain ⟨I, hI⟩ := G.exists_isNIndepSet_indepNum
  obtain ⟨v, hv⟩ :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.exists_not_mem_of_indep_of_connected
      hconn I hI.isIndepSet
  have hforest :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedForestSize
      G (insert v I)
        (_root_.WrittenOnTheWallII.GraphConjecture40Baseline.induce_insert_isAcyclic_of_indep
          G I v hI.isIndepSet)
  rw [Finset.card_insert_of_notMem hv, hI.card_eq] at hforest
  exact hforest

/-- The WOWII 40 source baseline pays the radicand square through residue
three whenever the induced-forest number is at least five. -/
theorem residue_mul_b_le_forest_square_of_residue_le_three_of_forest_ge_five
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hres : residue G ≤ 3)
    (hfive : 5 ≤ G.largestInducedForestSize) :
    (residue G : ℝ) * b G ≤
      (G.largestInducedForestSize : ℝ) ^ 2 := by
  have hbase :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.largestInducedBipartiteSubgraphSize_add_two_le_two_mul_forestSize
      G hconn Fintype.one_lt_card
  have hbaseR :
      b G + 2 ≤ 2 * (G.largestInducedForestSize : ℝ) := by
    unfold b
    exact_mod_cast hbase
  have hresR : (residue G : ℝ) ≤ 3 := by exact_mod_cast hres
  have hb0 : 0 ≤ b G := by
    unfold b
    positivity
  have hmul : 0 ≤ (3 - (residue G : ℝ)) * b G :=
    mul_nonneg (sub_nonneg.mpr hresR) hb0
  have hfiveR : (5 : ℝ) ≤ G.largestInducedForestSize := by
    exact_mod_cast hfive
  nlinarith [mul_nonneg
    (sub_nonneg.mpr hfiveR)
    (show 0 ≤ (G.largestInducedForestSize : ℝ) - 1 by linarith)]

/-- Upstream-shaped WOWII 59 on the full `residue <= 3, f >= 5` slice. -/
theorem conjecture59_of_residue_le_three_of_forest_ge_five
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hres : residue G ≤ 3)
    (hfive : 5 ≤ G.largestInducedForestSize) :
    ⌈Real.sqrt ((residue G : ℝ) * b G)⌉ ≤
      (G.largestInducedForestSize : ℝ) := by
  apply _root_.WrittenOnTheWallII.GraphConjecture59Extraction.conjecture59_of_product_le_forest_square G
  exact
    residue_mul_b_le_forest_square_of_residue_le_three_of_forest_ge_five
      G hconn hres hfive

/-- Assuming `residue <= indepNum`, every low-residue graph outside the
unresolved `b = 6` corner has the required product certificate. -/
theorem residue_mul_b_le_forest_square_of_residue_le_three_of_b_ne_six
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hres : residue G ≤ 3)
    (hresAlpha : residue G ≤ G.indepNum)
    (hbne : G.largestInducedBipartiteSubgraphSize ≠ 6) :
    (residue G : ℝ) * b G ≤
      (G.largestInducedForestSize : ℝ) ^ 2 := by
  by_cases htwo : residue G ≤ 2
  · exact
      _root_.WrittenOnTheWallII.GraphConjecture59Extraction.residue_mul_b_le_forest_square_of_residue_le_two
        G hconn htwo
  · have hr : residue G = 3 := by omega
    have hforestAlpha := indepNum_add_one_le_largestInducedForestSize G hconn
    have hfour : 4 ≤ G.largestInducedForestSize := by omega
    by_cases hfourEq : G.largestInducedForestSize = 4
    · have hbase :=
        _root_.WrittenOnTheWallII.GraphConjecture40Baseline.largestInducedBipartiteSubgraphSize_add_two_le_two_mul_forestSize
          G hconn Fintype.one_lt_card
      have hbFive : G.largestInducedBipartiteSubgraphSize ≤ 5 := by omega
      unfold b
      rw [hr, hfourEq]
      norm_num
      exact_mod_cast (show
        3 * G.largestInducedBipartiteSubgraphSize ≤ 16 by omega)
    · apply
        residue_mul_b_le_forest_square_of_residue_le_three_of_forest_ge_five
          G hconn hres
      omega

/-- Upstream-shaped residue-three extension.  Under the classical
`residue <= indepNum` inequality, the conjecture holds unless the maximum
induced bipartite order is exactly six. -/
theorem conjecture59_of_residue_le_three_of_b_ne_six
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hres : residue G ≤ 3)
    (hresAlpha : residue G ≤ G.indepNum)
    (hbne : G.largestInducedBipartiteSubgraphSize ≠ 6) :
    ⌈Real.sqrt ((residue G : ℝ) * b G)⌉ ≤
      (G.largestInducedForestSize : ℝ) := by
  apply _root_.WrittenOnTheWallII.GraphConjecture59Extraction.conjecture59_of_product_le_forest_square G
  exact residue_mul_b_le_forest_square_of_residue_le_three_of_b_ne_six
    G hconn hres hresAlpha hbne

/-- Exact frontier classification.  Subject to `residue <= indepNum`, any
failure of the product certificate with residue at most three is forced into
the single invariant triple `(residue,b,f) = (3,6,4)`. -/
theorem failure_with_residue_le_three_forces_exact_corner
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hres : residue G ≤ 3)
    (hresAlpha : residue G ≤ G.indepNum)
    (hfail : ¬((residue G : ℝ) * b G ≤
      (G.largestInducedForestSize : ℝ) ^ 2)) :
    residue G = 3 ∧
      G.largestInducedBipartiteSubgraphSize = 6 ∧
      G.largestInducedForestSize = 4 := by
  have hr : residue G = 3 := by
    by_contra hrne
    have htwo : residue G ≤ 2 := by omega
    exact hfail
      (_root_.WrittenOnTheWallII.GraphConjecture59Extraction.residue_mul_b_le_forest_square_of_residue_le_two
        G hconn htwo)
  have hb : G.largestInducedBipartiteSubgraphSize = 6 := by
    by_contra hbne
    exact hfail
      (residue_mul_b_le_forest_square_of_residue_le_three_of_b_ne_six
        G hconn hres hresAlpha hbne)
  have hforestAlpha := indepNum_add_one_le_largestInducedForestSize G hconn
  have hfour : 4 ≤ G.largestInducedForestSize := by omega
  have hf : G.largestInducedForestSize = 4 := by
    by_contra hfne
    have hfive : 5 ≤ G.largestInducedForestSize := by omega
    exact hfail
      (residue_mul_b_le_forest_square_of_residue_le_three_of_forest_ge_five
        G hconn hres hfive)
  exact ⟨hr, hb, hf⟩

end WrittenOnTheWallII.GraphConjecture59Extension
