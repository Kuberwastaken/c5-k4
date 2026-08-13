import FormalConjecturesUtil

/-!
# Independent-domination leaf-transfer coordinates

This file extracts the exact arithmetic and parity transfer from the completed
`H(5,5)` leaf-transfer trial.  It keeps the graph invariant equalities as
premises: the coordinate calculation certifies a graph once its order,
maximum degree, and independent domination number have been established, but
does not pretend to construct that graph or prove those invariants.
-/

namespace IndependentDominationLeafTransferCoordinates

open SimpleGraph

/-- The left side of the upstream even-degree declaration. -/
def evenLeft (D i : ℕ) : ℕ := (D + 2) ^ 2 * i

/-- The right side of the upstream even-degree declaration. -/
def evenRight (n D : ℕ) : ℕ := (D ^ 2 + 4) * n

/-- Exact safe-side slack, oriented as `left + slack = right`. -/
def HasEvenSlack (n D i slack : ℕ) : Prop :=
  evenLeft D i + slack = evenRight n D

/-- An exact nonnegative residual certificate implies the upstream-oriented
even independent-domination inequality. -/
theorem even_bound_of_slack {n D i slack : ℕ}
    (hslack : HasEvenSlack n D i slack) :
    (D + 2) ^ 2 * i ≤ (D ^ 2 + 4) * n := by
  unfold HasEvenSlack evenLeft evenRight at hslack
  omega

/-- The transformed trial coordinates have even maximum degree and exact
safe-side slack 240. -/
theorem transformed_coordinates :
    Even 10 ∧ HasEvenSlack 30 10 20 240 := by
  constructor
  · exact ⟨5, by norm_num⟩
  · norm_num [HasEvenSlack, evenLeft, evenRight]

/-- Graph-level adapter for the frozen transformed witness.  The three graph
invariants remain explicit certificate premises.  The conclusions reproduce
the parity premise, the declaration's multiplication order, and exact slack
orientation. -/
theorem graph_adapter {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hn : Fintype.card V = 30)
    (hD : G.maxDegree = 10)
    (hi : G.indepDominationNumber = 20) :
    Even G.maxDegree ∧
      (G.maxDegree + 2) ^ 2 * G.indepDominationNumber ≤
        (G.maxDegree ^ 2 + 4) * Fintype.card V ∧
      (G.maxDegree + 2) ^ 2 * G.indepDominationNumber + 240 =
        (G.maxDegree ^ 2 + 4) * Fintype.card V := by
  rw [hn, hD, hi]
  constructor
  · exact transformed_coordinates.1
  constructor
  · exact even_bound_of_slack transformed_coordinates.2
  · exact transformed_coordinates.2

/-- The same exact residual in subtraction notation, derived only after the
stronger addition-oriented equality. -/
theorem graph_adapter_residual {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [DecidableRel G.Adj]
    (hn : Fintype.card V = 30)
    (hD : G.maxDegree = 10)
    (hi : G.indepDominationNumber = 20) :
    (G.maxDegree ^ 2 + 4) * Fintype.card V -
      (G.maxDegree + 2) ^ 2 * G.indepDominationNumber = 240 := by
  obtain ⟨_, _, hslack⟩ := graph_adapter G hn hD hi
  omega

end IndependentDominationLeafTransferCoordinates
