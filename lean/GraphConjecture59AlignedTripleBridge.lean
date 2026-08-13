import GraphConjecture59ManyOutside

/-!
# WOWII 59: aligned-triple adjacency bridge

An aligned outside triple shares one core neighbor in each color side.  This
file isolates exactly what that incidence information does—and does not—force
before any global `f`, `b`, or residue argument is applied.
-/

namespace WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge

open SimpleGraph Finset

universe u
variable {V : Type u} [Fintype V] [DecidableEq V]

/-- The four unlabeled simple-graph types on an outside triple. -/
inductive OutsideTripleType
  | independent
  | oneEdge
  | path
  | triangle
  deriving DecidableEq

/-- A labeled realization of one of the four unlabeled outside-triple types. -/
def RealizesOutsideType (G : SimpleGraph V) (x y z : V) :
    OutsideTripleType → Prop
  | .independent => ¬G.Adj x y ∧ ¬G.Adj x z ∧ ¬G.Adj y z
  | .oneEdge =>
      (G.Adj x y ∧ ¬G.Adj x z ∧ ¬G.Adj y z) ∨
      (G.Adj x z ∧ ¬G.Adj x y ∧ ¬G.Adj y z) ∨
      (G.Adj y z ∧ ¬G.Adj x y ∧ ¬G.Adj x z)
  | .path =>
      (G.Adj x y ∧ G.Adj x z ∧ ¬G.Adj y z) ∨
      (G.Adj x y ∧ G.Adj y z ∧ ¬G.Adj x z) ∨
      (G.Adj x z ∧ G.Adj y z ∧ ¬G.Adj x y)
  | .triangle => G.Adj x y ∧ G.Adj x z ∧ G.Adj y z

omit [Fintype V] [DecidableEq V] in
/-- The three outside vertices always realize exactly one of the four
unlabeled adjacency types (existence form). -/
theorem outside_triple_type_exhaustive
    (G : SimpleGraph V) (x y z : V) :
    ∃ τ, RealizesOutsideType G x y z τ := by
  by_cases hxy : G.Adj x y <;> by_cases hxz : G.Adj x z <;>
    by_cases hyz : G.Adj y z
  · exact ⟨.triangle, hxy, hxz, hyz⟩
  · exact ⟨.path, Or.inl ⟨hxy, hxz, hyz⟩⟩
  · exact ⟨.path, Or.inr (Or.inl ⟨hxy, hyz, hxz⟩)⟩
  · exact ⟨.oneEdge, Or.inl ⟨hxy, hxz, hyz⟩⟩
  · exact ⟨.path, Or.inr (Or.inr ⟨hxz, hyz, hxy⟩)⟩
  · exact ⟨.oneEdge, Or.inr (Or.inl ⟨hxz, hxy, hyz⟩)⟩
  · exact ⟨.oneEdge, Or.inr (Or.inr ⟨hyz, hxy, hxz⟩)⟩
  · exact ⟨.independent, hxy, hxz, hyz⟩

/-- Two aligned core vertices are both adjacent to all three outside
vertices. -/
def AlignedOutsideTriple (G : SimpleGraph V)
    (a b x y z : V) : Prop :=
  G.Adj a x ∧ G.Adj a y ∧ G.Adj a z ∧
  G.Adj b x ∧ G.Adj b y ∧ G.Adj b z

/-- Pairwise distinctness of the two core vertices and outside triple. -/
def PairwiseDistinctFive (a b x y z : V) : Prop :=
  a ≠ b ∧ a ≠ x ∧ a ≠ y ∧ a ≠ z ∧
  b ≠ x ∧ b ≠ y ∧ b ≠ z ∧ x ≠ y ∧ x ≠ z ∧ y ≠ z

omit [Fintype V] [DecidableEq V] in
lemma fin_two_not_three_pairwise
    (i j k : Fin 2) : ¬(i ≠ j ∧ i ≠ k ∧ j ≠ k) := by
  fin_cases i <;> fin_cases j <;> fin_cases k <;> simp

