import FormalConjecturesUtil
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Circumference
import Mathlib.Combinatorics.SimpleGraph.Hamiltonian

/-!
# Hamiltonian adapter for Dean cycle divisibility

The completed order-ten Dean trial is theorem-closed once Hamiltonicity is
available: a Hamiltonian cycle has length equal to the order of the graph, so
every divisor of that order divides a cycle length.  This file formalizes that
last implication only.  It deliberately neither assumes nor reproves Dirac's
theorem.
-/

namespace DeanHamiltonianDivisibility

open SimpleGraph

/-- A supplied Hamiltonian cycle witnesses Dean's cycle-length conclusion for
every divisor of the graph order. -/
theorem of_hamiltonianCycle {V : Type*} [Fintype V] [DecidableEq V]
    {G : SimpleGraph V}
    {v : V} {p : G.Walk v v} (hp : p.IsHamiltonianCycle) {k : ℕ}
    (hk : k ∣ Fintype.card V) :
    ∃ m ∈ G.cycleLengths, k ∣ m := by
  refine ⟨Fintype.card V, ?_, hk⟩
  exact ⟨v, p, hp.isCycle, hp.length_eq⟩

/-- A non-singleton Hamiltonian graph satisfies Dean's cycle-length conclusion
for every divisor of its order.  The non-singleton premise discharges
mathlib's convention that the singleton graph is Hamiltonian without carrying
a graph-theoretic cycle. -/
theorem of_isHamiltonian {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V)
    (hcard : Fintype.card V ≠ 1) (hham : G.IsHamiltonian) {k : ℕ}
    (hk : k ∣ Fintype.card V) :
    ∃ m ∈ G.cycleLengths, k ∣ m := by
  obtain ⟨v, p, hp⟩ := hham hcard
  exact of_hamiltonianCycle hp hk

/-- Exact arithmetic adapter used by the frozen Dean `k=5` trial: every
Hamiltonian graph on ten vertices contains a ten-cycle, and hence a cycle
whose length is divisible by five. -/
theorem order_ten_five {V : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V)
    (hcard : Fintype.card V = 10) (hham : G.IsHamiltonian) :
    ∃ m ∈ G.cycleLengths, m = 10 ∧ 5 ∣ m := by
  have hne : Fintype.card V ≠ 1 := by omega
  obtain ⟨v, p, hp⟩ := hham hne
  refine ⟨10, ?_, rfl, by norm_num⟩
  exact ⟨v, p, hp.isCycle, hp.length_eq.trans hcard⟩

end DeanHamiltonianDivisibility
