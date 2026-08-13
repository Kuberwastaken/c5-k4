import Mathlib.Combinatorics.SimpleGraph.LineGraph
import FormalConjecturesUtil

/-!
# Line-graph endpoint-clique coordinates

The neighbors in `L(G)` of the vertex corresponding to an edge `uv` split
between the edges incident with `u` and those incident with `v`.  Each part is
a clique.  Consequently an independent subset of that neighborhood contains
at most one edge through each endpoint, and therefore has size at most two.

This is the reusable local-coordinate fact behind the line-graph analysis of
WOWII 19.
-/

namespace SimpleGraph.LineGraphEndpointCliques

open Set

universe u

variable {V : Type u} (G : SimpleGraph V)

/-- Edge-vertices of `L(G)` represented by edges incident with `u`. -/
def endpointClique (u : V) : Set G.edgeSet :=
  {e | u ∈ (e : Sym2 V)}

/-- Distinct edges through one endpoint are adjacent in the line graph. -/
theorem endpointClique_pairwise_adj (u : V) :
    (endpointClique G u).Pairwise (G.lineGraph.Adj) := by
  intro e he f hf hef
  rw [lineGraph_adj_iff_exists]
  exact ⟨hef, u, he, hf⟩

/-- Every neighbor of the edge-vertex `uv` lies in one of its two endpoint
cliques. -/
theorem neighborSet_subset_endpointCliques {u v : V} (huv : G.Adj u v) :
    G.lineGraph.neighborSet (⟨s(u, v), G.mem_edgeSet.mpr huv⟩ : G.edgeSet) ⊆
      endpointClique G u ∪ endpointClique G v := by
  intro e he
  rw [mem_neighborSet, lineGraph_adj_iff_exists] at he
  obtain ⟨_, w, hwuv, hwe⟩ := he
  rw [Sym2.mem_iff] at hwuv
  rcases hwuv with rfl | rfl
  · exact Or.inl hwe
  · exact Or.inr hwe

/-- An independent set meets any endpoint clique in at most one edge. -/
theorem independent_inter_endpointClique_subsingleton
    {S : Set G.edgeSet} (hS : G.lineGraph.IsIndepSet S) (u : V) :
    (S ∩ endpointClique G u).Subsingleton := by
  intro e he f hf
  by_contra hef
  exact hS he.1 hf.1 hef
    (endpointClique_pairwise_adj G u he.2 hf.2 hef)

/-- Any independent subset of the neighborhood of an edge-vertex in `L(G)`
has cardinality at most two. -/
theorem independent_ncard_le_two_of_subset_neighborSet [Fintype V]
    {u v : V} (huv : G.Adj u v) {S : Set G.edgeSet}
    (hS : G.lineGraph.IsIndepSet S)
    (hsub : S ⊆ G.lineGraph.neighborSet
      (⟨s(u, v), G.mem_edgeSet.mpr huv⟩ : G.edgeSet)) :
    S.ncard ≤ 2 := by
  have hcover : S ⊆ endpointClique G u ∪ endpointClique G v :=
    hsub.trans (neighborSet_subset_endpointCliques G huv)
  have hsplit : S = (S ∩ endpointClique G u) ∪
      (S ∩ endpointClique G v) := by
    ext e
    constructor
    · intro he
      rcases hcover he with heu | hev
      · exact Or.inl ⟨he, heu⟩
      · exact Or.inr ⟨he, hev⟩
    · rintro (⟨he, _⟩ | ⟨he, _⟩) <;> exact he
  rw [hsplit]
  calc
    ((S ∩ endpointClique G u) ∪ (S ∩ endpointClique G v)).ncard
        ≤ (S ∩ endpointClique G u).ncard +
          (S ∩ endpointClique G v).ncard := Set.ncard_union_le _ _
    _ ≤ 1 + 1 := Nat.add_le_add
      (Set.ncard_le_one_iff_subsingleton.mpr
        (independent_inter_endpointClique_subsingleton G hS u))
      (Set.ncard_le_one_iff_subsingleton.mpr
        (independent_inter_endpointClique_subsingleton G hS v))
    _ = 2 := rfl

