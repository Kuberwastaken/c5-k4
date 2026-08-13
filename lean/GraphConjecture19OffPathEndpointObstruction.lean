import GraphConjecture19EndpointIndexPlacement

/-!
# WOWII 19/13: the one-fundamental-endpoint-off-path obstruction
-/

namespace WrittenOnTheWallII.GraphConjecture19OffPathEndpointObstruction

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19DiameterBaseline
open WrittenOnTheWallII.GraphConjecture19FundamentalCycle
open WrittenOnTheWallII.GraphConjecture19FundamentalTriangleBranch
open WrittenOnTheWallII.GraphConjecture19EndpointIndexPlacement

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- If a vertex outside a geodesic is adjacent to two vertices on it, their
indices differ by at most two. -/
lemma natDist_le_two_of_common_off_path_neighbor
    {G : SimpleGraph V} {u v x y c : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) {i k : ℕ}
    (hi : i ≤ p.length) (hk : k ≤ p.length)
    (hix : p.getVert i = x) (hkc : p.getVert k = c)
    (hxy : G.Adj x y) (hcy : G.Adj c y) :
    i.dist k ≤ 2 := by
  have hmetric := dist_getVert_eq_natDist_of_length_eq_dist p hp hi hk
  have hxyDist : G.dist x y = 1 := dist_eq_one_iff_adj.mpr hxy
  have hycDist : G.dist y c = 1 := dist_eq_one_iff_adj.mpr hcy.symm
  have htriangle : G.dist x c ≤ G.dist x y + G.dist y c :=
    hcy.symm.reachable.dist_triangle_right x
  rw [hxyDist, hycDist] at htriangle
  rw [← hmetric, hix, hkc]
  omega

omit [Fintype V] [DecidableEq V] in
/-- In the nontriangle branch, if the right endpoint is off the geodesic but
adjacent to the on-geodesic center, then the left endpoint is either the
center itself or occurs exactly two geodesic steps from it. -/
theorem left_index_eq_center_or_natDist_eq_two
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (c : V) {i k : ℕ}
    (hi : i ≤ p.length) (hk : k ≤ p.length)
    (hiLeft : p.getVert i = D.extraLeft) (hkCenter : p.getVert k = c)
    (hcRight : G.Adj c D.extraRight)
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length) :
    i = k ∨ i.dist k = 2 := by
  have hle : i.dist k ≤ 2 :=
    natDist_le_two_of_common_off_path_neighbor p hp hi hk hiLeft hkCenter
      (D.adj_iff.mpr (Or.inr (Or.inl ⟨rfl, rfl⟩))) hcRight
  have hneOne : i.dist k ≠ 1 := by
    intro hik
    have hLeftCenter : G.Adj D.extraLeft c := by
      apply dist_eq_one_iff_adj.mp
      have hmetric := dist_getVert_eq_natDist_of_length_eq_dist p hp hi hk
      simpa [hiLeft, hkCenter, hik] using hmetric
    obtain ⟨q, hq, _hunique⟩ :=
      WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.existsUnique_fundamentalPath
        D
    have htwo := fundamentalPath_length_eq_two_of_common_neighbor D
      hLeftCenter.symm hcRight q hq
    have := hlong q hq
    omega
  by_cases hik : i = k
  · exact Or.inl hik
  · right
    have hneZero : i.dist k ≠ 0 := fun h => hik (Nat.eq_of_dist_eq_zero h)
    omega

