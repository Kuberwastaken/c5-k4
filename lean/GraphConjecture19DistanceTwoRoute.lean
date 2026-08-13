import GraphConjecture19OffPathEndpointObstruction

/-!
# WOWII 19/13: eliminating the distance-two alternate-route residue
-/

namespace WrittenOnTheWallII.GraphConjecture19DistanceTwoRoute

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19FundamentalCycle
open WrittenOnTheWallII.GraphConjecture19DiameterBaseline
open WrittenOnTheWallII.GraphConjecture19OffPathEndpointObstruction

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- An edge whose endpoints both lie on a walk avoiding the right endpoint of
the added edge must already be a spanning-tree edge. -/
lemma tree_adj_of_adj_of_mem_support_of_extraRight_not_mem
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v a b : V} (p : G.Walk u v)
    (ha : a ∈ p.support) (hb : b ∈ p.support)
    (hRightOff : D.extraRight ∉ p.support) (hab : G.Adj a b) :
    D.tree.Adj a b := by
  rcases D.adj_iff.mp hab with htree | hextra
  · exact htree
  · rcases hextra with hforward | hbackward
    · exact (hRightOff (hforward.2 ▸ hb)).elim
    · exact (hRightOff (hbackward.1 ▸ ha)).elim

omit [Fintype V] [DecidableEq V] in
/-- If the right added-edge endpoint is off a geodesic, while the left
endpoint and an on-geodesic center are exactly two positions apart and the
right endpoint is adjacent to the center, then the fundamental tree path has
length three. -/
theorem fundamentalPath_length_eq_three_of_right_off_of_natDist_eq_two
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v)
    (c : V) {i k : ℕ}
    (hi : i ≤ p.length) (hk : k ≤ p.length)
    (hiLeft : p.getVert i = D.extraLeft) (hkCenter : p.getVert k = c)
    (hik : i.dist k = 2)
    (hRightOff : D.extraRight ∉ p.support)
    (hcRight : G.Adj c D.extraRight)
    (q : D.tree.Walk D.extraRight D.extraLeft) (hq : q.IsPath) :
    q.length = 3 := by
  have hcMem : c ∈ p.support := hkCenter ▸ p.getVert_mem_support k
  have hcNeLeft : c ≠ D.extraLeft := by
    intro hEq
    have hmetric :=
      dist_getVert_eq_natDist_of_length_eq_dist p hp hi hk
    rw [hiLeft, hkCenter, hEq, dist_self, hik] at hmetric
    omega
  have hrightTree : D.tree.Adj c D.extraRight := by
    rcases D.adj_iff.mp hcRight with htree | hextra
    · exact htree
    · rcases hextra with hforward | hbackward
      · exact (hcNeLeft hforward.1).elim
      · exact (hRightOff (hbackward.1 ▸ hcMem)).elim
  have hroute : ∃ r : D.tree.Walk D.extraRight D.extraLeft,
      r.length = 3 ∧ r.IsPath := by
    rcases le_total i k with hikOrder | hkiOrder
    · have hkEq : k = i + 2 := by
        rw [Nat.dist_eq_sub_of_le hikOrder] at hik
        omega
      let m := p.getVert (i + 1)
      have hiSucc : i < p.length := by omega
      have hiOneSucc : i + 1 < p.length := by omega
      have hxmG : G.Adj D.extraLeft m := by
        dsimp [m]
        simpa [hiLeft] using p.adj_getVert_succ hiSucc
      have hmcG : G.Adj m c := by
        dsimp [m]
        have hnext := p.adj_getVert_succ hiOneSucc
        have hnextEq : p.getVert (i + 1 + 1) = c := by
          rw [show i + 1 + 1 = k by omega, hkCenter]
        exact hnextEq ▸ hnext
      have hxMem : D.extraLeft ∈ p.support := hiLeft ▸ p.getVert_mem_support i
      have hmMem : m ∈ p.support := p.getVert_mem_support (i + 1)
      have hxmT := tree_adj_of_adj_of_mem_support_of_extraRight_not_mem
        D p hxMem hmMem hRightOff hxmG
      have hmcT := tree_adj_of_adj_of_mem_support_of_extraRight_not_mem
        D p hmMem hcMem hRightOff hmcG
      let r : D.tree.Walk D.extraRight D.extraLeft :=
        hrightTree.symm.toWalk.append (hmcT.symm.toWalk.append hxmT.symm.toWalk)
      refine ⟨r, by simp [r], ?_⟩
      rw [Walk.isPath_def]
      simp [r]
      exact ⟨
        ⟨hcRight.ne.symm,
          fun h => hRightOff (h ▸ hmMem), D.endpoints_ne.symm⟩,
        ⟨hmcG.ne.symm, hcNeLeft⟩,
        hxmG.ne.symm⟩
    · have hiEq : i = k + 2 := by
        rw [Nat.dist_comm, Nat.dist_eq_sub_of_le hkiOrder] at hik
        omega
      let m := p.getVert (k + 1)
      have hkSucc : k < p.length := by omega
      have hkOneSucc : k + 1 < p.length := by omega
      have hcmG : G.Adj c m := by
        dsimp [m]
        simpa [hkCenter] using p.adj_getVert_succ hkSucc
      have hmxG : G.Adj m D.extraLeft := by
        dsimp [m]
        have hnext := p.adj_getVert_succ hkOneSucc
        have hnextEq : p.getVert (k + 1 + 1) = D.extraLeft := by
          rw [show k + 1 + 1 = i by omega, hiLeft]
        exact hnextEq ▸ hnext
      have hmMem : m ∈ p.support := p.getVert_mem_support (k + 1)
      have hxMem : D.extraLeft ∈ p.support := hiLeft ▸ p.getVert_mem_support i
      have hcmT := tree_adj_of_adj_of_mem_support_of_extraRight_not_mem
        D p hcMem hmMem hRightOff hcmG
      have hmxT := tree_adj_of_adj_of_mem_support_of_extraRight_not_mem
        D p hmMem hxMem hRightOff hmxG
      let r : D.tree.Walk D.extraRight D.extraLeft :=
        hrightTree.symm.toWalk.append (hcmT.toWalk.append hmxT.toWalk)
      refine ⟨r, by simp [r], ?_⟩
      rw [Walk.isPath_def]
      simp [r]
      exact ⟨
        ⟨hcRight.ne.symm,
          fun h => hRightOff (h ▸ hmMem), D.endpoints_ne.symm⟩,
        ⟨hcmG.ne, hcNeLeft⟩,
        hmxG.ne⟩
  obtain ⟨r, hrLength, hrPath⟩ := hroute
  have hqr :=
    WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.fundamentalPath_unique
      D q r hq hrPath
  rw [hqr, hrLength]

