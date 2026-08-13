import FormalConjecturesUtil

/-!
# WOWII 133: lightweight residual-completion interface

This module records the exact 44-vertex adjacency table used by the full
residual-completion certificate, together with the constructive connectivity
proof needed by downstream metric checks.  It intentionally omits the costly
all-pairs girth and regularity checks already certified by the full module, so
that endpoint-rerouting certificates can rebuild within the 60-second cap.
-/

namespace WrittenOnTheWallII.GraphConjecture133ResidualCompletionInterface

open SimpleGraph

abbrev Vertex := Fin 44

def neighbors : Vertex → Finset Vertex := ![
  {1, 6, 7, 8}, {0, 2, 12, 17}, {1, 3, 13, 16}, {2, 4, 14, 15},
  {3, 5, 19, 42}, {4, 30, 32, 33}, {0, 9, 25, 39}, {0, 10, 20, 43},
  {0, 11, 29, 35}, {6, 12, 13, 15}, {7, 12, 14, 16}, {8, 13, 14, 17},
  {1, 9, 10, 40}, {2, 9, 11, 18}, {3, 10, 11, 31}, {3, 9, 24, 27},
  {2, 10, 22, 41}, {1, 11, 28, 36}, {13, 32, 35, 38}, {4, 35, 36, 37},
  {7, 34, 40, 42}, {33, 35, 39, 43}, {16, 31, 33, 34}, {32, 37, 40, 43},
  {15, 32, 39, 42}, {6, 31, 41, 43}, {34, 37, 39, 41}, {15, 33, 36, 41},
  {17, 31, 38, 40}, {8, 37, 38, 42}, {5, 34, 36, 38}, {14, 22, 25, 28},
  {5, 18, 23, 24}, {5, 21, 22, 27}, {20, 22, 26, 30}, {8, 18, 19, 21},
  {17, 19, 27, 30}, {19, 23, 26, 29}, {18, 28, 29, 30}, {6, 21, 24, 26},
  {12, 20, 23, 28}, {16, 25, 26, 27}, {4, 20, 24, 29}, {7, 21, 23, 25}
]

def completionGraph : SimpleGraph Vertex :=
  SimpleGraph.fromRel fun u v ↦ v ∈ neighbors u

instance : DecidableRel completionGraph.Adj := by
  intro u v
  simp only [completionGraph, SimpleGraph.fromRel_adj]
  infer_instance

def rank : Vertex → Nat := ![
  0, 1, 2, 3, 4, 5, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 2, 3, 3, 2, 3,
  4, 3, 3, 2, 3, 4, 3, 2, 4, 3, 4, 4, 3, 2, 3, 3, 3, 2, 3, 3, 3, 2
]

def parent : Vertex → Vertex := ![
  0, 0, 1, 2, 3, 4, 0, 0, 0, 6, 7, 8, 1, 2, 10, 9, 2, 1, 35, 35, 7,
  35, 16, 43, 39, 6, 39, 15, 17, 8, 34, 25, 18, 21, 20, 8, 17, 29, 29,
  6, 12, 25, 20, 7
]

theorem root_or_parent_step (v : Vertex) :
    v = 0 ∨ (rank (parent v) < rank v ∧ completionGraph.Adj (parent v) v) := by
  fin_cases v <;> decide

theorem reachable_from_zero (v : Vertex) : completionGraph.Reachable 0 v := by
  generalize hn : rank v = n
  induction n using Nat.strong_induction_on generalizing v with
  | h n ih =>
      rcases root_or_parent_step v with rfl | ⟨hrank, hadj⟩
      · exact Reachable.refl 0
      · exact (ih (rank (parent v)) (by omega) (parent v) rfl).trans
          hadj.reachable

theorem completion_connected : completionGraph.Connected := by
  constructor
  intro u v
  exact (reachable_from_zero u).symm.trans (reachable_from_zero v)

end WrittenOnTheWallII.GraphConjecture133ResidualCompletionInterface
