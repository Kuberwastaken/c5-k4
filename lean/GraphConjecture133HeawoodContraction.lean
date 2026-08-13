import GraphConjecture133Next

/-!
# WOWII 133: the Heawood edge-contraction hold certificate

Contracting one edge of the Heawood graph gives the explicit thirteen-vertex
graph below.  The contraction remains connected, triangle-free, and C4-free.
Its radius is two and its average local-neighborhood independence is `40/13`,
whose floor is three.  The list `[0, 1, 2, 11, 10]` is an induced path, so the
formalized WOWII 133 target is met exactly at five vertices.

This is a hold certificate for the frozen prospective transformation, not a
proof of the universal conjecture and not a counterexample.
-/

namespace WrittenOnTheWallII.GraphConjecture133HeawoodContraction

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Next

/-- The current source-shaped proposition, reproduced locally so this finite
certificate depends only on the #133 invariant interface. -/
noncomputable def SourceConclusion (G : SimpleGraph (Fin 13))
    [DecidableRel G.Adj] : Prop := by
  classical
  exact
    let hasC4 := HasC4 G
    let cC4 : ℕ := if hasC4 then 0 else 1
    (G.radius.toNat : ℝ) + (⌊l G⌋ : ℝ) ^ cC4 ≤ (path G : ℝ)

/-- Boolean edge table for graph6 `LhcIGCP_GGc@_P`. -/
def contractedHeawoodEdge (u v : ℕ) : Bool :=
  let a := min u v
  let b := max u v
  (a == 0 && b == 1) || (a == 0 && b == 4) ||
  (a == 0 && b == 9) || (a == 0 && b == 12) ||
  (a == 1 && b == 2) || (a == 1 && b == 6) ||
  (a == 2 && b == 3) || (a == 2 && b == 11) ||
  (a == 3 && b == 4) || (a == 3 && b == 8) ||
  (a == 4 && b == 5) || (a == 5 && b == 6) ||
  (a == 5 && b == 10) || (a == 6 && b == 7) ||
  (a == 7 && b == 8) || (a == 7 && b == 12) ||
  (a == 8 && b == 9) || (a == 9 && b == 10) ||
  (a == 10 && b == 11) || (a == 11 && b == 12)

/-- One edge contraction of the Heawood graph.  Vertex `0` is the contracted
endpoint pair and is the unique degree-four vertex; every other vertex has
degree three. -/
def contractedHeawood : SimpleGraph (Fin 13) :=
  SimpleGraph.fromRel fun u v ↦ contractedHeawoodEdge u.1 v.1 = true

instance : DecidableRel contractedHeawood.Adj := by
  unfold contractedHeawood
  infer_instance

theorem contractedHeawood_connected : contractedHeawood.Connected := by
  native_decide

theorem contractedHeawood_c4Free : ¬HasC4 contractedHeawood := by
  unfold HasC4
  native_decide +revert

theorem contractedHeawood_triangleFree : contractedHeawood.CliqueFree 3 := by
  rw [← cliqueFinset_eq_empty_iff]
  native_decide

theorem contractedHeawood_radius : contractedHeawood.radius.toNat = 2 := by
  rw [radius_eq_computable contractedHeawood contractedHeawood_connected]
  native_decide

theorem contractedHeawood_degree_profile (v : Fin 13) :
    contractedHeawood.degree v = if v = 0 then 4 else 3 := by
  fin_cases v <;> native_decide

theorem contractedHeawood_averageDegree :
    averageDegree contractedHeawood = (40 / 13 : ℚ) := by
  unfold averageDegree
  simp_rw [contractedHeawood_degree_profile]
  native_decide

theorem contractedHeawood_l :
    l contractedHeawood = (40 / 13 : ℝ) := by
  rw [l_eq_averageDegree_of_triangleFree contractedHeawood
    contractedHeawood_triangleFree, contractedHeawood_averageDegree]
  norm_num

theorem contractedHeawood_floor_l : ⌊l contractedHeawood⌋ = (3 : ℤ) := by
  rw [contractedHeawood_l]
  norm_num

/-- The decision-first witness found by the frozen exact search. -/
def targetPath : List (Fin 13) := [0, 1, 2, 11, 10]

theorem targetPath_isInduced :
    contractedHeawood.isInducedPath targetPath := by
  unfold SimpleGraph.isInducedPath targetPath
  native_decide

/-- A concrete induced path lower-bounds the repository's `path` invariant. -/
theorem path_ge_of_isInducedPath
    (G : SimpleGraph (Fin 13)) (xs : List (Fin 13))
    (hxs : G.isInducedPath xs) : xs.length ≤ path G := by
  classical
  unfold path
  let paths := Finset.univ.filter (fun s : Finset (Fin 13) ↦
    ∃ ys : List (Fin 13), ys.toFinset = s ∧ G.isInducedPath ys)
  have hmem : xs.toFinset ∈ paths := by
    simp only [paths, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨xs, rfl, hxs⟩
  have hcard : xs.toFinset.card = xs.length :=
    List.toFinset_card_of_nodup hxs.1
  have himage : xs.toFinset.card ∈ paths.image Finset.card :=
    Finset.mem_image.mpr ⟨xs.toFinset, hmem, rfl⟩
  obtain ⟨m, hm⟩ := Finset.max_of_mem himage
  rw [← hcard]
  change xs.toFinset.card ≤ (paths.image Finset.card).max.getD 0
  rw [hm]
  simpa using Finset.le_max_of_eq himage hm

theorem five_le_contractedHeawood_path : 5 ≤ path contractedHeawood := by
  exact path_ge_of_isInducedPath contractedHeawood targetPath targetPath_isInduced

/-- The concrete decision inequality: the radius-plus-local-average target is
five, and the explicit induced path certifies that target. -/
theorem contractedHeawood_radius_add_floor_l_le_path :
    (contractedHeawood.radius.toNat : ℝ) +
        (⌊l contractedHeawood⌋ : ℝ) ≤ (path contractedHeawood : ℝ) := by
  rw [contractedHeawood_radius, contractedHeawood_floor_l]
  exact_mod_cast five_le_contractedHeawood_path

/-- The source-shaped current WOWII 133 proposition holds on this explicit
Heawood contraction. -/
theorem contractedHeawood_sourceConclusion :
    SourceConclusion contractedHeawood := by
  classical
  simp only [SourceConclusion]
  simp only [contractedHeawood_c4Free, ↓reduceIte, pow_one]
  exact contractedHeawood_radius_add_floor_l_le_path

/-- Complete reusable finite certificate for the rejected one-off move. -/
theorem contractedHeawood_hold_certificate :
    contractedHeawood.Connected ∧
    ¬HasC4 contractedHeawood ∧
    contractedHeawood.radius.toNat = 2 ∧
    ⌊l contractedHeawood⌋ = (3 : ℤ) ∧
    contractedHeawood.isInducedPath [0, 1, 2, 11, 10] ∧
    5 ≤ path contractedHeawood ∧
    SourceConclusion contractedHeawood := by
  exact ⟨contractedHeawood_connected, contractedHeawood_c4Free,
    contractedHeawood_radius, contractedHeawood_floor_l,
    targetPath_isInduced, five_le_contractedHeawood_path,
    contractedHeawood_sourceConclusion⟩

end WrittenOnTheWallII.GraphConjecture133HeawoodContraction
