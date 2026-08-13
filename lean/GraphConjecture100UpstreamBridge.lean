import GraphConjecture100ConnectedClosure

/-!
# WOWII 100: direct upstream-signature bridge

The theorem below deliberately repeats the hypotheses and conclusion currently
used by `FormalConjectures/WrittenOnTheWallII/GraphConjecture100.lean`.

The formal conclusion contains `degreeL2Norm Gᶜ`.  Although the upstream
module's prose discusses the diameter of the complement, this bridge proves
only the displayed Lean declaration and does not identify those quantities.
-/

namespace WrittenOnTheWallII.GraphConjecture100

open SimpleGraph
open WrittenOnTheWallII.GraphConjecture100ConnectedClosure

variable {α : Type*} [Fintype α] [DecidableEq α] [Nontrivial α]

/-- Direct drop-in proof of the current upstream `conjecture100` declaration.
The complement-connectedness hypothesis is retained to match upstream exactly,
although the stronger connected closure does not need it. -/
theorem conjecture100_upstream_bridge
    (G : SimpleGraph α) [DecidableRel G.Adj] (h : G.Connected)
    (_hGc : Gᶜ.Connected) :
    let maxL := (Finset.univ.image (indepNeighborsCard G)).max' (by simp)
    (G.indepNum : ℝ) ≤
      ⌈((maxL : ℝ) + (1 / 2) * (degreeL2Norm Gᶜ : ℝ)) / 2⌉ := by
  exact conjecture100_of_connected G h

end WrittenOnTheWallII.GraphConjecture100
