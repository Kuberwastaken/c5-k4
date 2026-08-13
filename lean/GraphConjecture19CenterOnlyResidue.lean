import GraphConjecture19DistanceTwoRoute

/-!
# WOWII 19/13: symmetric center-only off-path residue
-/

namespace WrittenOnTheWallII.GraphConjecture19CenterOnlyResidue

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19FundamentalCycle
open WrittenOnTheWallII.GraphConjecture19OffPathEndpointObstruction
open WrittenOnTheWallII.GraphConjecture19DistanceTwoRoute

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- Symmetric edge-transfer lemma: an edge whose endpoints both lie on a walk
avoiding the left added-edge endpoint must already be a tree edge. -/
lemma tree_adj_of_adj_of_mem_support_of_extraLeft_not_mem
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v a b : V} (p : G.Walk u v)
    (ha : a ∈ p.support) (hb : b ∈ p.support)
    (hLeftOff : D.extraLeft ∉ p.support) (hab : G.Adj a b) :
    D.tree.Adj a b := by
  rcases D.adj_iff.mp hab with htree | hextra
  · exact htree
  · rcases hextra with hforward | hbackward
    · exact (hLeftOff (hforward.1 ▸ ha)).elim
    · exact (hLeftOff (hbackward.2 ▸ hb)).elim

omit [Fintype V] [DecidableEq V] in
/-- Left-off-path symmetric route theorem: a distance-two placement between
the right endpoint and the center forces the fundamental tree path to have
length three. -/
theorem fundamentalPath_length_eq_three_of_left_off_of_natDist_eq_two
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (c : V) {j k : ℕ}
    (hj : j ≤ p.length) (hk : k ≤ p.length)
    (hjRight : p.getVert j = D.extraRight) (hkCenter : p.getVert k = c)
    (hjk : j.dist k = 2)
    (hLeftOff : D.extraLeft ∉ p.support)
    (hcLeft : G.Adj c D.extraLeft)
    (q : D.tree.Walk D.extraRight D.extraLeft) (hq : q.IsPath) :
    q.length = 3 := by
  have hcMem : c ∈ p.support := hkCenter ▸ p.getVert_mem_support k
  have hcNeRight : c ≠ D.extraRight := by
    intro hEq
    have hmetric :=
      WrittenOnTheWallII.GraphConjecture19DiameterBaseline.dist_getVert_eq_natDist_of_length_eq_dist
        p hp hj hk
    rw [hjRight, hkCenter, hEq, dist_self, hjk] at hmetric
    omega
  have hleftTree : D.tree.Adj c D.extraLeft := by
    rcases D.adj_iff.mp hcLeft with htree | hextra
    · exact htree
    · rcases hextra with hforward | hbackward
      · exact (hLeftOff (hforward.1 ▸ hcMem)).elim
      · exact (hcNeRight hbackward.1).elim
  have hroute : ∃ r : D.tree.Walk D.extraRight D.extraLeft,
      r.length = 3 ∧ r.IsPath := by
    rcases le_total j k with hjkOrder | hkjOrder
    · have hkEq : k = j + 2 := by
        rw [Nat.dist_eq_sub_of_le hjkOrder] at hjk
        omega
      let m := p.getVert (j + 1)
      have hjSucc : j < p.length := by omega
      have hjOneSucc : j + 1 < p.length := by omega
      have hrightmG : G.Adj D.extraRight m := by
        dsimp [m]
        simpa [hjRight] using p.adj_getVert_succ hjSucc
      have hmcG : G.Adj m c := by
        dsimp [m]
        have hnext := p.adj_getVert_succ hjOneSucc
        have hnextEq : p.getVert (j + 1 + 1) = c := by
          rw [show j + 1 + 1 = k by omega, hkCenter]
        exact hnextEq ▸ hnext
      have hrMem : D.extraRight ∈ p.support := hjRight ▸ p.getVert_mem_support j
      have hmMem : m ∈ p.support := p.getVert_mem_support (j + 1)
      have hrightmT := tree_adj_of_adj_of_mem_support_of_extraLeft_not_mem
        D p hrMem hmMem hLeftOff hrightmG
      have hmcT := tree_adj_of_adj_of_mem_support_of_extraLeft_not_mem
        D p hmMem hcMem hLeftOff hmcG
      let r : D.tree.Walk D.extraRight D.extraLeft :=
        hrightmT.toWalk.append (hmcT.toWalk.append hleftTree.toWalk)
      refine ⟨r, by simp [r], ?_⟩
      rw [Walk.isPath_def]
      simp [r]
      exact ⟨
        ⟨hrightmG.ne, hcNeRight.symm, D.endpoints_ne.symm⟩,
        ⟨hmcG.ne, fun h => hLeftOff (h ▸ hmMem)⟩,
        hcLeft.ne⟩
    · have hjEq : j = k + 2 := by
        rw [Nat.dist_comm, Nat.dist_eq_sub_of_le hkjOrder] at hjk
        omega
      let m := p.getVert (k + 1)
      have hkSucc : k < p.length := by omega
      have hkOneSucc : k + 1 < p.length := by omega
      have hcmG : G.Adj c m := by
        dsimp [m]
        simpa [hkCenter] using p.adj_getVert_succ hkSucc
      have hmrightG : G.Adj m D.extraRight := by
        dsimp [m]
        have hnext := p.adj_getVert_succ hkOneSucc
        have hnextEq : p.getVert (k + 1 + 1) = D.extraRight := by
          rw [show k + 1 + 1 = j by omega, hjRight]
        exact hnextEq ▸ hnext
      have hmMem : m ∈ p.support := p.getVert_mem_support (k + 1)
      have hrMem : D.extraRight ∈ p.support := hjRight ▸ p.getVert_mem_support j
      have hcmT := tree_adj_of_adj_of_mem_support_of_extraLeft_not_mem
        D p hcMem hmMem hLeftOff hcmG
      have hmrightT := tree_adj_of_adj_of_mem_support_of_extraLeft_not_mem
        D p hmMem hrMem hLeftOff hmrightG
      let r : D.tree.Walk D.extraRight D.extraLeft :=
        hmrightT.symm.toWalk.append (hcmT.symm.toWalk.append hleftTree.toWalk)
      refine ⟨r, by simp [r], ?_⟩
      rw [Walk.isPath_def]
      simp [r]
      exact ⟨
        ⟨hmrightG.ne.symm, hcNeRight.symm, D.endpoints_ne.symm⟩,
        ⟨hcmG.ne.symm, fun h => hLeftOff (h ▸ hmMem)⟩,
        hcLeft.ne⟩
  obtain ⟨r, hrLength, hrPath⟩ := hroute
  have hqr :=
    WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.fundamentalPath_unique
      D q r hq hrPath
  rw [hqr, hrLength]

