import FormalConjecturesUtil

/-!
# WOWII 141: the `K3,3-e` two-lift parity obstruction

After switching a two-sheet voltage assignment to zero on the five fixed
spanning-tree edges, its remaining data are the three cotree voltages
`x15`, `x23`, and `x35`.  The five base four-cycles then have the parity
forms recorded below.  This file proves algebraically that at least one form
is even for every assignment.  It also records the exact seven nonzero
gauge-fixed triples used by the prospective trial.

The graph-theoretic adapter -- that an even voltage on a simple base cycle
lifts to a cycle of the same length -- is deliberately not asserted here.
The result below is the complete finite-field obstruction on which that
standard covering-space adapter acts.
-/

namespace WrittenOnTheWallII.Wow141K33eTwoLiftParity

/-- The three cotree voltages in the frozen order `(x15,x23,x35)`. -/
structure Voltage where
  x15 : Bool
  x23 : Bool
  x35 : Bool
deriving DecidableEq

/-- The zero assignment, excluded from the frozen seven-member family. -/
def zeroVoltage : Voltage := ⟨false, false, false⟩

/-- Parities of the five four-cycles, in the frozen order
`0415, 0435, 1234, 1235, 1435`. -/
def cycleParity (v : Voltage) : Fin 5 → Bool
  | 0 => v.x15
  | 1 => v.x35
  | 2 => v.x23
  | 3 => xor (xor v.x15 v.x23) v.x35
  | 4 => xor v.x15 v.x35

/-- A constructive choice of a four-cycle whose parity is even.  If either
singleton form is even, use it; if both are odd, their xor is even. -/
def survivingCycleIndex (v : Voltage) : Fin 5 :=
  if v.x15 = false then 0 else if v.x35 = false then 1 else 4

/-- The selected parity form is always even. -/
theorem survivingCycleIndex_even (v : Voltage) :
    cycleParity v (survivingCycleIndex v) = false := by
  cases v with
  | mk x15 x23 x35 =>
      cases x15 <;> cases x35 <;> rfl

/-- Equivalently, the five listed four-cycle parity forms cannot all be odd. -/
theorem five_cycle_parities_not_all_odd (v : Voltage) :
    ¬∀ i : Fin 5, cycleParity v i = true := by
  intro hall
  have hodd := hall (survivingCycleIndex v)
  rw [survivingCycleIndex_even v] at hodd
  contradiction

/-- Exact enumeration `001,010,011,100,101,110,111` of the frozen nonzero
gauge-fixed voltage triples. -/
def sevenVoltage : Fin 7 → Voltage
  | 0 => ⟨false, false, true⟩
  | 1 => ⟨false, true, false⟩
  | 2 => ⟨false, true, true⟩
  | 3 => ⟨true, false, false⟩
  | 4 => ⟨true, false, true⟩
  | 5 => ⟨true, true, false⟩
  | 6 => ⟨true, true, true⟩

/-- Every member of the frozen seven-member table is nonzero. -/
theorem sevenVoltage_ne_zero (i : Fin 7) :
    sevenVoltage i ≠ zeroVoltage := by
  fin_cases i <;> decide

/-- The frozen table has no duplicate voltage triples. -/
theorem sevenVoltage_injective : Function.Injective sevenVoltage := by
  intro i j hij
  fin_cases i <;> fin_cases j <;> simp_all [sevenVoltage]

/-- The seven entries exhaust all nonzero Bool voltage triples. -/
theorem sevenVoltage_exhaustive (v : Voltage) (hv : v ≠ zeroVoltage) :
    ∃ i : Fin 7, sevenVoltage i = v := by
  rcases v with ⟨x15, x23, x35⟩
  cases x15 <;> cases x23 <;> cases x35
  · exact (hv rfl).elim
  · exact ⟨0, rfl⟩
  · exact ⟨1, rfl⟩
  · exact ⟨2, rfl⟩
  · exact ⟨3, rfl⟩
  · exact ⟨4, rfl⟩
  · exact ⟨5, rfl⟩
  · exact ⟨6, rfl⟩

/-- Each of the seven gauge-fixed assignments leaves a listed base four-cycle
with even voltage. -/
theorem sevenVoltage_has_even_fourCycle (i : Fin 7) :
    ∃ c : Fin 5, cycleParity (sevenVoltage i) c = false := by
  exact ⟨survivingCycleIndex (sevenVoltage i),
    survivingCycleIndex_even (sevenVoltage i)⟩

/-- Table-free form: every nonzero gauge-fixed assignment has the same parity
obstruction. -/
theorem nonzeroVoltage_has_even_fourCycle (v : Voltage)
    (_hv : v ≠ zeroVoltage) :
    ∃ c : Fin 5, cycleParity v c = false := by
  exact ⟨survivingCycleIndex v, survivingCycleIndex_even v⟩

end WrittenOnTheWallII.Wow141K33eTwoLiftParity

#print axioms WrittenOnTheWallII.Wow141K33eTwoLiftParity.five_cycle_parities_not_all_odd
#print axioms WrittenOnTheWallII.Wow141K33eTwoLiftParity.sevenVoltage_exhaustive
#print axioms WrittenOnTheWallII.Wow141K33eTwoLiftParity.sevenVoltage_has_even_fourCycle
