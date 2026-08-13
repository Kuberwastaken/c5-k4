import GraphConjecture19UnicyclicCharge

/-!
# WOWII 19/13: portable odd-unicyclic core certificate
-/

namespace WrittenOnTheWallII.GraphConjecture19OddUnicyclic

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19EndpointMax
open WrittenOnTheWallII.GraphConjecture19MetricIntersection
open WrittenOnTheWallII.GraphConjecture19UnicyclicCharge

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

/-- Portable structural data extracted from an odd-unicyclic decomposition.
Besides a cycle vertex whose deletion is bipartite, it records the extra
cycle-core vertex missed by the extremal path/neighborhood union precisely in
the two equality-danger cases. -/
structure OddUnicyclicCoreCertificate (G : SimpleGraph V)
    [DecidableRel G.Adj] where
  cycleVertex : V
  deleteCycleVertexBipartite :
    (G.induce (↑(Finset.univ.erase cycleVertex) : Set V)).IsBipartite
  maxVertex : V
  maxVertex_degree : G.maxDegree = G.degree maxVertex
  endpointLeft : V
  endpointRight : V
  diametral : G.dist endpointLeft endpointRight = G.diam
  path : G.Walk endpointLeft endpointRight
  path_isPath : path.IsPath
  path_shortest : path.length = G.dist endpointLeft endpointRight
  surplus_on_path :
    maxVertex ∈ path.support.toFinset →
      ∃ z : V, z ∉ path.support.toFinset ∪ G.neighborFinset maxVertex
  surplus_off_path_at_three :
    maxVertex ∉ path.support.toFinset →
    (path.support.toFinset ∩ G.neighborFinset maxVertex).card = 3 →
      ∃ z : V,
        z ∉ insert maxVertex
          (path.support.toFinset ∪ G.neighborFinset maxVertex)

/-- One extra vertex outside a finite set strengthens its cardinality bound by
one. -/
lemma card_add_one_le_card_univ_of_exists_not_mem (S : Finset V)
    (h : ∃ z : V, z ∉ S) :
    S.card + 1 ≤ Fintype.card V := by
  obtain ⟨z, hz⟩ := h
  rw [← card_insert_of_notMem hz]
  exact (insert z S).card_le_univ

/-- A certified odd-cycle surplus sharpens the classical diameter--degree
bound by one. -/
theorem diameter_add_maxDegree_le_card_of_coreCertificate
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (C : OddUnicyclicCoreCertificate G) :
    G.diam + G.maxDegree ≤ Fintype.card V := by
  let P := C.path.support.toFinset
  let N := G.neighborFinset C.maxVertex
  have hP : P.card = G.diam + 1 := by
    dsimp [P]
    rw [List.toFinset_card_of_nodup C.path_isPath.support_nodup,
      C.path.length_support, C.path_shortest, C.diametral]
  have hN : N.card = G.maxDegree := C.maxVertex_degree.symm
  have hm := diametralNeighborhoodIntersectionBound G
    (c := C.maxVertex) C.path C.path_isPath C.path_shortest
      (C.path_shortest.trans C.diametral)
  change (C.maxVertex ∈ P → (P ∩ N).card ≤ 2) ∧
    (C.maxVertex ∉ P → (P ∩ N).card ≤ 3) at hm
  by_cases hcP : C.maxVertex ∈ P
  · have hinter := hm.1 hcP
    have hplus := card_add_one_le_card_univ_of_exists_not_mem
      (P ∪ N) (C.surplus_on_path hcP)
    rw [Finset.card_union, hP, hN] at hplus
    omega
  · have hinter := hm.2 hcP
    by_cases hthree : (P ∩ N).card = 3
    · have hplus := card_add_one_le_card_univ_of_exists_not_mem
        (insert C.maxVertex (P ∪ N))
        (C.surplus_off_path_at_three hcP hthree)
      have hcN : C.maxVertex ∉ N := by dsimp [N]; simp
      have hcUnion : C.maxVertex ∉ P ∪ N := by simp [hcP, hcN]
      rw [card_insert_of_notMem hcUnion, Finset.card_union, hP, hN,
        hthree] at hplus
      omega
    · have hleTwo : (P ∩ N).card ≤ 2 := by omega
      have hunion : (insert C.maxVertex (P ∪ N)).card ≤
          Fintype.card V := (insert C.maxVertex (P ∪ N)).card_le_univ
      have hcN : C.maxVertex ∉ N := by dsimp [N]; simp
      have hcUnion : C.maxVertex ∉ P ∪ N := by simp [hcP, hcN]
      rw [card_insert_of_notMem hcUnion, Finset.card_union, hP, hN] at hunion
      omega

/-- Blanket WOWII 13 theorem for the explicit portable odd-unicyclic core
class. -/
theorem wowii13_of_oddUnicyclicCoreCertificate
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected) (C : OddUnicyclicCoreCertificate G) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  apply wowii13_of_odd_unicyclic_certificate G C.cycleVertex hconn
    C.deleteCycleVertexBipartite
  exact Or.inr (diameter_add_maxDegree_le_card_of_coreCertificate G C)

end WrittenOnTheWallII.GraphConjecture19OddUnicyclic
