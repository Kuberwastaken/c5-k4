import GraphConjecture19DiameterDegree

/-!
# WOWII 19/13: metric path-neighborhood intersection bound
-/

namespace WrittenOnTheWallII.GraphConjecture19MetricIntersection

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19DiameterDegree
open WrittenOnTheWallII.GraphConjecture19DiameterBaseline

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- A finite set of natural indices with pairwise distance at most two has at
most three members. -/
lemma card_le_three_of_pairwise_natDist_le_two (I : Finset ℕ)
    (hpair : ∀ i ∈ I, ∀ j ∈ I, i.dist j ≤ 2) :
    I.card ≤ 3 := by
  by_cases hI : I.Nonempty
  · let m := I.min' hI
    let J := I.image (fun i => i - m)
    have hinj : Set.InjOn (fun i => i - m) (I : Set ℕ) := by
      intro i hi j hj hij
      rw [Finset.mem_coe] at hi hj
      have hmi : m ≤ i := Finset.min'_le I i hi
      have hmj : m ≤ j := Finset.min'_le I j hj
      dsimp only at hij
      omega
    have hcard : J.card = I.card := by
      dsimp [J]
      exact Finset.card_image_iff.mpr hinj
    have hsub : J ⊆ Finset.range 3 := by
      intro x hx
      obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
      have hm : m ∈ I := Finset.min'_mem I hI
      have hmi : m ≤ i := Finset.min'_le I i hi
      have hd := hpair m hm i hi
      rw [Nat.dist_eq_sub_of_le hmi] at hd
      simp only [Finset.mem_range]
      omega
    rw [← hcard]
    exact (Finset.card_le_card hsub).trans_eq (Finset.card_range 3)
  · simp only [Finset.not_nonempty_iff_eq_empty] at hI
    simp [hI]

/-- Indices at natural distance exactly one from one fixed index form a set of
cardinality at most two. -/
lemma card_le_two_of_natDist_eq_one (I : Finset ℕ) (k : ℕ)
    (hdist : ∀ i ∈ I, k.dist i = 1) :
    I.card ≤ 2 := by
  have hsub : I ⊆ {k - 1, k + 1} := by
    intro i hi
    have hd := hdist i hi
    rcases le_total k i with hki | hik
    · rw [Nat.dist_eq_sub_of_le hki] at hd
      have : i = k + 1 := by omega
      simp [this]
    · rw [Nat.dist_comm, Nat.dist_eq_sub_of_le hik] at hd
      have : i = k - 1 := by omega
      simp [this]
  exact (Finset.card_le_card hsub).trans (by simp)

/-- Path indices whose vertices are adjacent to `c`. -/
def pathNeighborIndices {G : SimpleGraph V} [DecidableRel G.Adj]
    {u v : V} (p : G.Walk u v) (c : V) : Finset ℕ :=
  (Finset.range (p.length + 1)).filter fun i => G.Adj c (p.getVert i)

