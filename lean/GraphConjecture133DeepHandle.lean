import GraphConjecture133DegreeFour

/-!
# WOWII 133: deep-handle sufficient conditions

The degree-four wall needs three vertices beyond a radius geodesic's support.
This file states local clean-handle data that really do assemble into the
required induced path, and packages both one-ended and two-ended sufficient
classes for the exact source proposition.
-/

namespace WrittenOnTheWallII.GraphConjecture133DeepHandle

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic
open WrittenOnTheWallII.GraphConjecture133Regular
open WrittenOnTheWallII.GraphConjecture133Specialization

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

/-- A clean three-vertex handle attached to the head of a radius geodesic.
Each successive new vertex is fresh and has no forbidden contact with the
tail already constructed. -/
def HasCleanRadiusThreeHandle (G : SimpleGraph V) : Prop :=
  ∃ (u v : V) (p : G.Walk u v) (a b c : V),
    p.length = G.dist u v ∧
    p.length = G.radius.toNat ∧
    G.Adj c u ∧ c ∉ p.support ∧
      (∀ x ∈ p.support.tail, ¬G.Adj c x) ∧
    G.Adj b c ∧ b ∉ c :: p.support ∧
      (∀ x ∈ p.support, ¬G.Adj b x) ∧
    G.Adj a b ∧ a ∉ b :: c :: p.support ∧
      (∀ x ∈ c :: p.support, ¬G.Adj a x)

omit [Nonempty V] in
/-- The clean-handle data assemble, rung by rung, into an induced path with
`radius + 4` vertices. -/
lemma radius_add_four_le_path_of_cleanThreeHandle
    (G : SimpleGraph V) (hh : HasCleanRadiusThreeHandle G) :
    G.radius.toNat + 4 ≤ path G := by
  obtain ⟨u, v, p, a, b, c, hpDist, hpRadius, hcu, hcfresh, hcclean,
    hbc, hbfresh, hbclean, hab, hafresh, haclean⟩ := hh
  have hpInduced : G.isInducedPath p.support :=
    isInducedPath_support_of_length_eq_dist p hpDist
  have hcInduced : G.isInducedPath (c :: p.support) := by
    rw [p.support_eq_cons]
    apply isInducedPath_cons_of_adj_head_of_not_adj_tail
    · simpa [← p.support_eq_cons] using hpInduced
    · exact hcu
    · simpa [← p.support_eq_cons] using hcfresh
    · exact hcclean
  have hbInduced : G.isInducedPath (b :: c :: p.support) := by
    apply isInducedPath_cons_of_adj_head_of_not_adj_tail hcInduced hbc hbfresh
    exact hbclean
  have haInduced : G.isInducedPath (a :: b :: c :: p.support) := by
    apply isInducedPath_cons_of_adj_head_of_not_adj_tail hbInduced hab hafresh
    exact haclean
  have hlength : (a :: b :: c :: p.support).length = G.radius.toNat + 4 := by
    simp [p.length_support, hpRadius]
  rw [← hlength]
  exact path_ge_of_isInducedPath G (a :: b :: c :: p.support) haInduced

/-- A two-ended alternative: two vertices on one side and one on the other.
The induced-list condition is deliberately explicit because cross-end
contacts are the extra compatibility issue absent from the one-ended handle. -/
def HasInducedRadiusTwoEndedHandle (G : SimpleGraph V) : Prop :=
  ∃ (u v : V) (p : G.Walk u v) (a b c : V),
    p.length = G.radius.toNat ∧
    G.isInducedPath (a :: b :: (p.support ++ [c]))

omit [Nonempty V] in
/-- An induced two-ended handle also has exactly `radius + 4` vertices. -/
lemma radius_add_four_le_path_of_twoEndedHandle
    (G : SimpleGraph V) (hh : HasInducedRadiusTwoEndedHandle G) :
    G.radius.toNat + 4 ≤ path G := by
  obtain ⟨u, v, p, a, b, c, hpRadius, hpInduced⟩ := hh
  have hlength : (a :: b :: (p.support ++ [c])).length =
      G.radius.toNat + 4 := by
    simp [p.length_support, hpRadius]
  rw [← hlength]
  exact path_ge_of_isInducedPath G (a :: b :: (p.support ++ [c])) hpInduced

/-- The strongest one-ended structural class obtained in this checkpoint:
connected four-regular triangle-free graphs satisfy the exact source
conclusion whenever either the exponent-zero C4 branch applies or a clean
radius three-handle exists. -/
theorem degreeFourSpecialization_of_cleanThreeHandle
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hreg : G.IsRegularOfDegree 4)
    (htri : G.CliqueFree 3)
    (hh : WrittenOnTheWallII.GraphConjecture133Cubic.HasC4 G ∨
      HasCleanRadiusThreeHandle G) :
    SourceConclusion G := by
  rcases hh with hc4 | hhandle
  · exact sourceConclusion_of_hasC4 G hconn hc4
  · by_cases hc4 : WrittenOnTheWallII.GraphConjecture133Cubic.HasC4 G
    · exact sourceConclusion_of_hasC4 G hconn hc4
    · apply sourceConclusion_of_regular_triangleFree_pathWall G 4 hreg htri hc4
      exact radius_add_four_le_path_of_cleanThreeHandle G hhandle

/-- Parallel exact source theorem for the compatible two-ended class. -/
theorem degreeFourSpecialization_of_twoEndedHandle
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hconn : G.Connected) (hreg : G.IsRegularOfDegree 4)
    (htri : G.CliqueFree 3)
    (hh : WrittenOnTheWallII.GraphConjecture133Cubic.HasC4 G ∨
      HasInducedRadiusTwoEndedHandle G) :
    SourceConclusion G := by
  rcases hh with hc4 | hhandle
  · exact sourceConclusion_of_hasC4 G hconn hc4
  · by_cases hc4 : WrittenOnTheWallII.GraphConjecture133Cubic.HasC4 G
    · exact sourceConclusion_of_hasC4 G hconn hc4
    · apply sourceConclusion_of_regular_triangleFree_pathWall G 4 hreg htri hc4
      exact radius_add_four_le_path_of_twoEndedHandle G hhandle

end WrittenOnTheWallII.GraphConjecture133DeepHandle