/-- Source-shaped local form: the local independence number at every
edge-vertex of a finite line graph is at most two. -/
theorem neighbor_independent_ncard_le_two [Fintype V]
    {u v : V} (huv : G.Adj u v) {S : Set G.edgeSet}
    (hS : G.lineGraph.IsIndepSet S)
    (hSneighbor : S ⊆ G.lineGraph.neighborSet
      (⟨s(u, v), G.mem_edgeSet.mpr huv⟩ : G.edgeSet)) :
    S.ncard ≤ 2 :=
  independent_ncard_le_two_of_subset_neighborSet G huv hS hSneighbor

/-- Edges selected from `G` that are incident with a fixed original vertex.
This is the degree coordinate of the selected-edge subgraph, expressed
without introducing a second graph representation. -/
noncomputable def selectedIncidentEdges [Fintype V]
    (S : Finset G.edgeSet) (u : V) : Finset G.edgeSet := by
  classical
  exact S.filter fun e ↦ u ∈ (e : Sym2 V)

/-- A finite clique whose induced graph is bipartite has at most two
vertices.  Kept local so the line-graph coordinate lemma has no dependency on
the separate WOWII 183 development. -/
theorem clique_card_le_two_of_induce_isBipartite [Fintype V]
    (H : SimpleGraph G.edgeSet) (A : Finset G.edgeSet)
    (hclique : H.IsClique A)
    (hbip : (H.induce (↑A : Set G.edgeSet)).IsBipartite) :
    A.card ≤ 2 := by
  classical
  rw [induce_isBipartite_iff_exists_coloring] at hbip
  obtain ⟨color, hcolor⟩ := hbip
  let colorOnA : ↑A → Fin 2 := fun e ↦ color e
  have hinj : Function.Injective colorOnA := by
    intro e f hcolorEq
    apply Subtype.ext
    by_contra hef
    exact (hcolor e e.property f f.property
      (hclique e.property f.property hef)) hcolorEq
  simpa [colorOnA] using Fintype.card_le_of_injective colorOnA hinj

/-- **Selected-edge degree necessity.** If the line graph induced by a finite
edge selection `S` is bipartite, at most two selected edges are incident with
any original vertex.  Equivalently, the selected-edge subgraph has maximum
degree at most two, stated directly in incidence coordinates. -/
theorem selectedIncidentEdges_card_le_two_of_induce_isBipartite [Fintype V]
    (S : Finset G.edgeSet)
    (hbip : (G.lineGraph.induce (↑S : Set G.edgeSet)).IsBipartite)
    (u : V) :
    (selectedIncidentEdges G S u).card ≤ 2 := by
  classical
  let A := selectedIncidentEdges G S u
  have hAS : A ⊆ S := by
    intro e he
    simp only [A, selectedIncidentEdges, Finset.mem_filter] at he
    exact he.1
  have hAbip : (G.lineGraph.induce (↑A : Set G.edgeSet)).IsBipartite := by
    rw [induce_isBipartite_iff_exists_coloring] at hbip ⊢
    obtain ⟨color, hcolor⟩ := hbip
    exact ⟨color, fun e he f hf hef ↦
      hcolor e (hAS he) f (hAS hf) hef⟩
  apply clique_card_le_two_of_induce_isBipartite G G.lineGraph A
  · intro e he f hf hef
    have he' : e ∈ S ∧ u ∈ (e : Sym2 V) := by
      simpa [A, selectedIncidentEdges] using he
    have hf' : f ∈ S ∧ u ∈ (f : Sym2 V) := by
      simpa [A, selectedIncidentEdges] using hf
    exact endpointClique_pairwise_adj G u
      he'.2 hf'.2 hef
  · exact hAbip

end SimpleGraph.LineGraphEndpointCliques

#print axioms SimpleGraph.LineGraphEndpointCliques.neighborSet_subset_endpointCliques
#print axioms SimpleGraph.LineGraphEndpointCliques.independent_ncard_le_two_of_subset_neighborSet
#print axioms SimpleGraph.LineGraphEndpointCliques.selectedIncidentEdges_card_le_two_of_induce_isBipartite
