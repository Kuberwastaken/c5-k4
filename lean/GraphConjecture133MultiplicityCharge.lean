import FormalConjecturesUtil

/-!
# WOWII 133: abstract multiplicity charging

The 27 third-layer incidences can collapse through multiplicities one, two,
and three.  This file proves the exact Diophantine restrictions imposed by an
eleven-slot blocker budget.
-/

namespace WrittenOnTheWallII.GraphConjecture133MultiplicityCharge

/-- Aggregate incidence accounting for third vertices of multiplicity
one, two, and three. -/
def MultiplicityAccounting (n₁ n₂ n₃ : ℕ) : Prop :=
  n₁ + 2 * n₂ + 3 * n₃ = 27

/-- If every distinct third vertex needs its own blocker edge and the early
targets provide at most eleven slots, then at least five vertices have
multiplicity three. -/
theorem five_le_multiplicityThree_of_blockerCapacity
    {n₁ n₂ n₃ : ℕ} (hinc : MultiplicityAccounting n₁ n₂ n₃)
    (hcap : n₁ + n₂ + n₃ ≤ 11) :
    5 ≤ n₃ := by
  unfold MultiplicityAccounting at hinc
  omega

/-- The eleven-slot boundary with no multiplicity-one vertices forces six
double and five triple vertices. -/
theorem boundary_without_singletons
    {n₂ n₃ : ℕ} (hinc : MultiplicityAccounting 0 n₂ n₃)
    (hcount : n₂ + n₃ = 11) :
    n₂ = 6 ∧ n₃ = 5 := by
  unfold MultiplicityAccounting at hinc
  omega

/-- The fully collapsed control profile is uniquely nine vertices of
multiplicity three. -/
theorem nine_vertices_force_all_triple
    {n₁ n₂ n₃ : ℕ} (hinc : MultiplicityAccounting n₁ n₂ n₃)
    (hcount : n₁ + n₂ + n₃ = 9) :
    n₁ = 0 ∧ n₂ = 0 ∧ n₃ = 9 := by
  unfold MultiplicityAccounting at hinc
  omega

/-- Exact seven aggregate profiles compatible with 27 incidences and an
eleven-slot blocker capacity. -/
theorem capacity_profile_classification
    {n₁ n₂ n₃ : ℕ} (hinc : MultiplicityAccounting n₁ n₂ n₃)
    (hcap : n₁ + n₂ + n₃ ≤ 11) :
    (n₁ = 0 ∧ n₂ = 0 ∧ n₃ = 9) ∨
    (n₁ = 0 ∧ n₂ = 3 ∧ n₃ = 7) ∨
    (n₁ = 0 ∧ n₂ = 6 ∧ n₃ = 5) ∨
    (n₁ = 1 ∧ n₂ = 1 ∧ n₃ = 8) ∨
    (n₁ = 1 ∧ n₂ = 4 ∧ n₃ = 6) ∨
    (n₁ = 2 ∧ n₂ = 2 ∧ n₃ = 7) ∨
    (n₁ = 3 ∧ n₂ = 0 ∧ n₃ = 8) := by
  unfold MultiplicityAccounting at hinc
  have hn₃ : 5 ≤ n₃ := by omega
  have hn₃' : n₃ ≤ 9 := by omega
  interval_cases n₃ <;> omega

/-- A concrete abstract charge countermodel: nine multiplicity-three vertices
account for all 27 parent incidences while using only nine blocker slots. -/
theorem abstract_charge_countermodel :
    MultiplicityAccounting 0 0 9 ∧ 0 + 0 + 9 ≤ 11 := by
  constructor <;> norm_num [MultiplicityAccounting]

end WrittenOnTheWallII.GraphConjecture133MultiplicityCharge