/-- The image of neighbor indices is exactly the intersection of path support
with the neighborhood finset. -/
lemma image_pathNeighborIndices_eq_inter
    {G : SimpleGraph V} [DecidableRel G.Adj] {u v c : V}
    (p : G.Walk u v) :
    (pathNeighborIndices p c).image p.getVert =
      p.support.toFinset ∩ G.neighborFinset c := by
  ext x
  constructor
  · intro hx
    obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
    have hi' := Finset.mem_filter.mp hi
    refine Finset.mem_inter.mpr ⟨?_, ?_⟩
    · exact List.mem_toFinset.mpr (p.getVert_mem_support i)
    · simpa [mem_neighborFinset] using hi'.2
  · intro hx
    have hx' := Finset.mem_inter.mp hx
    obtain ⟨i, hiEq, hiLen⟩ := Walk.mem_support_iff_exists_getVert.mp
      (List.mem_toFinset.mp hx'.1)
    refine Finset.mem_image.mpr ⟨i, ?_, hiEq⟩
    apply Finset.mem_filter.mpr
    refine ⟨Finset.mem_range.mpr (by omega), ?_⟩
    simpa [hiEq, mem_neighborFinset] using hx'.2

/-- On a path, the neighbor-index image has the same cardinality as its index
set. -/
lemma card_inter_eq_card_pathNeighborIndices
    {G : SimpleGraph V} [DecidableRel G.Adj] {u v c : V}
    (p : G.Walk u v) (hpPath : p.IsPath) :
    (p.support.toFinset ∩ G.neighborFinset c).card =
      (pathNeighborIndices p c).card := by
  rw [← image_pathNeighborIndices_eq_inter p, Finset.card_image_iff.mpr]
  intro i hi j hj hij
  rw [Finset.mem_coe] at hi hj
  apply hpPath.getVert_injOn
  · have := (Finset.mem_filter.mp hi).1
    simp only [Finset.mem_range] at this
    show i ≤ p.length
    omega
  · have := (Finset.mem_filter.mp hj).1
    simp only [Finset.mem_range] at this
    show j ≤ p.length
    omega
  · exact hij

omit [Fintype V] [DecidableEq V] in
/-- Off-path case: every pair of neighbor indices is at distance at most two
through the two-edge walk via `c`. -/
lemma card_pathNeighborIndices_le_three
    {G : SimpleGraph V} [DecidableRel G.Adj] {u v c : V}
    (p : G.Walk u v) (hp : p.length = G.dist u v) :
    (pathNeighborIndices p c).card ≤ 3 := by
  apply card_le_three_of_pairwise_natDist_le_two
  intro i hi j hj
  have hi' := Finset.mem_filter.mp hi
  have hj' := Finset.mem_filter.mp hj
  have hil : i ≤ p.length := by
    have := Finset.mem_range.mp hi'.1
    omega
  have hjl : j ≤ p.length := by
    have := Finset.mem_range.mp hj'.1
    omega
  have hd := dist_getVert_eq_natDist_of_length_eq_dist p hp hil hjl
  have hpiC : G.dist (p.getVert i) c = 1 :=
    dist_eq_one_iff_adj.mpr hi'.2.symm
  have hcPj : G.dist c (p.getVert j) = 1 :=
    dist_eq_one_iff_adj.mpr hj'.2
  have htri : G.dist (p.getVert i) (p.getVert j) ≤
      G.dist (p.getVert i) c + G.dist c (p.getVert j) :=
    hj'.2.reachable.dist_triangle_right (p.getVert i)
  rw [hd, hpiC, hcPj] at htri
  exact htri

omit [Fintype V] [DecidableEq V] in
/-- On-path case: if `c=p[k]`, every neighbor index is exactly one away from
`k`, so there are at most two. -/
lemma card_pathNeighborIndices_le_two_of_eq_getVert
    {G : SimpleGraph V} [DecidableRel G.Adj] {u v c : V}
    (p : G.Walk u v) (hp : p.length = G.dist u v)
    (k : ℕ) (hklen : k ≤ p.length) (hck : c = p.getVert k) :
    (pathNeighborIndices p c).card ≤ 2 := by
  apply card_le_two_of_natDist_eq_one _ k
  intro i hi
  have hi' := Finset.mem_filter.mp hi
  have hil : i ≤ p.length := by
    have := Finset.mem_range.mp hi'.1
    omega
  have hd := dist_getVert_eq_natDist_of_length_eq_dist p hp hklen hil
  have hadj : G.Adj (p.getVert k) (p.getVert i) := by
    simpa [hck] using hi'.2
  exact hd ▸ dist_eq_one_iff_adj.mpr hadj

/-- The classical metric hinge holds for every shortest path (diametrality is
not needed for the intersection bounds themselves). -/
theorem diametralNeighborhoodIntersectionBound
    (G : SimpleGraph V) [DecidableRel G.Adj] :
    DiametralNeighborhoodIntersectionBound G := by
  intro u v c p hpPath hpDist _hpDiam
  dsimp only
  constructor
  · intro hc
    obtain ⟨k, hkEq, hkLen⟩ := Walk.mem_support_iff_exists_getVert.mp
      (List.mem_toFinset.mp hc)
    rw [card_inter_eq_card_pathNeighborIndices p hpPath]
    exact card_pathNeighborIndices_le_two_of_eq_getVert
      p hpDist k hkLen hkEq.symm
  · intro _hc
    rw [card_inter_eq_card_pathNeighborIndices p hpPath]
    exact card_pathNeighborIndices_le_three p hpDist

/-- Unconditional classical diameter--maximum-degree order inequality. -/
theorem diameter_add_maxDegree_le_card_add_one
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected) :
    G.diam + G.maxDegree ≤ Fintype.card V + 1 := by
  exact diameter_add_maxDegree_le_card_add_one_of_intersection_bound
    G hconn (diametralNeighborhoodIntersectionBound G)

/-- Unconditional WOWII 13 for finite connected trees. -/
theorem wowii13_tree
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hacyc : G.IsAcyclic) :
    (G.diam : ℝ) +
        (_root_.WrittenOnTheWallII.GraphConjecture19EndpointMax.localMax G : ℝ) - 1 ≤
      b G := by
  exact _root_.WrittenOnTheWallII.GraphConjecture19TreeCharge.wowii13_of_tree_of_degree_count
    G hacyc (diameter_add_maxDegree_le_card_add_one G hconn)

end WrittenOnTheWallII.GraphConjecture19MetricIntersection
