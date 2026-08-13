import GraphConjecture133Cubic
import GraphConjecture133TriangleBijection

/-!
# WOWII 133: exact reduction and the complete cubic specialization

The triangle-incidence identity turns the C4-free branch into one explicit
path inequality.  Combining that reduction with the existing C4-free cubic
theorem and the universal `radius + 1 <= path` bound closes the original
source-shaped statement for every connected cubic graph, whether or not it
contains a four-cycle.
-/

namespace WrittenOnTheWallII.GraphConjecture133Specialization

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic
open WrittenOnTheWallII.GraphConjecture133TriangleBijection

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

/-- The exact remaining inequality after eliminating the local-neighborhood
average from the C4-free branch. -/
def TriangleCorrectedPathConclusion (G : SimpleGraph V)
    [DecidableRel G.Adj] : Prop :=
  (G.radius.toNat : ℝ) +
      (⌊(((2 * G.edgeFinset.card - 3 * (G.cliqueFinset 3).card : ℕ) : ℝ) /
          (Fintype.card V : ℝ))⌋ : ℝ) ≤
    (path G : ℝ)

/-- The C4-free branch of the source conclusion before eliminating `l`. -/
def C4FreeBranchConclusion (G : SimpleGraph V)
    [DecidableRel G.Adj] : Prop :=
  (G.radius.toNat : ℝ) + (⌊l G⌋ : ℝ) ≤ (path G : ℝ)

/-- On every finite C4-free graph, WOWII 133 is exactly the
triangle-corrected path inequality.  This is an equivalence, not a new graph
inequality hidden behind an implication. -/
theorem c4FreeBranch_iff_triangleCorrected
    (G : SimpleGraph V) [DecidableRel G.Adj] (hc4 : ¬HasC4 G) :
    C4FreeBranchConclusion G ↔ TriangleCorrectedPathConclusion G := by
  unfold C4FreeBranchConclusion TriangleCorrectedPathConclusion
  rw [l_eq_two_edges_sub_three_triangles_of_c4Free G hc4]

/-- The original upstream proposition, kept local so that this file can state
specializations without importing the still-unproved upstream theorem. -/
noncomputable def SourceConclusion (G : SimpleGraph V)
    [DecidableRel G.Adj] : Prop := by
  classical
  exact
    let hasC4 := ∃ a b c d : V,
      a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
        G.Adj a b ∧ G.Adj b c ∧ G.Adj c d ∧ G.Adj d a
    let cC4 : ℕ := if hasC4 then 0 else 1
    (G.radius.toNat : ℝ) + (⌊l G⌋ : ℝ) ^ cC4 ≤ (path G : ℝ)

/-- Every connected graph containing a (not necessarily induced) four-cycle
satisfies WOWII 133: the characteristic exponent is zero, leaving the
universal `radius + 1 <= path` bound. -/
theorem sourceConclusion_of_hasC4 (G : SimpleGraph V)
    [DecidableRel G.Adj] (hconn : G.Connected) (hc4 : HasC4 G) :
    SourceConclusion G := by
  classical
  simp only [SourceConclusion, HasC4] at hc4 ⊢
  simp only [hc4, ↓reduceIte, pow_zero]
  exact_mod_cast radius_add_one_le_path G hconn

/-- Every connected cubic graph satisfies the full source-shaped WOWII 133
statement.  The C4-containing branch uses only `radius + 1 <= path`; the
C4-free branch is the already proved corrected cubic specialization. -/
theorem cubicSpecialization (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hreg : G.IsRegularOfDegree 3) :
    SourceConclusion G := by
  classical
  by_cases hc4 : HasC4 G
  · exact sourceConclusion_of_hasC4 G hconn hc4
  · simp only [SourceConclusion, HasC4] at hc4 ⊢
    simp only [hc4, ↓reduceIte, pow_one]
    exact cubicC4FreeSpecialization G hconn hreg hc4

end WrittenOnTheWallII.GraphConjecture133Specialization
