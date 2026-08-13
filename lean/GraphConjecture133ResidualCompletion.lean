import FormalConjecturesUtil

/-!
# WOWII 133: residual completion countermodel

The sharp six-third cross-branch survivor admits a genuine finite completion.
This 44-vertex graph contains the frozen geodesic/branch/parent/third/blocker
core, is connected and four-regular, has no triangle or four-cycle, and keeps
the distinguished endpoints at distance exactly five.

The completion was constructed by attaching the twenty residual core stubs to
the endpoints of ten deleted edges in the 26-vertex incidence graph of
`PG(2,3)`.  This file records the resulting graph directly and checks its
properties in the Lean kernel.
-/

namespace WrittenOnTheWallII.GraphConjecture133ResidualCompletion

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

def completionGraph : SimpleGraph Vertex where
  Adj u v := v ∈ neighbors u
  symm := by
    intro u v h
    fin_cases u <;> fin_cases v <;> decide
  loopless := by
    intro u
    fin_cases u <;> decide

instance : DecidableRel completionGraph.Adj := by
  intro u v
  change Decidable (v ∈ neighbors u)
  infer_instance

theorem neighborFinset_eq_neighbors (v : Vertex) :
    completionGraph.neighborFinset v = neighbors v := by
  ext w
  simp [completionGraph]

theorem completion_four_regular :
    completionGraph.IsRegularOfDegree 4 := by
  intro v
  rw [← completionGraph.card_neighborFinset_eq_degree,
    neighborFinset_eq_neighbors]
  fin_cases v <;> decide

def HasTriangle : Prop :=
  ∃ a b c : Vertex,
    a ≠ b ∧ a ≠ c ∧ b ≠ c ∧
      completionGraph.Adj a b ∧ completionGraph.Adj b c ∧
      completionGraph.Adj c a

def HasC4 : Prop :=
  ∃ a b c d : Vertex,
    a ≠ b ∧ a ≠ c ∧ a ≠ d ∧ b ≠ c ∧ b ≠ d ∧ c ≠ d ∧
      completionGraph.Adj a b ∧ completionGraph.Adj b c ∧
      completionGraph.Adj c d ∧ completionGraph.Adj d a

def commonNeighbors (u v : Vertex) : Finset Vertex :=
  (neighbors u).filter fun z ↦ z ∈ neighbors v

theorem common_neighbors_le_one (u v : Vertex) (h : u ≠ v) :
    (commonNeighbors u v).card ≤ 1 := by
  revert h
  fin_cases u <;> fin_cases v <;> decide

theorem no_triangle : ¬HasTriangle := by
  decide

theorem no_C4 : ¬HasC4 := by
  rintro ⟨a, b, c, d, _hab, hac, _had, _hbc, hbd, _hcd,
    hab, hbc, hcd, hda⟩
  have hle := common_neighbors_le_one a c hac
  have hbmem : b ∈ commonNeighbors a c := by
    simp [commonNeighbors, hab, hbc]
  have hdmem : d ∈ commonNeighbors a c := by
    simp [commonNeighbors, hda, hcd]
  exact hbd (Finset.card_le_one.mp hle b hbmem d hdmem)

/-- A walk of length at most four between the distinguished endpoints. -/
def HasShortEndpointWalk : Prop :=
  completionGraph.Adj 0 5 ∨
  (∃ a, completionGraph.Adj 0 a ∧ completionGraph.Adj a 5) ∨
  (∃ a b, completionGraph.Adj 0 a ∧ completionGraph.Adj a b ∧
    completionGraph.Adj b 5) ∨
  (∃ a b c, completionGraph.Adj 0 a ∧ completionGraph.Adj a b ∧
    completionGraph.Adj b c ∧ completionGraph.Adj c 5)

theorem no_endpoint_walk_shorter_than_five : ¬HasShortEndpointWalk := by
  decide

theorem endpoint_path_of_length_five :
    completionGraph.Adj 0 1 ∧ completionGraph.Adj 1 2 ∧
    completionGraph.Adj 2 3 ∧ completionGraph.Adj 3 4 ∧
    completionGraph.Adj 4 5 := by
  decide

/-- The frozen 18-vertex core from v0.31 is present verbatim.  Vertices
`0..5` are the geodesic, `6..8` first choices, `9..11` parents, and `12..17`
the six thirds. -/
def FrozenCorePreserved : Prop :=
  (completionGraph.Adj 0 1 ∧ completionGraph.Adj 1 2 ∧
    completionGraph.Adj 2 3 ∧ completionGraph.Adj 3 4 ∧
    completionGraph.Adj 4 5) ∧
  (completionGraph.Adj 0 6 ∧ completionGraph.Adj 0 7 ∧
    completionGraph.Adj 0 8) ∧
  (completionGraph.Adj 6 9 ∧ completionGraph.Adj 7 10 ∧
    completionGraph.Adj 8 11) ∧
  (completionGraph.Adj 9 12 ∧ completionGraph.Adj 9 13 ∧
    completionGraph.Adj 9 15) ∧
  (completionGraph.Adj 10 12 ∧ completionGraph.Adj 10 14 ∧
    completionGraph.Adj 10 16) ∧
  (completionGraph.Adj 11 13 ∧ completionGraph.Adj 11 14 ∧
    completionGraph.Adj 11 17) ∧
  (completionGraph.Adj 12 1 ∧ completionGraph.Adj 13 2 ∧
    completionGraph.Adj 14 3 ∧ completionGraph.Adj 15 3 ∧
    completionGraph.Adj 16 2 ∧ completionGraph.Adj 17 1)

theorem frozen_core_preserved : FrozenCorePreserved := by
  decide

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

/-- Kernel-checked completion package. -/
theorem residual_completion_certificate :
    FrozenCorePreserved ∧ completionGraph.Connected ∧
    completionGraph.IsRegularOfDegree 4 ∧ ¬HasTriangle ∧ ¬HasC4 ∧
    ¬HasShortEndpointWalk ∧
    (completionGraph.Adj 0 1 ∧ completionGraph.Adj 1 2 ∧
      completionGraph.Adj 2 3 ∧ completionGraph.Adj 3 4 ∧
      completionGraph.Adj 4 5) := by
  exact ⟨frozen_core_preserved, completion_connected,
    completion_four_regular, no_triangle, no_C4,
    no_endpoint_walk_shorter_than_five, endpoint_path_of_length_five⟩

end WrittenOnTheWallII.GraphConjecture133ResidualCompletion