omit [Fintype V] in
/-- Exact local boundary: the five vertices consisting of the two aligned
cores and the outside triple are bipartite exactly when the core pair is a
nonedge and the outside triple is independent. -/
theorem aligned_five_isBipartite_iff
    (G : SimpleGraph V) (a b x y z : V)
    (halign : AlignedOutsideTriple G a b x y z)
    (hdist : PairwiseDistinctFive a b x y z) :
    (G.induce (({a, b, x, y, z} : Finset V) : Set V)).IsBipartite ↔
      ¬G.Adj a b ∧ RealizesOutsideType G x y z .independent := by
  rcases hdist with
    ⟨habV, haxV, hayV, hazV, hbxV, hbyV, hbzV, hxyV, hxzV, hyzV⟩
  rw [induce_isBipartite_iff_exists_coloring]
  constructor
  · rintro ⟨c, hc⟩
    have hmemA : a ∈ ({a, b, x, y, z} : Finset V) := by simp
    have hmemB : b ∈ ({a, b, x, y, z} : Finset V) := by simp
    have hmemX : x ∈ ({a, b, x, y, z} : Finset V) := by simp
    have hmemY : y ∈ ({a, b, x, y, z} : Finset V) := by simp
    have hmemZ : z ∈ ({a, b, x, y, z} : Finset V) := by simp
    have no_triangle (p q r : V)
        (hp : p ∈ ({a, b, x, y, z} : Finset V))
        (hq : q ∈ ({a, b, x, y, z} : Finset V))
        (hr : r ∈ ({a, b, x, y, z} : Finset V))
        (hpq : G.Adj p q) (hpr : G.Adj p r) (hqr : G.Adj q r) : False := by
      exact fin_two_not_three_pairwise (c p) (c q) (c r)
        ⟨hc p hp q hq hpq, hc p hp r hr hpr, hc q hq r hr hqr⟩
    have hab : ¬G.Adj a b := by
      intro hab
      exact no_triangle a b x hmemA hmemB hmemX hab halign.1 halign.2.2.2.1
    have hxy : ¬G.Adj x y := by
      intro hxy
      exact no_triangle a x y hmemA hmemX hmemY halign.1 halign.2.1 hxy
    have hxz : ¬G.Adj x z := by
      intro hxz
      exact no_triangle a x z hmemA hmemX hmemZ halign.1 halign.2.2.1 hxz
    have hyz : ¬G.Adj y z := by
      intro hyz
      exact no_triangle a y z hmemA hmemY hmemZ halign.2.1 halign.2.2.1 hyz
    exact ⟨hab, hxy, hxz, hyz⟩
  · rintro ⟨hab, hxy, hxz, hyz⟩
    refine ⟨fun v ↦ if v = a ∨ v = b then 0 else 1, ?_⟩
    intro p hp q hq hpq
    simp only [mem_insert, mem_singleton] at hp hq
    rcases hp with rfl | rfl | rfl | rfl | rfl <;>
      rcases hq with rfl | rfl | rfl | rfl | rfl <;>
      simp_all [AlignedOutsideTriple, hpq.ne, hpq.ne', G.adj_comm, eq_comm]

/-- Under pairwise distinctness, the favorable local boundary gives an
explicit five-vertex induced-bipartite witness. -/
theorem five_le_b_of_aligned_independent_nonedge
    (G : SimpleGraph V) (a b x y z : V)
    (halign : AlignedOutsideTriple G a b x y z)
    (hdist : PairwiseDistinctFive a b x y z)
    (hab : ¬G.Adj a b)
    (hout : RealizesOutsideType G x y z .independent) :
    5 ≤ G.largestInducedBipartiteSubgraphSize := by
  have hbip := (aligned_five_isBipartite_iff G a b x y z halign hdist).2 ⟨hab, hout⟩
  have hcard : ({a, b, x, y, z} : Finset V).card = 5 := by
    rcases hdist with
      ⟨habV, haxV, hayV, hazV, hbxV, hbyV, hbzV, hxyV, hxzV, hyzV⟩
    simp [habV, haxV, hayV, hazV, hbxV, hbyV, hbzV,
      hxyV, hxzV, hyzV]
  have hbound :=
    _root_.WrittenOnTheWallII.GraphConjecture40Baseline.card_le_largestInducedBipartiteSubgraphSize
      G ({a, b, x, y, z} : Finset V) hbip
  simpa [hcard] using hbound

omit [Fintype V] in
/-- The smallest bad adjacency addition is already one outside edge: together
with either common core vertex it forms a triangle, so the aligned five-set is
not bipartite. -/
theorem one_outside_edge_blocks_aligned_five_bipartite
    (G : SimpleGraph V) (a b x y z : V)
    (halign : AlignedOutsideTriple G a b x y z)
    (hxy : G.Adj x y) :
    ¬(G.induce (({a, b, x, y, z} : Finset V) : Set V)).IsBipartite := by
  rw [induce_isBipartite_iff_exists_coloring]
  rintro ⟨c, hc⟩
  have hax : c a ≠ c x := hc a (by simp) x (by simp) halign.1
  have hay : c a ≠ c y := hc a (by simp) y (by simp) halign.2.1
  have hxy' : c x ≠ c y := hc x (by simp) y (by simp) hxy
  exact fin_two_not_three_pairwise (c a) (c x) (c y) ⟨hax, hay, hxy'⟩

end WrittenOnTheWallII.GraphConjecture59AlignedTripleBridge
