import GraphConjecture133ResidualCompletionInterface

/-!
# WOWII 133: the residual completion escapes by endpoint shifting

The 44-vertex residual completion is not an obstruction to the conjectured
path bound.  Vertex `1` has eccentricity four, and the list

`[9, 6, 0, 1, 2, 3, 4, 5]`

is an induced path on eight vertices.  Structurally, the geodesic is
shifted from the frozen `0--5` path to `1--5`; the old endpoint `0`, first
choice `6`, and parent `9` become a clean three-vertex handle in reverse.
-/

namespace WrittenOnTheWallII.GraphConjecture133ResidualAlternativeHandle

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133ResidualCompletionInterface

theorem computable_eccent_one_eq_four :
    computable_eccent completionGraph 1 = 4 := by
  set_option maxRecDepth 100000 in
  decide

theorem completion_radius_toNat_le_four :
    completionGraph.radius.toNat ≤ 4 := by
  rw [radius_eq_computable completionGraph completion_connected]
  simp only [ENat.toNat_coe]
  unfold computable_radius
  calc
    Finset.univ.inf' Finset.univ_nonempty
        (computable_eccent completionGraph) ≤
        computable_eccent completionGraph 1 :=
      Finset.inf'_le _ (Finset.mem_univ 1)
    _ = 4 := computable_eccent_one_eq_four

theorem shifted_endpoint_distance_eq_four :
    completionGraph.dist 1 5 = 4 := by
  rw [completionGraph.dist_eq_computable]
  set_option maxRecDepth 100000 in
  decide

def alternatePath : List Vertex := [9, 6, 0, 1, 2, 3, 4, 5]

theorem alternatePath_isInduced :
    completionGraph.isInducedPath alternatePath := by
  unfold SimpleGraph.isInducedPath alternatePath
  set_option maxRecDepth 100000 in
  decide

/-- A concrete induced-path witness gives a lower bound for the noncomputable
`path` invariant. -/
theorem path_ge_of_isInducedPath
    (G : SimpleGraph Vertex) (xs : List Vertex)
    (hxs : G.isInducedPath xs) : xs.length ≤ path G := by
  classical
  unfold path
  let paths := Finset.univ.filter (fun s : Finset Vertex ↦
    ∃ l : List Vertex, l.toFinset = s ∧ G.isInducedPath l)
  have hmem : xs.toFinset ∈ paths := by
    simp only [paths, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨xs, rfl, hxs⟩
  have hnodup : xs.Nodup := hxs.1
  have hcard : xs.toFinset.card = xs.length :=
    List.toFinset_card_of_nodup hnodup
  have himage : xs.toFinset.card ∈ paths.image Finset.card :=
    Finset.mem_image.mpr ⟨xs.toFinset, hmem, rfl⟩
  obtain ⟨m, hm⟩ := Finset.max_of_mem himage
  rw [← hcard]
  change xs.toFinset.card ≤ (paths.image Finset.card).max.getD 0
  rw [hm]
  simpa using Finset.le_max_of_eq himage hm

theorem eight_le_completion_path : 8 ≤ path completionGraph := by
  exact path_ge_of_isInducedPath completionGraph alternatePath
    alternatePath_isInduced

/-- The exact degree-four C4-free path wall required by WOWII 133 holds on
the calibrated completion. -/
theorem completion_satisfies_radius_add_four_wall :
    completionGraph.radius.toNat + 4 ≤ path completionGraph := by
  calc
    completionGraph.radius.toNat + 4 ≤ 4 + 4 :=
      Nat.add_le_add_right completion_radius_toNat_le_four 4
    _ = 8 := rfl
    _ ≤ path completionGraph := eight_le_completion_path

/-- Concrete structural package: `1--2--3--4--5` realizes distance four,
vertex `1` has eccentricity four, and `9--6--0` is the clean handle prepended
to that geodesic. -/
theorem shifted_endpoint_handle_certificate :
    completionGraph.dist 1 5 = 4 ∧
    completionGraph.radius.toNat ≤ 4 ∧
    completionGraph.isInducedPath [9, 6, 0, 1, 2, 3, 4, 5] := by
  exact ⟨shifted_endpoint_distance_eq_four,
    completion_radius_toNat_le_four, alternatePath_isInduced⟩

end WrittenOnTheWallII.GraphConjecture133ResidualAlternativeHandle
