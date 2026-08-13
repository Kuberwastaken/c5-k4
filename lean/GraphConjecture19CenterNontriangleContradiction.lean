import GraphConjecture19ReverseWalkLift
import GraphConjecture19OffPathEndpointObstruction

/-!
# WOWII 19/13: contradiction in the center-attained nontriangle branch
-/

namespace WrittenOnTheWallII.GraphConjecture19CenterNontriangleContradiction

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19UnicyclicDecomposition
open WrittenOnTheWallII.GraphConjecture19FundamentalCycle
open WrittenOnTheWallII.GraphConjecture19CenterTreeAttachment
open WrittenOnTheWallII.GraphConjecture19OffPathEndpointObstruction
open WrittenOnTheWallII.GraphConjecture19DistanceTwoRoute

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] in
/-- In the rigid center-attained geometry, the center and the unique tree
attachment of `extraRight` occur exactly two positions apart on the geodesic. -/
theorem center_attachment_index_distance_eq_two
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {a b : V} (p : G.Walk a b)
    (hp : p.length = G.dist a b)
    (P : Finset V) (c x : V)
    (hP : P = p.support.toFinset)
    (hcLeft : D.extraLeft = c)
    (hcP : c ∈ P) (hxP : x ∈ P) (hxCenter : x ≠ c)
    (hcenter : G.IsIndepSet (G.neighborSet c))
    (hRightX : D.tree.Adj D.extraRight x) :
    ∃ k i : ℕ,
      k ≤ p.length ∧ i ≤ p.length ∧
      p.getVert k = c ∧ p.getVert i = x ∧ k.dist i = 2 := by
  obtain ⟨k, hkCenter, hkLength⟩ := Walk.mem_support_iff_exists_getVert.mp
    (List.mem_toFinset.mp (hP ▸ hcP))
  obtain ⟨i, hiX, hiLength⟩ := Walk.mem_support_iff_exists_getVert.mp
    (List.mem_toFinset.mp (hP ▸ hxP))
  have hcRight : G.Adj c D.extraRight := by
    simpa [← hcLeft] using
      (D.adj_iff.mpr (Or.inr (Or.inl ⟨rfl, rfl⟩)))
  have hxRight : G.Adj x D.extraRight :=
    D.adj_iff.mpr (Or.inl hRightX.symm)
  have hle : k.dist i ≤ 2 :=
    natDist_le_two_of_common_off_path_neighbor p hp
      hkLength hiLength hkCenter hiX hcRight hxRight
  have hneZero : k.dist i ≠ 0 := by
    intro hzero
    have hki : k = i := Nat.eq_of_dist_eq_zero hzero
    apply hxCenter
    rw [← hkCenter, ← hiX, hki]
  have hneOne : k.dist i ≠ 1 := by
    intro hone
    have hmetric :=
      WrittenOnTheWallII.GraphConjecture19DiameterBaseline.dist_getVert_eq_natDist_of_length_eq_dist
        p hp hkLength hiLength
    have hcx : G.Adj c x := by
      apply dist_eq_one_iff_adj.mp
      rw [← hkCenter, ← hiX, hmetric, hone]
    have hrightN : D.extraRight ∈ G.neighborSet c := hcRight
    have hxN : x ∈ G.neighborSet c := hcx
    exact hcenter hrightN hxN hxRight.ne.symm hxRight.symm
  refine ⟨k, i, hkLength, hiLength, hkCenter, hiX, ?_⟩
  omega

/-- The center-attained saturated geometry is impossible when the fundamental
tree path has length at least four.  Equivalently, a nontriangular fundamental
odd cycle cannot realize this equality branch. -/
theorem center_attained_nontriangle_impossible
    {G : SimpleGraph V} [DecidableRel G.Adj]
    (D : TreePlusOneEdge G) {a b : V} (p : G.Walk a b)
    (hp : p.length = G.dist a b)
    (c : V)
    (hcLeft : D.extraLeft = c)
    (hcP : c ∈ p.support.toFinset)
    (hRightOff : D.extraRight ∉ p.support.toFinset)
    (hsat : p.support.toFinset ∪ G.neighborFinset c = Finset.univ)
    (hcenter : G.IsIndepSet (G.neighborSet c))
    (hlong : ∀ (q : D.tree.Walk D.extraRight D.extraLeft),
      q.IsPath → 4 ≤ q.length) : False := by
  obtain ⟨x, hxP, hxCenter, hRightX⟩ :=
    exists_fundamental_tree_attachment_on_path D p.support.toFinset c
      hcLeft hRightOff hsat hcenter
  obtain ⟨k, i, hkLength, hiLength, hkCenter, hiX, hdist⟩ :=
    center_attachment_index_distance_eq_two D p hp p.support.toFinset c x
      rfl hcLeft hcP hxP hxCenter hcenter hRightX
  obtain ⟨q, hq, _hunique⟩ :=
    WrittenOnTheWallII.GraphConjecture19FundamentalCycle.TreePlusOneEdge.existsUnique_fundamentalPath
      D
  have hRightOffList : D.extraRight ∉ p.support := by simpa using hRightOff
  have hthree :=
    fundamentalPath_length_eq_three_of_right_off_of_natDist_eq_two
      D p hp x hkLength hiLength
      (hkCenter.trans hcLeft.symm) hiX hdist
      hRightOffList
      (D.adj_iff.mpr (Or.inl hRightX.symm)) q hq
  have := hlong q hq
  omega

end WrittenOnTheWallII.GraphConjecture19CenterNontriangleContradiction
