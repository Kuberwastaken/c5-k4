import GraphConjecture133MatchingNeighborhood
import GraphConjecture133TriangleIncidence

/-!
# WOWII 133: neighborhood edges are incident triangles

This file closes the representation bridge between edges of an induced open
neighborhood and 3-cliques containing its center.  Combining that bijection
with the two committed #133 modules gives the unconditional source-notation
triangle correction for finite C4-free graphs.
-/

namespace WrittenOnTheWallII.GraphConjecture133TriangleBijection

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture133MatchingNeighborhood
open WrittenOnTheWallII.GraphConjecture133TriangleIncidence

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Send an edge of the open neighborhood of `v` to its ambient endpoint pair,
with `v` inserted. -/
noncomputable def edgeToTriangle (G : SimpleGraph V) [DecidableRel G.Adj]
    (v : V) (e : (G.induce (G.neighborSet v)).edgeFinset) : Finset V :=
  insert v (e.val.toFinset.map (Function.Embedding.subtype _))

/-- Concrete form of `edgeToTriangle` on a represented unordered pair. -/
lemma edgeToTriangle_mk (G : SimpleGraph V) [DecidableRel G.Adj]
    (v : V) (a b : G.neighborSet v)
    (hab : s(a, b) ∈ (G.induce (G.neighborSet v)).edgeFinset) :
    edgeToTriangle G v ⟨s(a, b), hab⟩ = {v, a.val, b.val} := by
  simp [edgeToTriangle, Sym2.toFinset_mk_eq]

/-- A neighborhood edge and its center form an incident 3-clique. -/
lemma edgeToTriangle_mem (G : SimpleGraph V) [DecidableRel G.Adj]
    (v : V) (e : (G.induce (G.neighborSet v)).edgeFinset) :
    edgeToTriangle G v e ∈
      (G.cliqueFinset 3).filter (fun s ↦ v ∈ s) := by
  rcases e with ⟨⟨a, b⟩, hab⟩
  simp only [mem_edgeFinset, mem_edgeSet] at hab
  rw [edgeToTriangle_mk]
  rw [Finset.mem_filter, SimpleGraph.mem_cliqueFinset_iff,
    SimpleGraph.is3Clique_triple_iff]
  exact ⟨⟨a.property, b.property, hab⟩, by simp⟩

/-- The center of an open neighborhood is not one of its vertices. -/
lemma center_not_mem_mapped_edge (G : SimpleGraph V) [DecidableRel G.Adj]
    (v : V) (e : (G.induce (G.neighborSet v)).edgeFinset) :
    v ∉ e.val.toFinset.map (Function.Embedding.subtype _) := by
  intro hv
  rw [Finset.mem_map] at hv
  obtain ⟨x, _hx, hxv⟩ := hv
  exact x.property.ne hxv.symm

/-- Erasing the center recovers the endpoint pair, so the map is injective. -/
lemma edgeToTriangle_injective (G : SimpleGraph V) [DecidableRel G.Adj]
    (v : V) : Function.Injective (edgeToTriangle G v) := by
  intro e f hef
  have herase := congrArg (fun s : Finset V ↦ s.erase v) hef
  simp only [edgeToTriangle] at herase
  rw [Finset.erase_insert (center_not_mem_mapped_edge G v e),
    Finset.erase_insert (center_not_mem_mapped_edge G v f)] at herase
  apply Subtype.ext
  apply Sym2.ext
  intro x
  rw [← Sym2.mem_toFinset, ← Sym2.mem_toFinset]
  have hmap := Finset.map_injective
    (Function.Embedding.subtype (G.neighborSet v)) herase
  exact Finset.ext_iff.mp hmap x

