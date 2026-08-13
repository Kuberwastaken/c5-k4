import GraphConjecture19EndpointMax

/-!
# WOWII 19/13: whole-graph and one-deletion multi-arm certificates

The one-tail construction can lose an entire second branch.  This file records
the complementary certificate: retain all branches simultaneously, either as
the whole graph when bipartite or after deleting one odd-cycle transversal
vertex.
-/

namespace WrittenOnTheWallII.GraphConjecture19MultiArm

open SimpleGraph Finset
open WrittenOnTheWallII.GraphConjecture19EndpointMax

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [DecidableEq V] in
/-- Any explicitly supplied induced bipartite vertex set gives its exact order
as a lower bound on `b`. -/
theorem card_le_b_of_induced_bipartite (G : SimpleGraph V) (S : Finset V)
    (hS : (G.induce (↑S : Set V)).IsBipartite) :
    (S.card : ℝ) ≤ b G := by
  unfold b
  exact_mod_cast
    _root_.WrittenOnTheWallII.GraphConjecture19EndpointWitness.card_le_largestInducedBipartiteSubgraphSize
      G S hS

omit [DecidableEq V] in
/-- Retaining every branch of an already bipartite graph gives `b >= |V|`. -/
theorem card_univ_le_b_of_bipartite (G : SimpleGraph V)
    (hG : G.IsBipartite) :
    (Fintype.card V : ℝ) ≤ b G := by
  apply card_le_b_of_induced_bipartite G Finset.univ
  rcases hG with ⟨c⟩
  exact ⟨Coloring.mk (fun x => c x.val) fun {_x _y} hxy => c.valid hxy⟩

/-- Deleting one vertex while retaining every remaining arm gives
`b >= |V|-1`. -/
theorem card_sub_one_le_b_of_delete_vertex (G : SimpleGraph V) (z : V)
    (hz : (G.induce (↑(Finset.univ.erase z) : Set V)).IsBipartite) :
    ((Fintype.card V - 1 : ℕ) : ℝ) ≤ b G := by
  have hb := card_le_b_of_induced_bipartite G (Finset.univ.erase z) hz
  rw [Finset.card_erase_of_mem (Finset.mem_univ z), Finset.card_univ] at hb
  exact hb

omit [DecidableEq V] in
/-- Full WOWII 13 from the all-arms bipartite certificate and the exact
counting condition witnessed by a diametral path plus the remaining arms. -/
theorem wowii13_of_bipartite_of_count
    (G : SimpleGraph V) [Nonempty V] (hG : G.IsBipartite)
    (hcount : G.diam + localMax G ≤ Fintype.card V + 1) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  have hb := card_univ_le_b_of_bipartite G hG
  have hcR : (G.diam : ℝ) + (localMax G : ℝ) ≤
      (Fintype.card V : ℝ) + 1 := by exact_mod_cast hcount
  linarith

/-- Full WOWII 13 from a one-vertex odd-cycle-transversal certificate. -/
theorem wowii13_of_delete_vertex_of_count
    (G : SimpleGraph V) [Nonempty V] (z : V)
    (hz : (G.induce (↑(Finset.univ.erase z) : Set V)).IsBipartite)
    (hcount : G.diam + localMax G ≤ Fintype.card V) :
    (G.diam : ℝ) + (localMax G : ℝ) - 1 ≤ b G := by
  have hb := card_sub_one_le_b_of_delete_vertex G z hz
  have hcard : 1 ≤ Fintype.card V := Fintype.card_pos
  have hb' : (Fintype.card V : ℝ) - 1 ≤ b G := by
    have hsub : ((Fintype.card V - 1 : ℕ) : ℝ) =
        (Fintype.card V : ℝ) - 1 := by
      rw [Nat.cast_sub hcard]
      norm_num
    rw [← hsub]
    exact hb
  have hcR : (G.diam : ℝ) + (localMax G : ℝ) ≤
      (Fintype.card V : ℝ) := by exact_mod_cast hcount
  linarith

end WrittenOnTheWallII.GraphConjecture19MultiArm
