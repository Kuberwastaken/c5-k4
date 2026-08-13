import GraphConjecture40Baseline

/-!
# WOWII 40: the internal-edge theorem shadow

This file formalizes the structural obstruction behind the `K_{2,c}`
internal-edge trials.  An arbitrary graph `H` is placed on the right side of a
complete two-hub join.  If a bipartite induced witness omits at most one
ambient vertex, then the omitted right vertices form a vertex cover of `H` of
cardinality at most one.  Consequently `H` is a star plus isolates and all of
its vertices form an induced-forest witness.

The API accepts the actual near-spanning bipartite witness.  It does not assume
an unformalized equivalence between that witness and the upstream `sSup`
invariant.
-/

namespace WrittenOnTheWallII.GraphConjecture40InternalEdgeShadow

open SimpleGraph Finset

universe u

variable {B : Type u}

/-- Add two nonadjacent universal hubs to an arbitrary internal graph `H`. -/
def twoHubExtension (H : SimpleGraph B) : SimpleGraph (Fin 2 ⊕ B) where
  Adj x y :=
    match x, y with
    | Sum.inl _, Sum.inl _ => False
    | Sum.inl _, Sum.inr _ => True
    | Sum.inr _, Sum.inl _ => True
    | Sum.inr x, Sum.inr y => H.Adj x y
  symm := by
    intro x y h
    cases x <;> cases y <;> simp_all [H.adj_comm]
  loopless := by
    intro x
    cases x <;> simp

@[simp] lemma twoHubExtension_adj_left_right (H : SimpleGraph B)
    (i : Fin 2) (x : B) :
    (twoHubExtension H).Adj (Sum.inl i) (Sum.inr x) := by
  trivial

@[simp] lemma twoHubExtension_adj_right_left (H : SimpleGraph B)
    (x : B) (i : Fin 2) :
    (twoHubExtension H).Adj (Sum.inr x) (Sum.inl i) := by
  trivial

@[simp] lemma twoHubExtension_adj_right_right (H : SimpleGraph B)
    (x y : B) :
    (twoHubExtension H).Adj (Sum.inr x) (Sum.inr y) ↔ H.Adj x y := by
  rfl

/-- The subgraph induced by all right-side vertices is exactly `H`. -/
noncomputable def rightSideIso (H : SimpleGraph B) :
    (twoHubExtension H).induce
      ((Sum.inr : B → Fin 2 ⊕ B) '' (Set.univ : Set B)) ≃g H where
  toEquiv :=
    (Equiv.Set.image (Sum.inr : B → Fin 2 ⊕ B) (Set.univ : Set B)
      Sum.inr_injective).symm.trans (Equiv.Set.univ B)
  map_rel_iff' := by
    rintro ⟨_, ⟨x, -, rfl⟩⟩ ⟨_, ⟨y, -, rfl⟩⟩
    let e := Equiv.Set.image (Sum.inr : B → Fin 2 ⊕ B) (Set.univ : Set B)
      Sum.inr_injective
    have hx : e.symm ⟨Sum.inr x, Set.mem_image Sum.inr Set.univ (Sum.inr x) |>.2
        ⟨x, Set.mem_univ x, rfl⟩⟩ = ⟨x, Set.mem_univ x⟩ := by
      apply e.injective
      rw [e.apply_symm_apply]
      rfl
    have hy : e.symm ⟨Sum.inr y, Set.mem_image Sum.inr Set.univ (Sum.inr y) |>.2
        ⟨y, Set.mem_univ y, rfl⟩⟩ = ⟨y, Set.mem_univ y⟩ := by
      apply e.injective
      rw [e.apply_symm_apply]
      rfl
    change H.Adj (↑(e.symm ⟨Sum.inr x, _⟩)) (↑(e.symm ⟨Sum.inr y, _⟩)) ↔
      H.Adj x y
    rw [hx, hy]

