import GraphConjecture19StarBound
import GraphConjecture19Eccentricity

/-!
# WOWII 19: the self-centered diameter-two branch

This file closes a genuine branch of the graph-theoretic obstruction isolated
for WOWII 19.  In a self-centered graph of diameter two, every vertex has a
non-neighbor.  At a vertex attaining the maximum local independence number,
that non-neighbor supplies the one-vertex outside independent set in the
induced-star bound.  The resulting induced bipartite subgraph has order
`lambda_max + 2`, exactly the conjectured right-hand side because every
eccentricity is two.
-/

namespace WrittenOnTheWallII.GraphConjecture19Combinatorial

open SimpleGraph Finset

universe u

variable {V : Type u} [Fintype V] [DecidableEq V]

omit [Fintype V] [DecidableEq V] in
/-- Self-centeredness identifies every eccentricity with the diameter. -/
lemma eccent_eq_ediam_of_radius_eq_ediam (G : SimpleGraph V) [Nonempty V]
    (hself : G.radius = G.ediam) (v : V) :
    G.eccent v = G.ediam := by
  exact le_antisymm G.eccent_le_ediam (hself ▸ G.radius_le_eccent)

omit [DecidableEq V] in
/-- In a connected self-centered diameter-two graph, every vertex has a
distinct non-neighbor. -/
lemma exists_nonneighbor_of_radius_eq_ediam_diam_eq_two
    (G : SimpleGraph V) [Nonempty V] (hconn : G.Connected)
    (hself : G.radius = G.ediam) (hdiam : G.diam = 2) (v : V) :
    ∃ w : V, w ≠ v ∧ ¬G.Adj v w := by
  obtain ⟨w, hw⟩ := G.exists_edist_eq_eccent_of_finite v
  have hed_ne : G.ediam ≠ ⊤ := SimpleGraph.connected_iff_ediam_ne_top.mp hconn
  have hed : G.ediam = (2 : ℕ∞) := by
    have hcoe : (G.diam : ℕ∞) = G.ediam := ENat.coe_toNat hed_ne
    simpa [hdiam] using hcoe.symm
  have hedvw : G.edist v w = (2 : ℕ∞) := by
    rw [hw, eccent_eq_ediam_of_radius_eq_ediam G hself v, hed]
  refine ⟨w, ?_, ?_⟩
  · intro hwv
    subst w
    simp at hedvw
  · intro hadj
    have hone : G.edist v w = 1 := edist_eq_one_iff_adj.mpr hadj
    rw [hone] at hedvw
    norm_num at hedvw

/-- A non-neighbor supplies the singleton outside independent set in the
induced-star lower bound. -/
theorem indepNeighborsCard_add_two_le_b_of_nonneighbor
    (G : SimpleGraph V) [DecidableRel G.Adj] (v w : V)
    (hwv : w ≠ v) (hnotadj : ¬G.Adj v w) :
    ((indepNeighborsCard G v + 2 : ℕ) : ℝ) ≤ b G := by
  have hI : G.IsIndepSet (({w} : Finset V) : Set V) := by
    simp
  have hIout : ∀ x ∈ ({w} : Finset V), x ≠ v ∧ ¬G.Adj v x := by
    intro x hx
    simp only [mem_singleton] at hx
    subst x
    exact ⟨hwv, hnotadj⟩
  have hstar :=
    _root_.WrittenOnTheWallII.GraphConjecture19StarBound.indepNeighborsCard_add_card_add_one_le_b
      G v ({w} : Finset V) hI hIout
  norm_num at hstar ⊢
  linarith

/-- Consequently, a self-centered diameter-two graph has an induced
bipartite subgraph of order at least two plus its maximum local independence
number, in the exact `sSup` syntax of WOWII 19. -/
theorem two_add_sSup_indepNeighbors_le_b_of_self_centered_diam_two
    (G : SimpleGraph V) [Nonempty V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hself : G.radius = G.ediam)
    (hdiam : G.diam = 2) :
    2 + sSup (Set.range (indepNeighbors G)) ≤ b G := by
  obtain ⟨v, hv⟩ :=
    _root_.WrittenOnTheWallII.GraphConjecture19Eccentricity.exists_indepNeighborsCard_cast_eq_sSup
      G
  obtain ⟨w, hwv, hnotadj⟩ :=
    exists_nonneighbor_of_radius_eq_ediam_diam_eq_two G hconn hself hdiam v
  have hbound := indepNeighborsCard_add_two_le_b_of_nonneighbor
    G v w hwv hnotadj
  rw [← hv]
  norm_num at hbound ⊢
  linarith

omit [Fintype V] [DecidableEq V] in
/-- Every natural eccentricity is exactly two in the branch under study. -/
lemma eccent_toNat_eq_two_of_radius_eq_ediam_diam_eq_two
    (G : SimpleGraph V) [Nonempty V]
    (hself : G.radius = G.ediam) (hdiam : G.diam = 2) (v : V) :
    (G.eccent v).toNat = 2 := by
  rw [eccent_eq_ediam_of_radius_eq_ediam G hself v]
  exact hdiam

omit [DecidableEq V] in
/-- The exact upstream eccentricity average is two in a self-centered graph
of diameter two. -/
lemma average_eccentricity_eq_two_of_radius_eq_ediam_diam_eq_two
    (G : SimpleGraph V) [Nonempty V]
    (hself : G.radius = G.ediam) (hdiam : G.diam = 2) :
    ( ∑ v ∈ Finset.univ, ((G.eccent v).toNat : ℝ)) /
        (Fintype.card V : ℝ) = 2 := by
  simp_rw [eccent_toNat_eq_two_of_radius_eq_ediam_diam_eq_two G hself hdiam]
  simp [Fintype.card_ne_zero]

/-- WOWII 19 holds, with its exact formalized right-hand side, throughout
the self-centered diameter-two branch. -/
theorem conjecture19_of_radius_eq_ediam_diam_eq_two
    (G : SimpleGraph V) [Nontrivial V] [DecidableRel G.Adj]
    (hconn : G.Connected) (hself : G.radius = G.ediam)
    (hdiam : G.diam = 2) :
    ⌊(∑ v ∈ Finset.univ, ((G.eccent v).toNat : ℝ)) /
          (Fintype.card V : ℝ) +
        sSup (Set.range (indepNeighbors G))⌋ ≤ b G := by
  rw [average_eccentricity_eq_two_of_radius_eq_ediam_diam_eq_two
    G hself hdiam]
  have hbound :=
    two_add_sSup_indepNeighbors_le_b_of_self_centered_diam_two
      G hconn hself hdiam
  have hsSupInt : ∃ n : ℕ,
      sSup (Set.range (indepNeighbors G)) = (n : ℝ) := by
    obtain ⟨v, hv⟩ :=
      _root_.WrittenOnTheWallII.GraphConjecture19Eccentricity.exists_indepNeighborsCard_cast_eq_sSup
        G
    exact ⟨indepNeighborsCard G v, hv.symm⟩
  obtain ⟨n, hn⟩ := hsSupInt
  rw [hn] at hbound ⊢
  norm_num at hbound ⊢
  exact hbound

end WrittenOnTheWallII.GraphConjecture19Combinatorial
