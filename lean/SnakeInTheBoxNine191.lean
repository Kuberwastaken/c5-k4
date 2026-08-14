import FormalConjectures.Wikipedia.SnakeInTheBox

/-!
# A 191-edge snake in the 9-cube

This file certifies the dimension-nine transition sequence published in
P. Orland, L. Fagan et al., *A Census of New Snake-in-the-Box Records*,
arXiv:2607.15270v2 (July 2026), Section 3.

The transition sequence below is verbatim (whitespace removed) from the paper
and its public record-table mirror.  Its canonical digit string is

`01230431035430123043103563012354321351032135431237532103543013503210356301234532134103213453084036452031235432136415023124012316301235634721354312301431235432103653012305310345301230531078012`.

Audited source snapshot SHA-256:
`62fe3f292411694cfd72261437bbcd841220f3c2dc4f4e25b9a553497ee743c0`.
Paper PDF SHA-256:
`02529c7852f3b089e0f689c34c80ad158c76f920ed49cf537a3c561234020e87`.
-/

namespace SnakeInTheBoxNine191

set_option maxRecDepth 10000

open SimpleGraph symmDiff
open SnakeInBox

/-- Toggle one hypercube coordinate. -/
def toggle (v : Finset (Fin 9)) (i : Fin 9) : Finset (Fin 9) := v ∆ {i}

/-- A coordinate toggle is an edge of the formalized nine-dimensional cube. -/
theorem adj_toggle (v : Finset (Fin 9)) (i : Fin 9) :
    (Hypercube 9).Adj v (toggle v i) := by
  change (v ∆ toggle v i).card = 1
  have htoggle : v ∆ toggle v i = {i} := by
    ext x
    by_cases hxv : x ∈ v <;> by_cases hxi : x = i <;>
      simp [toggle, Finset.mem_symmDiff, hxv, hxi]
  rw [htoggle]
  simp

/-- The exact published transition sequence, with 0-indexed coordinates. -/
def transitions : List (Fin 9) := [
  0, 1, 2, 3, 0, 4, 3, 1, 0, 3, 5, 4, 3, 0, 1, 2, 3, 0, 4, 3, 1, 0, 3, 5,
  6, 3, 0, 1, 2, 3, 5, 4, 3, 2, 1, 3, 5, 1, 0, 3, 2, 1, 3, 5, 4, 3, 1, 2,
  3, 7, 5, 3, 2, 1, 0, 3, 5, 4, 3, 0, 1, 3, 5, 0, 3, 2, 1, 0, 3, 5, 6, 3,
  0, 1, 2, 3, 4, 5, 3, 2, 1, 3, 4, 1, 0, 3, 2, 1, 3, 4, 5, 3, 0, 8, 4, 0,
  3, 6, 4, 5, 2, 0, 3, 1, 2, 3, 5, 4, 3, 2, 1, 3, 6, 4, 1, 5, 0, 2, 3, 1,
  2, 4, 0, 1, 2, 3, 1, 6, 3, 0, 1, 2, 3, 5, 6, 3, 4, 7, 2, 1, 3, 5, 4, 3,
  1, 2, 3, 0, 1, 4, 3, 1, 2, 3, 5, 4, 3, 2, 1, 0, 3, 6, 5, 3, 0, 1, 2, 3,
  0, 5, 3, 1, 0, 3, 4, 5, 3, 0, 1, 2, 3, 0, 5, 3, 1, 0, 7, 8, 0, 1, 2]

theorem transitions_length : transitions.length = 191 := by decide

/-- Endpoint after applying a list of coordinate toggles. -/
def endpoint (v : Finset (Fin 9)) : List (Fin 9) → Finset (Fin 9)
  | [] => v
  | i :: is => endpoint (toggle v i) is

/-- The graph walk determined by a transition list. -/
def walkFrom (v : Finset (Fin 9)) :
    (is : List (Fin 9)) → (Hypercube 9).Walk v (endpoint v is)
  | [] => .nil
  | i :: is => .cons (adj_toggle v i) (walkFrom (toggle v i) is)

/-- The published walk, beginning at the all-zero cube vertex. -/
def snakeWalk : (Hypercube 9).Walk ∅ (endpoint ∅ transitions) :=
  walkFrom ∅ transitions

/-- The 192 visited vertices in path order. -/
def vertices : List (Finset (Fin 9)) :=
  transitions.scanl toggle ∅

theorem snakeWalk_support : snakeWalk.support = vertices := by rfl

/-- The constructed walk has exactly the published number of edges. -/
theorem snakeWalk_length : snakeWalk.length = 191 := by decide

/-- Kernel reduction checks that all 192 published vertices are distinct. -/
theorem vertices_nodup : vertices.Nodup := by decide

/-- Four independently reducible distinctness checkpoints.  They keep the
large literal auditable in bounded pieces in addition to the full theorem. -/
theorem vertices_prefix_48_nodup : (vertices.take 48).Nodup := by decide
theorem vertices_middle_48_nodup : ((vertices.drop 48).take 48).Nodup := by decide
theorem vertices_middle_two_48_nodup : ((vertices.drop 96).take 48).Nodup := by decide
theorem vertices_suffix_nodup : (vertices.drop 144).Nodup := by decide

/-- Distinctness of the explicit support makes the walk a graph-theoretic path. -/
theorem snakeWalk_isPath : snakeWalk.IsPath := by
  apply SimpleGraph.Walk.IsPath.mk'
  rw [snakeWalk_support]
  exact vertices_nodup

/-- Kernel reduction checks that the ambient cube has no edge between two
nonconsecutive vertices of the published path. -/
theorem snakeWalk_isInduced : snakeWalk.toSubgraph.IsInduced := by decide

/-- The explicit subgraph and walk satisfy the corrected upstream definition
of a length-191 snake. -/
theorem published_isSnake :
    IsSnakeInGraphOfLength (Hypercube 9) snakeWalk.toSubgraph 191 := by
  refine ⟨snakeWalk_isInduced, ⟨∅, endpoint ∅ transitions, snakeWalk, ?_, rfl, ?_⟩⟩
  · exact snakeWalk_isPath
  · exact snakeWalk_length

/-- Honest adapter from the explicit certificate to the upstream `sSup`
definition.  This proves a lower bound only; it makes no optimality claim. -/
theorem one_hundred_ninety_one_le_longestSnakeInTheBox :
    191 ≤ LongestSnakeInTheBox 9 := by
  unfold LongestSnakeInTheBox LongestSnakeInGraph
  apply le_csSup
  exact ⟨snakeWalk.toSubgraph, published_isSnake⟩

#print axioms published_isSnake
#print axioms one_hundred_ninety_one_le_longestSnakeInTheBox

end SnakeInTheBoxNine191