/-- A bipartite induced graph cannot contain a triangle whose three vertices
belong to the inducing set. -/
lemma false_of_triangle_of_induce_isBipartite
    {V : Type*} [DecidableEq V] (G : SimpleGraph V) (S : Finset V)
    (hS : (G.induce (S : Set V)).IsBipartite) {x y z : V}
    (hx : x ∈ S) (hy : y ∈ S) (hz : z ∈ S)
    (hxy : G.Adj x y) (hyz : G.Adj y z) (hzx : G.Adj z x) :
    False := by
  rw [induce_isBipartite_iff_exists_coloring] at hS
  obtain ⟨color, hcolor⟩ := hS
  have hxy' := hcolor x hx y hy hxy
  have hyz' := hcolor y hy z hz hyz
  have hzx' := hcolor z hz x hx hzx
  omega

/-- If an inducing set has size at least `|B|+1`, its complement in the
`|B|+2` vertex two-hub extension is subsingleton. -/
lemma complement_subsingleton_of_large_finset [Fintype B] [DecidableEq B]
    (S : Finset (Fin 2 ⊕ B))
    (hcard : Fintype.card B + 1 ≤ S.card) :
    ((S : Set (Fin 2 ⊕ B))ᶜ).Subsingleton := by
  classical
  have hcompcard : (Finset.univ \ S).card ≤ 1 := by
    rw [Finset.card_sdiff_of_subset (Finset.subset_univ S)]
    simp only [Finset.card_univ, Fintype.card_sum, Fintype.card_fin]
    omega
  intro x hx y hy
  have hx' : x ∈ Finset.univ \ S := by simpa using hx
  have hy' : y ∈ Finset.univ \ S := by simpa using hy
  exact (Finset.card_le_one.mp hcompcard) x hx' y hy'

/-- Core theorem-shadow implication.  The omitted right vertices cover every
internal edge, and there is at most one such vertex. -/
theorem exists_subsingleton_internal_vertexCover
    (H : SimpleGraph B) (S : Finset (Fin 2 ⊕ B))
    (hS : ((twoHubExtension H).induce (S : Set (Fin 2 ⊕ B))).IsBipartite)
    (homit : ((S : Set (Fin 2 ⊕ B))ᶜ).Subsingleton) :
    ∃ C : Set B, C.Subsingleton ∧ H.IsVertexCover C := by
  classical
  let C : Set B := {x | Sum.inr x ∉ S}
  have hleft : Sum.inl (0 : Fin 2) ∈ S ∨ Sum.inl (1 : Fin 2) ∈ S := by
    by_contra h
    push_neg at h
    have heq := homit h.1 h.2
    have : (0 : Fin 2) = 1 := Sum.inl_injective heq
    omega
  have hCsub : C.Subsingleton := by
    intro x hx y hy
    apply Sum.inr_injective
    exact homit hx hy
  refine ⟨C, hCsub, ?_⟩
  intro x y hxy
  by_contra hcover
  push_neg at hcover
  have hxS : Sum.inr x ∈ S := by simpa [C] using hcover.1
  have hyS : Sum.inr y ∈ S := by simpa [C] using hcover.2
  rcases hleft with hl | hl
  · exact false_of_triangle_of_induce_isBipartite
      (twoHubExtension H) S hS hl hxS hyS
      (twoHubExtension_adj_left_right H 0 x)
      ((twoHubExtension_adj_right_right H x y).2 hxy)
      (twoHubExtension_adj_right_left H y 0)
  · exact false_of_triangle_of_induce_isBipartite
      (twoHubExtension H) S hS hl hxS hyS
      (twoHubExtension_adj_left_right H 1 x)
      ((twoHubExtension_adj_right_right H x y).2 hxy)
      (twoHubExtension_adj_right_left H y 1)

/-- A graph with a subsingleton vertex cover is a star plus isolated vertices,
and hence is acyclic. -/
theorem isAcyclic_of_subsingleton_vertexCover (H : SimpleGraph B)
    (C : Set B) (hC : C.Subsingleton) (hcover : H.IsVertexCover C) :
    H.IsAcyclic := by
  have hcomp : H.IsIndepSet Cᶜ :=
    (@SimpleGraph.isIndepSet_compl_iff_isVertexCover B H C).2 hcover
  have hCind : H.IsIndepSet C := by
    intro x hx y hy hxy _
    exact hxy (hC hx hy)
  apply
    GraphConjecture40Baseline.isAcyclic_of_independent_parts_of_left_unique_neighbor
      (G := H) Cᶜ C
  · exact Set.compl_union_self C
  · exact hcomp
  · exact hCind
  · intro i hi x hx y hy _ _
    exact hC hx hy

