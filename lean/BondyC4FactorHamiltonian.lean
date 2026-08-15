import Mathlib.Combinatorics.SimpleGraph.Hamiltonian
import Mathlib.Combinatorics.SimpleGraph.Circulant
import Mathlib.Data.Fin.VecNotation

namespace BondyC4FactorHamiltonian

open SimpleGraph

/-- A concrete frozen v3.5 peripheral row (row 0). -/
private def rowZeroEdges : List (Fin 20 × Fin 20) :=
  [(0, 2), (0, 3), (0, 4), (0, 12), (1, 2), (1, 3), (1, 10), (1, 17),
   (2, 6), (2, 18), (3, 7), (3, 19), (4, 6), (4, 7), (4, 8), (5, 6),
   (5, 7), (5, 9), (5, 16), (6, 15), (7, 11), (8, 10), (8, 11), (8, 12),
   (9, 10), (9, 11), (9, 13), (10, 14), (11, 19), (12, 14), (12, 15),
   (13, 14), (13, 15), (13, 16), (14, 17), (15, 18), (16, 18), (16, 19),
   (17, 18), (17, 19)]

def rowZero : SimpleGraph (Fin 20) :=
  SimpleGraph.fromRel fun u v => (u, v) ∈ rowZeroEdges

instance : DecidableRel rowZero.Adj := by
  unfold rowZero
  infer_instance

private def rowZeroCycle : rowZero.Walk 0 0 :=
  Walk.cons (by native_decide : rowZero.Adj 0 2)
  (Walk.cons (by native_decide : rowZero.Adj 2 1)
  (Walk.cons (by native_decide : rowZero.Adj 1 3)
  (Walk.cons (by native_decide : rowZero.Adj 3 7)
  (Walk.cons (by native_decide : rowZero.Adj 7 4)
  (Walk.cons (by native_decide : rowZero.Adj 4 6)
  (Walk.cons (by native_decide : rowZero.Adj 6 5)
  (Walk.cons (by native_decide : rowZero.Adj 5 9)
  (Walk.cons (by native_decide : rowZero.Adj 9 10)
  (Walk.cons (by native_decide : rowZero.Adj 10 8)
  (Walk.cons (by native_decide : rowZero.Adj 8 11)
  (Walk.cons (by native_decide : rowZero.Adj 11 19)
  (Walk.cons (by native_decide : rowZero.Adj 19 16)
  (Walk.cons (by native_decide : rowZero.Adj 16 13)
  (Walk.cons (by native_decide : rowZero.Adj 13 14)
  (Walk.cons (by native_decide : rowZero.Adj 14 17)
  (Walk.cons (by native_decide : rowZero.Adj 17 18)
  (Walk.cons (by native_decide : rowZero.Adj 18 15)
  (Walk.cons (by native_decide : rowZero.Adj 15 12)
  (Walk.cons (by native_decide : rowZero.Adj 12 0) Walk.nil)))))))))))))))))))

private lemma rowZeroCycle_hamiltonian : rowZeroCycle.IsHamiltonianCycle := by
  rw [Walk.isHamiltonianCycle_iff_isCycle_and_support_count_tail_eq_one]
  constructor
  · simp [rowZeroCycle, Walk.isCycle_def, Walk.isTrail_def]
  · intro a
    fin_cases a <;> native_decide

/-- No-sorry Hamiltonicity proof for one exact frozen row. This is a
feasibility certificate for the finite-row route, not the general theorem. -/
theorem rowZero_isHamiltonian : rowZero.IsHamiltonian := by
  intro _
  exact ⟨0, rowZeroCycle, rowZeroCycle_hamiltonian⟩

end BondyC4FactorHamiltonian

#print axioms BondyC4FactorHamiltonian.rowZero_isHamiltonian