/-- Conversely, erasing `v` from an incident 3-clique leaves two distinct
neighbors joined by an edge. -/
lemma edgeToTriangle_surjective (G : SimpleGraph V) [DecidableRel G.Adj]
    (v : V) :
    ∀ s ∈ (G.cliqueFinset 3).filter (fun s ↦ v ∈ s),
      ∃ e : (G.induce (G.neighborSet v)).edgeFinset,
        edgeToTriangle G v e = s := by
  intro s hs
  rw [Finset.mem_filter] at hs
  obtain ⟨hsclique, hv⟩ := hs
  rw [SimpleGraph.mem_cliqueFinset_iff] at hsclique
  have herasecard : (s.erase v).card = 2 := by
    rw [Finset.card_erase_of_mem hv, hsclique.card_eq]
  obtain ⟨a, b, hab, herase⟩ := Finset.card_eq_two.mp herasecard
  have haerase : a ∈ s.erase v := by simp [herase]
  have hberase : b ∈ s.erase v := by simp [herase]
  have hav : a ≠ v := (Finset.mem_erase.mp haerase).1
  have hbv : b ≠ v := (Finset.mem_erase.mp hberase).1
  have has : a ∈ s := (Finset.mem_erase.mp haerase).2
  have hbs : b ∈ s := (Finset.mem_erase.mp hberase).2
  have hva : G.Adj v a := hsclique.isClique hv has hav.symm
  have hvb : G.Adj v b := hsclique.isClique hv hbs hbv.symm
  have habAdj : G.Adj a b := hsclique.isClique has hbs hab
  let aa : G.neighborSet v := ⟨a, hva⟩
  let bb : G.neighborSet v := ⟨b, hvb⟩
  have hedge : s(aa, bb) ∈
      (G.induce (G.neighborSet v)).edgeFinset := by
    rw [mem_edgeFinset, mem_edgeSet, induce_adj]
    exact habAdj
  refine ⟨⟨s(aa, bb), hedge⟩, ?_⟩
  rw [edgeToTriangle_mk]
  change {v, a, b} = s
  rw [← herase, Finset.insert_erase hv]

/-- Pointwise bridge: edges among the neighbors of `v` are in bijection with
3-cliques containing `v`. -/
theorem neighborhoodEdgeCount_eq_numTrianglesAtVertex
    (G : SimpleGraph V) [DecidableRel G.Adj] (v : V) :
    neighborhoodEdgeCount G v = numTrianglesAtVertex G v := by
  unfold neighborhoodEdgeCount numTrianglesAtVertex
  apply Finset.card_bij
    (s := (G.induce (G.neighborSet v)).edgeFinset)
    (t := (G.cliqueFinset 3).filter (fun s ↦ v ∈ s))
    (fun e he ↦ edgeToTriangle G v ⟨e, he⟩)
  · intro e he
    exact edgeToTriangle_mem G v ⟨e, he⟩
  · intro e he f hf hef
    exact congrArg Subtype.val (edgeToTriangle_injective G v hef)
  · intro s hs
    obtain ⟨e, he⟩ := edgeToTriangle_surjective G v s hs
    exact ⟨e.val, e.property, he⟩

/-- The neighborhood-edge incidence sum is exactly three times the number of
triangles. -/
theorem triangleIncidenceCount_eq_three_mul
    (G : SimpleGraph V) [DecidableRel G.Adj] :
    triangleIncidenceCount G = 3 * (G.cliqueFinset 3).card := by
  unfold triangleIncidenceCount
  simp_rw [neighborhoodEdgeCount_eq_numTrianglesAtVertex]
  exact sum_numTrianglesAtVertex_eq_three_mul G

/-- Unconditional source-notation identity for every finite C4-free graph:
`l = (2m - 3t) / n`. -/
theorem l_eq_two_edges_sub_three_triangles_of_c4Free
    [Nonempty V] (G : SimpleGraph V) [DecidableRel G.Adj]
    (hc4 : ¬HasC4 G) :
    l G =
      ((2 * G.edgeFinset.card - 3 * (G.cliqueFinset 3).card : ℕ) : ℝ) /
        (Fintype.card V : ℝ) := by
  apply WrittenOnTheWallII.GraphConjecture133MatchingNeighborhood.l_eq_two_edges_sub_three_triangles_of_c4Free
  · exact hc4
  · exact triangleIncidenceCount_eq_three_mul G

end WrittenOnTheWallII.GraphConjecture133TriangleBijection
