import FormalConjecturesUtil

/-!
# WOWII 133: triangle incidence double counting

This file closes the representation-independent half of the triangle correction:
the sum of the numbers of triangles incident to each vertex is three times the
number of triangles.  It uses the source definition `numTrianglesAtVertex`, so
the result can be reused once neighborhood edges have been identified with
incident triangles.
-/

namespace WrittenOnTheWallII.GraphConjecture133TriangleIncidence

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Every 3-clique is counted once at each of its three vertices. -/
theorem sum_numTrianglesAtVertex_eq_three_mul
    (G : SimpleGraph V) [DecidableRel G.Adj] :
    (∑ v, numTrianglesAtVertex G v) =
      3 * (G.cliqueFinset 3).card := by
  classical
  let T := G.cliqueFinset 3
  let incident : V → Finset V → Prop := fun v s ↦ v ∈ s
  have hdouble :=
    Finset.sum_card_bipartiteAbove_eq_sum_card_bipartiteBelow
      incident (s := (Finset.univ : Finset V)) (t := T)
  rw [show (∑ v, numTrianglesAtVertex G v) =
      ∑ v ∈ (Finset.univ : Finset V),
        (Finset.bipartiteAbove incident T v).card by
          simp [numTrianglesAtVertex, T, incident,
            Finset.bipartiteAbove]]
  rw [hdouble]
  calc
    ∑ s ∈ T, (Finset.bipartiteBelow incident Finset.univ s).card
        = ∑ _s ∈ T, 3 := by
            apply Finset.sum_congr rfl
            intro s hs
            have hclique : G.IsNClique 3 s :=
              SimpleGraph.mem_cliqueFinset_iff.mp hs
            simp [Finset.bipartiteBelow, incident, hclique.card_eq]
    _ = 3 * T.card := by simp [mul_comm]

end WrittenOnTheWallII.GraphConjecture133TriangleIncidence