omit [Fintype V] [DecidableEq V] in
/-- Hence the distance-two right-off-path residue is impossible when every
fundamental tree path has length at least four. -/
theorem not_right_off_natDist_eq_two_of_four_le
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v)
    (c : V) {i k : ℕ}
    (hi : i ≤ p.length) (hk : k ≤ p.length)
    (hiLeft : p.getVert i = D.extraLeft) (hkCenter : p.getVert k = c)
    (hRightOff : D.extraRight ∉ p.support)
    (hcRight : G.Adj c D.extraRight)
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length) :
    i.dist k ≠ 2 := by
  intro hik
  obtain ⟨q, hq, _hunique⟩ :=
    WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.existsUnique_fundamentalPath
      D
  have hthree := fundamentalPath_length_eq_three_of_right_off_of_natDist_eq_two
    D p hp c hi hk hiLeft hkCenter hik hRightOff hcRight q hq
  have := hlong q hq
  omega

omit [Fintype V] [DecidableEq V] in
/-- Combining v30's zero-or-two split with the route exclusion leaves only
the center case: the on-geodesic left endpoint is exactly the center. -/
theorem left_index_eq_center_of_right_off_of_four_le
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (c : V) {i k : ℕ}
    (hi : i ≤ p.length) (hk : k ≤ p.length)
    (hiLeft : p.getVert i = D.extraLeft) (hkCenter : p.getVert k = c)
    (hRightOff : D.extraRight ∉ p.support)
    (hcRight : G.Adj c D.extraRight)
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length) :
    i = k := by
  rcases left_index_eq_center_or_natDist_eq_two D p hp c
      hi hk hiLeft hkCenter hcRight hlong with hik | htwo
  · exact hik
  · exact (not_right_off_natDist_eq_two_of_four_le D p hp c
      hi hk hiLeft hkCenter hRightOff hcRight hlong htwo).elim

end WrittenOnTheWallII.GraphConjecture19DistanceTwoRoute
