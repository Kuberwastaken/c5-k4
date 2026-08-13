import GraphConjecture133EarlyEscapeCombinatorics

/-!
# WOWII 133: forbidden pairs in the depth-three cover

For a candidate third handle vertex, triangle-freeness forbids contacts with
consecutive geodesic vertices and C4-freeness forbids contacts two steps
apart.  Among indices one through four, the only possible double contact is
therefore the endpoint pair `{1,4}`.
-/

namespace WrittenOnTheWallII.GraphConjecture133DepthThreeCover

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133Cubic

variable {V : Type*} [Fintype V] [DecidableEq V] [Nonempty V]

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A vertex cannot be adjacent to both ends of an edge in a triangle-free
graph. -/
lemma not_adj_both_ends_of_edge_of_triangleFree {G : SimpleGraph V}
    (htri : G.CliqueFree 3) {a x y : V}
    (hxy : G.Adj x y) (hax : G.Adj a x) :
    ¬G.Adj a y := by
  intro hay
  exact G.isIndepSet_neighborSet_of_triangleFree htri a
    (by simpa [G.mem_neighborSet, adj_comm] using hax)
    (by simpa [G.mem_neighborSet, adj_comm] using hay)
    hxy.ne
    hxy

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- A vertex cannot contact both endpoints of a length-two path in a C4-free
graph, provided those endpoints are distinct. -/
lemma not_adj_both_distance_two_of_c4Free {G : SimpleGraph V}
    (hc4 : ¬HasC4 G) {a x y z : V}
    (hxy : G.Adj x y) (hyz : G.Adj y z) (hxz : x ≠ z) (hay : a ≠ y)
    (hax : G.Adj a x) :
    ¬G.Adj a z := by
  intro haz
  apply hc4
  refine ⟨a, x, y, z, ?_, ?_, ?_, ?_, ?_, ?_, hax, hxy, hyz, haz.symm⟩
  · exact hax.ne
  · exact hay
  · exact haz.ne
  · exact hxy.ne
  · exact hxz
  · exact hyz.ne

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- Complete forbidden-pair table for contacts of one vertex with geodesic
indices `1..4`.  The five forbidden pairs leave only `{1,4}` as a possible
double contact. -/
theorem depthThree_forbiddenPairTable {G : SimpleGraph V} {u v a : V}
    (p : G.Walk u v) (hp : p.IsPath) (hlen : 4 ≤ p.length)
    (htri : G.CliqueFree 3) (hc4 : ¬HasC4 G) (hafresh : a ∉ p.support) :
    (¬(G.Adj a (p.getVert 1) ∧ G.Adj a (p.getVert 2))) ∧
    (¬(G.Adj a (p.getVert 2) ∧ G.Adj a (p.getVert 3))) ∧
    (¬(G.Adj a (p.getVert 3) ∧ G.Adj a (p.getVert 4))) ∧
    (¬(G.Adj a (p.getVert 1) ∧ G.Adj a (p.getVert 3))) ∧
    (¬(G.Adj a (p.getVert 2) ∧ G.Adj a (p.getVert 4))) := by
  have h12 : G.Adj (p.getVert 1) (p.getVert 2) :=
    p.adj_getVert_succ (by omega)
  have h23 : G.Adj (p.getVert 2) (p.getVert 3) :=
    p.adj_getVert_succ (by omega)
  have h34 : G.Adj (p.getVert 3) (p.getVert 4) :=
    p.adj_getVert_succ (by omega)
  have h13 : p.getVert 1 ≠ p.getVert 3 := by
    intro h
    have := hp.getVert_injOn
      (show 1 ≤ p.length by omega) (show 3 ≤ p.length by omega) h
    omega
  have h24 : p.getVert 2 ≠ p.getVert 4 := by
    intro h
    have := hp.getVert_injOn
      (show 2 ≤ p.length by omega) (show 4 ≤ p.length by omega) h
    omega
  have ha2 : a ≠ p.getVert 2 := by
    intro h
    subst a
    exact hafresh (p.getVert_mem_support 2)
  have ha3 : a ≠ p.getVert 3 := by
    intro h
    subst a
    exact hafresh (p.getVert_mem_support 3)
  constructor
  · rintro ⟨ha1, ha2⟩
    exact not_adj_both_ends_of_edge_of_triangleFree htri h12 ha1 ha2
  constructor
  · rintro ⟨ha2, ha3⟩
    exact not_adj_both_ends_of_edge_of_triangleFree htri h23 ha2 ha3
  constructor
  · rintro ⟨ha3, ha4⟩
    exact not_adj_both_ends_of_edge_of_triangleFree htri h34 ha3 ha4
  constructor
  · rintro ⟨ha1, ha3⟩
    exact not_adj_both_distance_two_of_c4Free hc4 h12 h23 h13 ha2 ha1 ha3
  · rintro ⟨ha2, ha4⟩
    exact not_adj_both_distance_two_of_c4Free hc4 h23 h34 h24 ha3 ha2 ha4

omit [Fintype V] [DecidableEq V] [Nonempty V] in
/-- If a depth-three candidate has two distinct contacts among indices
`1..4`, they must be exactly indices one and four. -/
theorem two_contacts_force_endpoints {G : SimpleGraph V} {u v a : V}
    (p : G.Walk u v) (hp : p.IsPath) (hlen : 4 ≤ p.length)
    (htri : G.CliqueFree 3) (hc4 : ¬HasC4 G) (hafresh : a ∉ p.support)
    {i j : ℕ} (hi : 1 ≤ i) (hj : j ≤ 4) (hij : i < j)
    (hai : G.Adj a (p.getVert i)) (haj : G.Adj a (p.getVert j)) :
    i = 1 ∧ j = 4 := by
  obtain ⟨h12, h23, h34, h13, h24⟩ :=
    depthThree_forbiddenPairTable p hp hlen htri hc4 hafresh
  have hiCases : i = 1 ∨ i = 2 ∨ i = 3 := by omega
  have hjCases : j = 2 ∨ j = 3 ∨ j = 4 := by omega
  rcases hiCases with rfl | rfl | rfl <;>
    rcases hjCases with rfl | rfl | rfl <;> simp_all

end WrittenOnTheWallII.GraphConjecture133DepthThreeCover