omit [Fintype V] [DecidableEq V] in
/-- Symmetric right-on-path version. -/
theorem right_index_eq_center_or_natDist_eq_two
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (c : V) {j k : ℕ}
    (hj : j ≤ p.length) (hk : k ≤ p.length)
    (hjRight : p.getVert j = D.extraRight) (hkCenter : p.getVert k = c)
    (hcLeft : G.Adj c D.extraLeft)
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length) :
    j = k ∨ j.dist k = 2 := by
  have hle : j.dist k ≤ 2 :=
    natDist_le_two_of_common_off_path_neighbor p hp hj hk hjRight hkCenter
      (D.adj_iff.mpr (Or.inr (Or.inr ⟨rfl, rfl⟩))) hcLeft
  have hneOne : j.dist k ≠ 1 := by
    intro hjk
    have hRightCenter : G.Adj D.extraRight c := by
      apply dist_eq_one_iff_adj.mp
      have hmetric := dist_getVert_eq_natDist_of_length_eq_dist p hp hj hk
      simpa [hjRight, hkCenter, hjk] using hmetric
    obtain ⟨q, hq, _hunique⟩ :=
      WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.existsUnique_fundamentalPath
        D
    have htwo := fundamentalPath_length_eq_two_of_common_neighbor D
      hcLeft hRightCenter.symm q hq
    have := hlong q hq
    omega
  by_cases hjk : j = k
  · exact Or.inl hjk
  · right
    have hneZero : j.dist k ≠ 0 := fun h => hjk (Nat.eq_of_dist_eq_zero h)
    omega

/-- Fully composed refinement of the nontriangle on-path saturation branch.
If the second endpoint falls outside the geodesic, its forced neighborhood
membership restricts the on-path endpoint to the center itself or to exactly
two geodesic steps from the center. -/
theorem refined_fundamental_endpoint_dichotomy_of_on_path_saturation
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (c : V)
    (hcP : c ∈ p.support.toFinset)
    (hsat : p.support.toFinset ∪ G.neighborFinset c = Finset.univ)
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length) :
    (∃ i k : ℕ,
      i ≤ p.length ∧ k ≤ p.length ∧
      p.getVert i = D.extraLeft ∧ p.getVert k = c ∧
      ((∃ j : ℕ, j ≤ p.length ∧ p.getVert j = D.extraRight ∧
          i.dist j = 1) ∨
        (D.extraRight ∉ p.support.toFinset ∧
          D.extraRight ∈ G.neighborFinset c ∧
          (i = k ∨ i.dist k = 2)))) ∨
    (∃ j k : ℕ,
      j ≤ p.length ∧ k ≤ p.length ∧
      p.getVert j = D.extraRight ∧ p.getVert k = c ∧
      ((∃ i : ℕ, i ≤ p.length ∧ p.getVert i = D.extraLeft ∧
          i.dist j = 1) ∨
        (D.extraLeft ∉ p.support.toFinset ∧
          D.extraLeft ∈ G.neighborFinset c ∧
          (j = k ∨ j.dist k = 2)))) := by
  obtain ⟨k, hkCenter, hkLength⟩ := Walk.mem_support_iff_exists_getVert.mp
    (List.mem_toFinset.mp hcP)
  rcases fundamental_endpoint_index_dichotomy_of_on_path_saturation
      D p hp c hsat hlong with hLeft | hRight
  · obtain ⟨i, hiLength, hiLeft, hOther⟩ := hLeft
    refine Or.inl ⟨i, k, hiLength, hkLength, hiLeft, hkCenter, ?_⟩
    rcases hOther with hRightOn | hRightOff
    · exact Or.inl hRightOn
    · refine Or.inr ⟨hRightOff.1, hRightOff.2, ?_⟩
      apply left_index_eq_center_or_natDist_eq_two D p hp c
        hiLength hkLength hiLeft hkCenter
      · simpa [mem_neighborFinset] using hRightOff.2
      · exact hlong
  · obtain ⟨j, hjLength, hjRight, hOther⟩ := hRight
    refine Or.inr ⟨j, k, hjLength, hkLength, hjRight, hkCenter, ?_⟩
    rcases hOther with hLeftOn | hLeftOff
    · exact Or.inl hLeftOn
    · refine Or.inr ⟨hLeftOff.1, hLeftOff.2, ?_⟩
      apply right_index_eq_center_or_natDist_eq_two D p hp c
        hjLength hkLength hjRight hkCenter
      · simpa [mem_neighborFinset] using hLeftOff.2
      · exact hlong

end WrittenOnTheWallII.GraphConjecture19OffPathEndpointObstruction