/-- A near-spanning bipartite witness in the two-hub extension forces the
entire internal graph to be a forest. -/
theorem internal_isAcyclic_of_near_spanning_bipartite
    (H : SimpleGraph B) (S : Finset (Fin 2 ⊕ B))
    (hS : ((twoHubExtension H).induce (S : Set (Fin 2 ⊕ B))).IsBipartite)
    (homit : ((S : Set (Fin 2 ⊕ B))ᶜ).Subsingleton) :
    H.IsAcyclic := by
  obtain ⟨C, hC, hcover⟩ :=
    exists_subsingleton_internal_vertexCover H S hS homit
  exact isAcyclic_of_subsingleton_vertexCover H C hC hcover

/-- Finite cardinality adapter: a bipartite witness of order at least
`|B|+1` forces the internal side to be a forest. -/
theorem internal_isAcyclic_of_large_bipartite_finset
    [Fintype B] [DecidableEq B]
    (H : SimpleGraph B) (S : Finset (Fin 2 ⊕ B))
    (hS : ((twoHubExtension H).induce (S : Set (Fin 2 ⊕ B))).IsBipartite)
    (hcard : Fintype.card B + 1 ≤ S.card) :
    H.IsAcyclic := by
  apply internal_isAcyclic_of_near_spanning_bipartite H S hS
  exact complement_subsingleton_of_large_finset S hcard

/-- In invariant language, all internal vertices themselves provide an
induced-forest witness of order `|B|`. -/
theorem card_le_internal_largestInducedForestSize
    [Fintype B] [DecidableEq B]
    (H : SimpleGraph B) (hH : H.IsAcyclic) :
    Fintype.card B ≤ H.largestInducedForestSize := by
  have huniv : (H.induce (Set.univ : Set B)).IsAcyclic :=
    (SimpleGraph.induceUnivIso H).isAcyclic_iff.mpr hH
  have hfinuniv :
      (H.induce ((↑(Finset.univ : Finset B)) : Set B)).IsAcyclic := by
    rw [show ((↑(Finset.univ : Finset B)) : Set B) = Set.univ by
      ext x
      simp]
    exact huniv
  simpa only [Finset.card_univ] using
    (GraphConjecture40Baseline.card_le_largestInducedForestSize
      H (Finset.univ : Finset B) hfinuniv)

/-- The right-side copy of an acyclic `H` is an induced-forest witness of size
`|B|` inside the full two-hub extension. -/
theorem card_le_extension_largestInducedForestSize
    [Fintype B] [DecidableEq B]
    (H : SimpleGraph B) (hH : H.IsAcyclic) :
    Fintype.card B ≤ (twoHubExtension H).largestInducedForestSize := by
  let e : B ↪ Fin 2 ⊕ B := ⟨Sum.inr, Sum.inr_injective⟩
  let R : Finset (Fin 2 ⊕ B) := Finset.univ.map e
  have hRset : (R : Set (Fin 2 ⊕ B)) =
      (Sum.inr : B → Fin 2 ⊕ B) '' (Set.univ : Set B) := by
    simp only [R, Finset.coe_map, Finset.coe_univ]
    change (Sum.inr : B → Fin 2 ⊕ B) '' Set.univ = Sum.inr '' Set.univ
    rfl
  have hRacyclic : ((twoHubExtension H).induce (R : Set (Fin 2 ⊕ B))).IsAcyclic := by
    rw [hRset]
    exact (rightSideIso H).isAcyclic_iff.mpr hH
  have hbound :=
    GraphConjecture40Baseline.card_le_largestInducedForestSize
      (twoHubExtension H) R hRacyclic
  simpa only [R, Finset.card_map, Finset.card_univ] using hbound

