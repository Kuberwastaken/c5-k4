import GraphConjecture19FundamentalTriangleBranch
import GraphConjecture19DiameterBaseline

/-!
# WOWII 19: geodesic index placement of the fundamental-edge endpoints
-/

namespace WrittenOnTheWallII.GraphConjecture19EndpointIndexPlacement

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19DiameterBaseline
open WrittenOnTheWallII.GraphConjecture19ExtremalSaturation
open WrittenOnTheWallII.GraphConjecture19FundamentalTriangleBranch

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- Adjacent vertices occurring on a shortest path occur at consecutive
indices. -/
lemma natDist_eq_one_of_adj_getVert_of_geodesic
    {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) {i j : ℕ}
    (hi : i ≤ p.length) (hj : j ≤ p.length)
    (hadj : G.Adj (p.getVert i) (p.getVert j)) :
    i.dist j = 1 := by
  have hmetric := dist_getVert_eq_natDist_of_length_eq_dist p hp hi hj
  have hone : G.dist (p.getVert i) (p.getVert j) = 1 :=
    dist_eq_one_iff_adj.mpr hadj
  omega

omit [Fintype V] [DecidableEq V] in
/-- Support-level form: two adjacent vertices on a geodesic have consecutive
path indices. -/
lemma exists_consecutive_indices_of_adj_mem_geodesic_support
    {G : SimpleGraph V} {u v x y : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v)
    (hx : x ∈ p.support) (hy : y ∈ p.support) (hxy : G.Adj x y) :
    ∃ i j : ℕ,
      i ≤ p.length ∧ j ≤ p.length ∧
      p.getVert i = x ∧ p.getVert j = y ∧ i.dist j = 1 := by
  obtain ⟨i, hi, hiLength⟩ := Walk.mem_support_iff_exists_getVert.mp hx
  obtain ⟨j, hj, hjLength⟩ := Walk.mem_support_iff_exists_getVert.mp hy
  refine ⟨i, j, hiLength, hjLength, hi, hj, ?_⟩
  apply natDist_eq_one_of_adj_getVert_of_geodesic p hp hiLength hjLength
  simpa [hi, hj] using hxy

/-- In the nontriangle on-path saturation branch, the added edge has exactly
two possible placements relative to the diametral geodesic.  One endpoint is
on the geodesic.  Either the other endpoint is also on it, at a consecutive
index, or the other endpoint is genuinely off-path and is forced into the
maximum-degree neighborhood. -/
theorem fundamental_endpoint_index_dichotomy_of_on_path_saturation
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (c : V)
    (hsat : p.support.toFinset ∪ G.neighborFinset c = Finset.univ)
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length) :
    (∃ i : ℕ, i ≤ p.length ∧ p.getVert i = D.extraLeft ∧
      ((∃ j : ℕ, j ≤ p.length ∧ p.getVert j = D.extraRight ∧
          i.dist j = 1) ∨
        (D.extraRight ∉ p.support.toFinset ∧
          D.extraRight ∈ G.neighborFinset c))) ∨
    (∃ j : ℕ, j ≤ p.length ∧ p.getVert j = D.extraRight ∧
      ((∃ i : ℕ, i ≤ p.length ∧ p.getVert i = D.extraLeft ∧
          i.dist j = 1) ∨
        (D.extraLeft ∉ p.support.toFinset ∧
          D.extraLeft ∈ G.neighborFinset c))) := by
  let P := p.support.toFinset
  let N := G.neighborFinset c
  have hone : D.extraLeft ∈ P ∨ D.extraRight ∈ P :=
    endpoint_mem_path_of_on_path_saturation_of_four_le D P c hsat hlong
  have hend := fundamental_endpoints_classified_of_on_path_saturation D P N hsat
  rcases hone with hLeftP | hRightP
  · obtain ⟨i, hiEq, hiLength⟩ := Walk.mem_support_iff_exists_getVert.mp
      (List.mem_toFinset.mp hLeftP)
    refine Or.inl ⟨i, hiLength, hiEq, ?_⟩
    by_cases hRightP : D.extraRight ∈ P
    · obtain ⟨j, hjEq, hjLength⟩ := Walk.mem_support_iff_exists_getVert.mp
        (List.mem_toFinset.mp hRightP)
      refine Or.inl ⟨j, hjLength, hjEq, ?_⟩
      apply natDist_eq_one_of_adj_getVert_of_geodesic p hp hiLength hjLength
      simpa [hiEq, hjEq] using
        (D.adj_iff.mpr (Or.inr (Or.inl ⟨rfl, rfl⟩)))
    · refine Or.inr ⟨hRightP, ?_⟩
      exact hend.2.resolve_left hRightP
  · obtain ⟨j, hjEq, hjLength⟩ := Walk.mem_support_iff_exists_getVert.mp
      (List.mem_toFinset.mp hRightP)
    refine Or.inr ⟨j, hjLength, hjEq, ?_⟩
    by_cases hLeftP : D.extraLeft ∈ P
    · obtain ⟨i, hiEq, hiLength⟩ := Walk.mem_support_iff_exists_getVert.mp
        (List.mem_toFinset.mp hLeftP)
      refine Or.inl ⟨i, hiLength, hiEq, ?_⟩
      apply natDist_eq_one_of_adj_getVert_of_geodesic p hp hiLength hjLength
      simpa [hiEq, hjEq] using
        (D.adj_iff.mpr (Or.inr (Or.inl ⟨rfl, rfl⟩)))
    · refine Or.inr ⟨hLeftP, ?_⟩
      exact hend.1.resolve_left hLeftP

end WrittenOnTheWallII.GraphConjecture19EndpointIndexPlacement
