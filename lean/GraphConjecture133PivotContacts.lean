import GraphConjecture133MetricContactMatrices

/-!
# WOWII 133: same-row metric pruning and gap-four pivots

A single candidate contacting two geodesic vertices gives a two-edge detour,
so their indices differ by at most two.  Combined with the triangle/C4
forbidden-pair table, this removes every multi-contact early row.
-/

namespace WrittenOnTheWallII.GraphConjecture133PivotContacts

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic
open WrittenOnTheWallII.GraphConjecture133DepthThreeCover

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Two contacts made by the same vertex give a two-edge replacement for the
geodesic segment, hence their ordered index gap is at most two. -/
theorem sameContact_index_gap_le_two {G : SimpleGraph V}
    {u v a : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    {i j : ℕ} (hi : i ≤ p.length) (hj : j ≤ p.length)
    (hia : G.Adj (p.getVert i) a) (haj : G.Adj a (p.getVert j)) :
    j ≤ i + 2 := by
  let q : G.Walk u v :=
    (((p.take i).append hia.toWalk).append haj.toWalk).append (p.drop j)
  have hq : G.dist u v ≤ q.length := G.dist_le q
  have htake : (p.take i).length = i := by simp [Walk.take_length, hi]
  have hdrop : (p.drop j).length = p.length - j := by simp [Walk.drop_length]
  simp only [q, Walk.length_append, Walk.length_cons, Walk.length_nil,
    zero_add] at hq
  rw [htake, hdrop, ← hp] at hq
  omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- In particular, one candidate cannot carry two contacts separated by
three or more geodesic indices. -/
theorem not_sameContacts_of_gap_three {G : SimpleGraph V}
    {u v a : V} (p : G.Walk u v) (hp : p.length = G.dist u v)
    {i j : ℕ} (hi : i ≤ p.length) (hj : j ≤ p.length)
    (hgap : i + 3 ≤ j) (hia : G.Adj (p.getVert i) a) :
    ¬G.Adj a (p.getVert j) := by
  intro haj
  have := sameContact_index_gap_le_two p hp hi hj hia haj
  omega

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- On a geodesic in a triangle-free C4-free graph, a fresh vertex has at
most one contact among indices `0..4`.  Gaps one and two are forbidden by
triangle/C4 structure; gaps at least three are forbidden by shortestness. -/
theorem early_contacts_unique {G : SimpleGraph V} {u v a : V}
    (p : G.Walk u v) (hpDist : p.length = G.dist u v) (hpPath : p.IsPath)
    (htri : G.CliqueFree 3) (hc4 : ¬HasC4 G) (hafresh : a ∉ p.support)
    {i j : ℕ} (hi : i < 5) (hj : j < 5)
    (hilength : i ≤ p.length) (hjlength : j ≤ p.length)
    (hai : G.Adj a (p.getVert i)) (haj : G.Adj a (p.getVert j)) :
    i = j := by
  by_contra hij
  rcases lt_or_gt_of_ne hij with hijlt | hjilt
  · have hgap := sameContact_index_gap_le_two p hpDist hilength hjlength hai.symm haj
    have hd : j = i + 1 ∨ j = i + 2 := by omega
    rcases hd with rfl | rfl
    · exact not_adj_both_ends_of_edge_of_triangleFree htri
        (p.adj_getVert_succ (by omega)) hai haj
    · have hilt : i < p.length := lt_of_lt_of_le (by omega) hjlength
      have hi1lt : i + 1 < p.length := lt_of_lt_of_le (by omega) hjlength
      have hmid := p.adj_getVert_succ (i := i) hilt
      have hnext := p.adj_getVert_succ (i := i + 1) hi1lt
      have hne : p.getVert i ≠ p.getVert (i + 2) := by
        intro h
        have := hpPath.getVert_injOn hilength
          (show i + 2 ≤ p.length from hjlength) h
        omega
      have hameda : a ≠ p.getVert (i + 1) := by
        intro h; subst a; exact hafresh (p.getVert_mem_support (i + 1))
      exact not_adj_both_distance_two_of_c4Free hc4 hmid hnext hne hameda hai haj
  · have hgap := sameContact_index_gap_le_two p hpDist hjlength hilength haj.symm hai
    have hd : i = j + 1 ∨ i = j + 2 := by omega
    rcases hd with rfl | rfl
    · exact not_adj_both_ends_of_edge_of_triangleFree htri
        (p.adj_getVert_succ (by omega)) haj hai
    · have hjlt : j < p.length := lt_of_lt_of_le (by omega) hilength
      have hj1lt : j + 1 < p.length := lt_of_lt_of_le (by omega) hilength
      have hmid := p.adj_getVert_succ (i := j) hjlt
      have hnext := p.adj_getVert_succ (i := j + 1) hj1lt
      have hne : p.getVert j ≠ p.getVert (j + 2) := by
        intro h
        have := hpPath.getVert_injOn hjlength
          (show j + 2 ≤ p.length from hilength) h
        omega
      have hameda : a ≠ p.getVert (j + 1) := by
        intro h; subst a; exact hafresh (p.getVert_mem_support (j + 1))
      exact not_adj_both_distance_two_of_c4Free hc4 hmid hnext hne hameda haj hai

end WrittenOnTheWallII.GraphConjecture133PivotContacts
