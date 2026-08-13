import FormalConjecturesUtil

/-!
# Erdős 64: the Petersen `Z3` eight-cycle voltage obstruction

For the frozen BFS gauge on Petersen, six cotree voltages determine the total
voltage of each of its fifteen simple eight-cycles.  These fifteen covectors
cover `ZMod 3 ^ 6`: every assignment annihilates at least one of them.

The proof is algebraic rather than an enumeration of the 728 nonzero voltage
rows.  The first six cycle forms are a basis.  If one basis coordinate is zero
we are done; otherwise each belongs to `{1,-1}`.  The other nine cycle forms
block all 64 possible sign patterns.

The graph-cover adapter saying that a zero-voltage simple base eight-cycle
lifts to three simple eight-cycles is intentionally left outside this file.
-/

namespace Erdos64.PetersenZ3EightCycleForms

/-- Cotree coordinates in frozen order `23,27,38,68,69,79`. -/
structure Voltage where
  x23 : ZMod 3
  x27 : ZMod 3
  x38 : ZMod 3
  x68 : ZMod 3
  x69 : ZMod 3
  x79 : ZMod 3

/-- Total oriented voltages of Petersen's fifteen simple eight-cycles, in the
lexicographic cycle order recorded by the exact extraction. -/
def eightCycleVoltage (x : Voltage) : Fin 15 → ZMod 3
  | 0 => x.x23 - x.x79
  | 1 => x.x23 + x.x38 - x.x68 + x.x69
  | 2 => x.x27 - x.x38
  | 3 => x.x27 + x.x68 - x.x69 + x.x79
  | 4 => -x.x23 + x.x27 - x.x38 + x.x68
  | 5 => x.x68 + x.x79
  | 6 => x.x38 + x.x69
  | 7 => x.x23 - x.x27 + x.x69 - x.x79
  | 8 => -x.x23 + x.x68
  | 9 => x.x38 - x.x68 + x.x69 - x.x79
  | 10 => x.x27 - x.x69
  | 11 => x.x23 - x.x27 + x.x38 - x.x79
  | 12 => x.x23 + x.x38 - x.x69 + x.x79
  | 13 => x.x27 + x.x38 - x.x68 + x.x79
  | 14 => x.x23 - x.x27 + x.x68 - x.x69

/-- The same blocking set in coordinates given by its first six independent
forms.  Entries `6`--`14` are their exact linear combinations. -/
def basisCycleVoltage (y0 y1 y2 y3 y4 y5 : ZMod 3) : Fin 15 → ZMod 3
  | 0 => y0
  | 1 => y1
  | 2 => y2
  | 3 => y3
  | 4 => y4
  | 5 => y5
  | 6 => y1 - y2 + y4
  | 7 => y0 - y3 + y5
  | 8 => -y2 + y4
  | 9 => y1 - y2 + y4 - y5
  | 10 => y3 - y5
  | 11 => y0 - y2
  | 12 => y3 - y4
  | 13 => -y0 + y1 + y3 - y5
  | 14 => y0 - y1 - y4 + y5

/-- A nonzero element of `F3` is one of its two signs.  This is the only
three-element classification used in the proof. -/
lemma zmod_three_eq_one_or_neg_one {a : ZMod 3} (ha : a ≠ 0) :
    a = 1 ∨ a = -1 := by
  classical
  fin_cases a
  · exact (ha rfl).elim
  · exact Or.inl rfl
  · apply Or.inr
    apply add_left_cancel (a := (1 : ZMod 3))
    change (1 : ZMod 3) + 2 = 0
    change (3 : ZMod 3) = 0
    exact ZMod.natCast_self 3

/-- The fifteen covectors cover six-dimensional ternary space.  After the
six basis-zero cases, this checks the 64 sign patterns, not the 728 voltage
assignments. -/
theorem basis_forms_cover (y0 y1 y2 y3 y4 y5 : ZMod 3) :
    ∃ i : Fin 15, basisCycleVoltage y0 y1 y2 y3 y4 y5 i = 0 := by
  by_cases h0 : y0 = 0
  · exact ⟨0, h0⟩
  by_cases h1 : y1 = 0
  · exact ⟨1, h1⟩
  by_cases h2 : y2 = 0
  · exact ⟨2, h2⟩
  by_cases h3 : y3 = 0
  · exact ⟨3, h3⟩
  by_cases h4 : y4 = 0
  · exact ⟨4, h4⟩
  by_cases h5 : y5 = 0
  · exact ⟨5, h5⟩
  rcases zmod_three_eq_one_or_neg_one h0 with h0 | h0 <;>
    rcases zmod_three_eq_one_or_neg_one h1 with h1 | h1 <;>
    rcases zmod_three_eq_one_or_neg_one h2 with h2 | h2 <;>
    rcases zmod_three_eq_one_or_neg_one h3 with h3 | h3 <;>
    rcases zmod_three_eq_one_or_neg_one h4 with h4 | h4 <;>
    rcases zmod_three_eq_one_or_neg_one h5 with h5 | h5 <;>
    subst_vars <;>
    first
    | exact ⟨6, by decide⟩
    | exact ⟨7, by decide⟩
    | exact ⟨8, by decide⟩
    | exact ⟨9, by decide⟩
    | exact ⟨10, by decide⟩
    | exact ⟨11, by decide⟩
    | exact ⟨12, by decide⟩

/-- The basis-coordinate table agrees identically with the fifteen Petersen
cycle forms derived from the frozen cotree orientation. -/
theorem basis_coordinates_agree (x : Voltage) (i : Fin 15) :
    basisCycleVoltage
      (eightCycleVoltage x 0) (eightCycleVoltage x 1)
      (eightCycleVoltage x 2) (eightCycleVoltage x 3)
      (eightCycleVoltage x 4) (eightCycleVoltage x 5) i =
        eightCycleVoltage x i := by
  fin_cases i <;> simp [basisCycleVoltage, eightCycleVoltage] <;> ring

/-- Every ternary voltage assignment gives zero total voltage to at least one
simple eight-cycle of the Petersen base.  The statement is stronger than
needed: the all-zero assignment is included. -/
theorem exists_zero_voltage_eightCycle (x : Voltage) :
    ∃ i : Fin 15, eightCycleVoltage x i = 0 := by
  obtain ⟨i, hi⟩ := basis_forms_cover
    (eightCycleVoltage x 0) (eightCycleVoltage x 1)
    (eightCycleVoltage x 2) (eightCycleVoltage x 3)
    (eightCycleVoltage x 4) (eightCycleVoltage x 5)
  exact ⟨i, (basis_coordinates_agree x i) ▸ hi⟩

end Erdos64.PetersenZ3EightCycleForms

#print axioms Erdos64.PetersenZ3EightCycleForms.basis_forms_cover
#print axioms Erdos64.PetersenZ3EightCycleForms.basis_coordinates_agree
#print axioms Erdos64.PetersenZ3EightCycleForms.exists_zero_voltage_eightCycle