omit [Fintype V] [DecidableEq V] in
/-- The symmetric distance-two residue is impossible in the fundamental
length-at-least-four branch. -/
theorem not_left_off_natDist_eq_two_of_four_le
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (c : V) {j k : ℕ}
    (hj : j ≤ p.length) (hk : k ≤ p.length)
    (hjRight : p.getVert j = D.extraRight) (hkCenter : p.getVert k = c)
    (hLeftOff : D.extraLeft ∉ p.support)
    (hcLeft : G.Adj c D.extraLeft)
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length) :
    j.dist k ≠ 2 := by
  intro hjk
  obtain ⟨q, hq, _hunique⟩ :=
    WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.existsUnique_fundamentalPath
      D
  have hthree := fundamentalPath_length_eq_three_of_left_off_of_natDist_eq_two
    D p hp c hj hk hjRight hkCenter hjk hLeftOff hcLeft q hq
  have := hlong q hq
  omega

omit [Fintype V] [DecidableEq V] in
/-- Combining the symmetric zero-or-two split with the route exclusion leaves
only the center case. -/
theorem right_index_eq_center_of_left_off_of_four_le
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (c : V) {j k : ℕ}
    (hj : j ≤ p.length) (hk : k ≤ p.length)
    (hjRight : p.getVert j = D.extraRight) (hkCenter : p.getVert k = c)
    (hLeftOff : D.extraLeft ∉ p.support)
    (hcLeft : G.Adj c D.extraLeft)
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length) :
    j = k := by
  rcases right_index_eq_center_or_natDist_eq_two D p hp c
      hj hk hjRight hkCenter hcLeft hlong with hjk | htwo
  · exact hjk
  · exact (not_left_off_natDist_eq_two_of_four_le D p hp c
      hj hk hjRight hkCenter hLeftOff hcLeft hlong htwo).elim

omit [Fintype V] [DecidableEq V] in
/-- Unified center-only conclusion.  Once exactly one endpoint of the added
edge is off the geodesic and adjacent to the on-geodesic center, the endpoint
remaining on the geodesic is the center itself. -/
theorem on_path_fundamental_endpoint_eq_center_of_other_off_of_four_le
    {G : SimpleGraph V} (D : TreePlusOneEdge G)
    {u v : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    (c : V)
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length)
    (hplacement :
      (∃ i k : ℕ,
        i ≤ p.length ∧ k ≤ p.length ∧
        p.getVert i = D.extraLeft ∧ p.getVert k = c ∧
        D.extraRight ∉ p.support ∧ G.Adj c D.extraRight) ∨
      (∃ j k : ℕ,
        j ≤ p.length ∧ k ≤ p.length ∧
        p.getVert j = D.extraRight ∧ p.getVert k = c ∧
        D.extraLeft ∉ p.support ∧ G.Adj c D.extraLeft)) :
    D.extraLeft = c ∨ D.extraRight = c := by
  rcases hplacement with hRightOff | hLeftOff
  · obtain ⟨i, k, hi, hk, hiLeft, hkCenter, hRightNot, hcRight⟩ := hRightOff
    left
    have hik := left_index_eq_center_of_right_off_of_four_le D p hp c
      hi hk hiLeft hkCenter hRightNot hcRight hlong
    rw [← hiLeft, ← hkCenter, hik]
  · obtain ⟨j, k, hj, hk, hjRight, hkCenter, hLeftNot, hcLeft⟩ := hLeftOff
    right
    have hjk := right_index_eq_center_of_left_off_of_four_le D p hp c
      hj hk hjRight hkCenter hLeftNot hcLeft hlong
    rw [← hjRight, ← hkCenter, hjk]

end WrittenOnTheWallII.GraphConjecture19CenterOnlyResidue