/-- Combined honest-certificate form of the theorem shadow. -/
theorem internal_forest_bound_of_large_bipartite_finset
    [Fintype B] [DecidableEq B]
    (H : SimpleGraph B) (S : Finset (Fin 2 ⊕ B))
    (hS : ((twoHubExtension H).induce (S : Set (Fin 2 ⊕ B))).IsBipartite)
    (hcard : Fintype.card B + 1 ≤ S.card) :
    Fintype.card B ≤ H.largestInducedForestSize := by
  exact card_le_internal_largestInducedForestSize H
    (internal_isAcyclic_of_large_bipartite_finset H S hS hcard)

/-- Invariant-level vertex-cover conclusion: `b(G(H)) ≥ |B|+1` forces the
internal edges to be covered by at most one right-side vertex. -/
theorem exists_subsingleton_internal_vertexCover_of_large_bipartiteSize
    [Fintype B] [DecidableEq B] (H : SimpleGraph B)
    (hlarge : Fintype.card B + 1 ≤
      (twoHubExtension H).largestInducedBipartiteSubgraphSize) :
    ∃ C : Set B, C.Subsingleton ∧ H.IsVertexCover C := by
  have hfinite : 1 < Fintype.card (Fin 2 ⊕ B) := by
    simp only [Fintype.card_sum, Fintype.card_fin]
    omega
  obtain ⟨S, hS, hcard⟩ :=
    GraphConjecture40Baseline.exists_largestInducedBipartiteSubgraphSize_witness
      (twoHubExtension H) hfinite
  apply exists_subsingleton_internal_vertexCover H S hS
  apply complement_subsingleton_of_large_finset S
  omega

/-- Full invariant adapter.  If the two-hub extension has a bipartite induced
subgraph on at least `|B|+1` vertices, then the entire internal graph is an
induced forest. -/
theorem internal_forest_bound_of_large_bipartiteSize
    [Fintype B] [DecidableEq B] (H : SimpleGraph B)
    (hlarge : Fintype.card B + 1 ≤
      (twoHubExtension H).largestInducedBipartiteSubgraphSize) :
    Fintype.card B ≤ H.largestInducedForestSize := by
  have hfinite : 1 < Fintype.card (Fin 2 ⊕ B) := by
    simp only [Fintype.card_sum, Fintype.card_fin]
    omega
  obtain ⟨S, hS, hcard⟩ :=
    GraphConjecture40Baseline.exists_largestInducedBipartiteSubgraphSize_witness
      (twoHubExtension H) hfinite
  apply internal_forest_bound_of_large_bipartite_finset H S hS
  omega

/-- The WOWII-40 theorem-shadow in ambient invariant language:
`b(G(H)) ≥ |B|+1` forces `f(G(H)) ≥ |B|`. -/
theorem extension_forest_bound_of_large_bipartiteSize
    [Fintype B] [DecidableEq B] (H : SimpleGraph B)
    (hlarge : Fintype.card B + 1 ≤
      (twoHubExtension H).largestInducedBipartiteSubgraphSize) :
    Fintype.card B ≤ (twoHubExtension H).largestInducedForestSize := by
  obtain ⟨C, hC, hcover⟩ :=
    exists_subsingleton_internal_vertexCover_of_large_bipartiteSize H hlarge
  exact card_le_extension_largestInducedForestSize H
    (isAcyclic_of_subsingleton_vertexCover H C hC hcover)

#print axioms exists_subsingleton_internal_vertexCover
#print axioms isAcyclic_of_subsingleton_vertexCover
#print axioms internal_isAcyclic_of_large_bipartite_finset
#print axioms internal_forest_bound_of_large_bipartite_finset
#print axioms exists_subsingleton_internal_vertexCover_of_large_bipartiteSize
#print axioms internal_forest_bound_of_large_bipartiteSize
#print axioms extension_forest_bound_of_large_bipartiteSize

end WrittenOnTheWallII.GraphConjecture40InternalEdgeShadow
