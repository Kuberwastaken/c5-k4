import GraphConjecture40Baseline

/-!
# WOWII 59: a low-residue theorem slice

Written on the Wall II Conjecture 59 is false in general.  This file extracts
an unconditional surviving region from the elementary induced-bipartite versus
induced-forest inequality already formalized for WOWII 40.

For a connected nontrivial finite graph, that source inequality says

`b(G) + 2 <= 2 f(G)`.

Consequently `residue(G) <= 2` forces
`residue(G) * b(G) <= f(G)^2`, which is exactly the arithmetic needed for the
conjectured ceiling-square-root bound.  The proof does not use the open
upstream declaration or any other theorem containing `sorry`.
-/

namespace WrittenOnTheWallII.GraphConjecture59Extraction

open SimpleGraph

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [DecidableEq V] in
/-- The exact numerical certificate underlying WOWII 59: once the radicand is
bounded by the square of the induced-forest number, the ceiling contributes no
additional obstruction. -/
theorem conjecture59_of_product_le_forest_square
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hprod : (residue G : ℝ) * b G ≤
      (G.largestInducedForestSize : ℝ) ^ 2) :
    ⌈Real.sqrt ((residue G : ℝ) * b G)⌉ ≤
      (G.largestInducedForestSize : ℝ) := by
  have hceil :
      ⌈Real.sqrt ((residue G : ℝ) * b G)⌉ ≤
        (G.largestInducedForestSize : ℤ) := by
    rw [Int.ceil_le]
    exact Real.sqrt_le_iff.mpr ⟨by positivity, hprod⟩
  exact_mod_cast hceil

/-- The WOWII 40 source baseline implies the complete WOWII 59 product
certificate whenever the Havel--Hakimi residue is at most two. -/
theorem residue_mul_b_le_forest_square_of_residue_le_two
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hres : residue G ≤ 2) :
    (residue G : ℝ) * b G ≤
      (G.largestInducedForestSize : ℝ) ^ 2 := by
  have hbase :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.largestInducedBipartiteSubgraphSize_add_two_le_two_mul_forestSize
      G hconn (Fintype.one_lt_card)
  have hbaseR :
      b G + 2 ≤ 2 * (G.largestInducedForestSize : ℝ) := by
    unfold b
    exact_mod_cast hbase
  have hresR : (residue G : ℝ) ≤ 2 := by
    exact_mod_cast hres
  have hb0 : 0 ≤ b G := by
    unfold b
    positivity
  have hmul : 0 ≤ (2 - (residue G : ℝ)) * b G :=
    mul_nonneg (sub_nonneg.mpr hresR) hb0
  nlinarith [sq_nonneg ((G.largestInducedForestSize : ℝ) - 2)]

/-- A substantial theorem slice of WOWII 59: the conjectured inequality holds
for every connected finite graph whose Havel--Hakimi residue is at most two. -/
theorem conjecture59_of_residue_le_two
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hres : residue G ≤ 2) :
    ⌈Real.sqrt ((residue G : ℝ) * b G)⌉ ≤
      (G.largestInducedForestSize : ℝ) := by
  apply conjecture59_of_product_le_forest_square G
  exact residue_mul_b_le_forest_square_of_residue_le_two G hconn hres

/-- The coefficient two is the limit of this baseline-only argument: the
abstract integer values `b = 4`, `f = 3`, `residue = 3` satisfy the source
baseline but violate its desired product certificate.  This is an arithmetic
countermodel, not a claim that those three values are graph-realizable. -/
theorem source_baseline_alone_does_not_pay_residue_three :
    (4 : ℕ) + 2 ≤ 2 * 3 ∧ ¬((3 : ℕ) * 4 ≤ 3 ^ 2) := by
  norm_num

end WrittenOnTheWallII.GraphConjecture59Extraction
