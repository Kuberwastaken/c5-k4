import FormalConjecturesUtil

/-!
# WOWII 19/13: geodesic endpoint splice

This file formalizes the metric core of the standard construction behind the
diameter-plus-local-independence lower bound.  Along a shortest walk from an
endpoint `u`, a neighbor of `u` cannot coincide with the walk from index two
onward and cannot be adjacent to the walk from index three onward.  Therefore
an independent set in `N(u)` can interact with the retained geodesic tail only
at its first retained vertex, `p.getVert 2`.
-/

namespace WrittenOnTheWallII.GraphConjecture19DiameterBaseline

open SimpleGraph Finset

universe u

variable {V : Type u}

/-- Indices on a shortest walk measure their exact graph distance. -/
theorem dist_getVert_eq_natDist_of_length_eq_dist
    {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) {i j : ℕ}
    (hi : i ≤ p.length) (hj : j ≤ p.length) :
    G.dist (p.getVert i) (p.getVert j) = i.dist j := by
  have hordered : ∀ {a b : ℕ}, a ≤ b → b ≤ p.length →
      G.dist (p.getVert a) (p.getVert b) = b - a := by
    intro a b hab hb
    let q := (p.drop a).take (b - a)
    have hqsub : q.IsSubwalk p := by
      exact (Walk.isSubwalk_take (p.drop a) (b - a)).trans
        (Walk.isSubwalk_drop p a)
    have hshort := length_eq_dist_of_subwalk hp hqsub
    have hqlen : q.length = b - a := by
      dsimp [q]
      simp only [Walk.take_length, Walk.drop_length]
      rw [Nat.min_eq_left]
      omega
    have hqend : (p.drop a).getVert (b - a) = p.getVert b := by
      rw [Walk.drop_getVert]
      congr 1
      omega
    rw [hqlen, hqend] at hshort
    exact hshort.symm
  rcases le_total i j with hij | hji
  · rw [Nat.dist_eq_sub_of_le hij]
    exact hordered hij hj
  · rw [Nat.dist_comm, SimpleGraph.dist_comm]
    rw [Nat.dist_eq_sub_of_le hji]
    exact hordered hji hi

/-- A shortest walk has no chord between indices separated by at least two. -/
theorem not_adj_getVert_of_add_two_le
    {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) {i j : ℕ}
    (hij : i + 2 ≤ j) (hj : j ≤ p.length) :
    ¬G.Adj (p.getVert i) (p.getVert j) := by
  intro hadj
  have hdist := dist_getVert_eq_natDist_of_length_eq_dist p hp
    (by omega : i ≤ p.length) hj
  have hone : G.dist (p.getVert i) (p.getVert j) = 1 :=
    dist_eq_one_iff_adj.mpr hadj
  rw [hone, Nat.dist_eq_sub_of_le (by omega : i ≤ j)] at hdist
  omega

/-- A neighbor of the initial endpoint cannot itself be a geodesic vertex at
index two or later. -/
theorem neighbor_ne_getVert_of_two_le
    {G : SimpleGraph V} {u v a : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hua : G.Adj u a)
    {i : ℕ} (hi : 2 ≤ i) (hilength : i ≤ p.length) :
    a ≠ p.getVert i := by
  intro hai
  have hdist := dist_getVert_eq_natDist_of_length_eq_dist p hp
    (show 0 ≤ p.length by omega) hilength
  have hu0 : p.getVert 0 = u := p.getVert_zero
  have hone : G.dist u a = 1 := dist_eq_one_iff_adj.mpr hua
  rw [hu0, ← hai, hone, Nat.dist_zero_left] at hdist
  omega

/-- The key endpoint-separation fact: a neighbor of the initial endpoint can
meet the retained geodesic tail only at index two.  It has no edge to any
index-three-or-later vertex. -/
theorem neighbor_not_adj_getVert_of_three_le
    {G : SimpleGraph V} {u v a : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (hua : G.Adj u a)
    {i : ℕ} (hi : 3 ≤ i) (hilength : i ≤ p.length) :
    ¬G.Adj a (p.getVert i) := by
  intro hai
  have hdist := dist_getVert_eq_natDist_of_length_eq_dist p hp
    (show 0 ≤ p.length by omega) hilength
  have hu0 : p.getVert 0 = u := p.getVert_zero
  have huaDist : G.dist u a = 1 := dist_eq_one_iff_adj.mpr hua
  have haiDist : G.dist a (p.getVert i) = 1 := dist_eq_one_iff_adj.mpr hai
  have htriangle : G.dist u (p.getVert i) ≤
      G.dist u a + G.dist a (p.getVert i) := by
    exact hai.reachable.dist_triangle_right u
  rw [hu0, Nat.dist_zero_left] at hdist
  rw [huaDist, haiDist, hdist] at htriangle
  omega

/-- Set-level form used by the endpoint splice: every member of a local
independent set is separated from all geodesic vertices at indices at least
three.  Independence is retained in the interface because it is the other
half of the eventual bipartition proof. -/
theorem indep_neighbors_separated_from_geodesic_tail
    {G : SimpleGraph V} {u v : V} (p : G.Walk u v)
    (hp : p.length = G.dist u v) (A : Set V)
    (hAindep : G.IsIndepSet A) (hAN : A ⊆ G.neighborSet u) :
    G.IsIndepSet A ∧
      ∀ a ∈ A, ∀ i : ℕ, 3 ≤ i → i ≤ p.length →
        ¬G.Adj a (p.getVert i) := by
  refine ⟨hAindep, ?_⟩
  intro a ha i hi hilength
  exact neighbor_not_adj_getVert_of_three_le p hp (hAN ha) hi hilength

/-- Connectedness supplies a shortest path to any chosen far endpoint.  This
packages the metric rungs above in the exact diameter-endpoint situation. -/
theorem exists_diametral_geodesic_from_endpoint
    {G : SimpleGraph V} [Finite V] (hconn : G.Connected) (u v : V)
    (huv : G.dist u v = G.diam) :
    ∃ p : G.Walk u v,
      p.IsPath ∧ p.length = G.diam ∧
      (∀ a : V, G.Adj u a →
        (∀ i : ℕ, 2 ≤ i → i ≤ p.length → a ≠ p.getVert i) ∧
        (∀ i : ℕ, 3 ≤ i → i ≤ p.length → ¬G.Adj a (p.getVert i))) := by
  obtain ⟨p, hpPath, hpDist⟩ := hconn.exists_path_of_dist u v
  refine ⟨p, hpPath, hpDist.trans huv, ?_⟩
  intro a hua
  constructor
  · intro i hi hilength
    exact neighbor_ne_getVert_of_two_le p hpDist hua hi hilength
  · intro i hi hilength
    exact neighbor_not_adj_getVert_of_three_le p hpDist hua hi hilength

end WrittenOnTheWallII.GraphConjecture19DiameterBaseline
