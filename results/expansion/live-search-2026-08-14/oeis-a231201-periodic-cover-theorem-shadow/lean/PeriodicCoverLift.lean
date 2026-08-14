import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.Ring

/-!
# A231201 periodic-cover lift core

This file formalizes the generic finite-fiber fact used by the periodic-cover
theorem shadow.  If a fiber has the form `r + k * step` modulo `q`, and `step`
is nonzero modulo `q`, then a single forbidden value of `x - b` cannot exclude
the entire fiber.  In fact, the proof only needs the two indices `0` and `1`.

The second theorem packages the result for the natural-number lifts
`r + k * (d * M)`: the selected lift remains congruent to `r` modulo `M`.
-/

namespace OeisA231201

/-- An affine fiber in `ZMod q` with nonzero step contains a point avoiding
any one forbidden residue.  The hypothesis `2 ≤ q` supplies distinct indices
`0, 1 : Fin q`; primality is not needed for this core statement. -/
theorem exists_fin_affine_avoiding
    {q : ℕ} [NeZero q] (hq : 2 ≤ q)
    (r step power forbidden : ZMod q) (hstep : step ≠ 0) :
    ∃ k : Fin q, r + (k.val : ZMod q) * step - power ≠ forbidden := by
  let k0 : Fin q := ⟨0, lt_of_lt_of_le (by decide : 0 < 2) hq⟩
  let k1 : Fin q := ⟨1, hq⟩
  by_cases h0 : r - power ≠ forbidden
  · refine ⟨k0, ?_⟩
    simpa [k0] using h0
  · have h0eq : r - power = forbidden := by
      simpa only [ne_eq, not_not] using h0
    refine ⟨k1, ?_⟩
    simp only [k1, Nat.cast_one, one_mul]
    intro h1eq
    apply hstep
    calc
      step = (r + step - power) - (r - power) := by ring
      _ = forbidden - forbidden := by rw [h1eq, h0eq]
      _ = 0 := sub_self forbidden

/-- A natural-number lift chosen in one `q`-fiber both preserves the old
congruence modulo `M` and avoids one forbidden value modulo `q`.

In the periodic-cover application `step = d * M`, while `power` is the common
value of `2^x` on the exponent fiber.  The arithmetic-order argument proving
that common-power premise is deliberately independent of this finite-fiber
selection lemma. -/
theorem exists_natural_lift_avoiding
    {q M d r : ℕ} [NeZero q] (hq : 2 ≤ q)
    (power forbidden : ZMod q) (hstep : (d * M : ZMod q) ≠ 0) :
    ∃ k : Fin q,
      (r + k.val * (d * M)) % M = r % M ∧
        ((r + k.val * (d * M) : ℕ) : ZMod q) - power ≠ forbidden := by
  obtain ⟨k, hk⟩ := exists_fin_affine_avoiding hq (r : ZMod q)
    (d * M : ZMod q) power forbidden hstep
  refine ⟨k, ?_, ?_⟩
  · rw [← Nat.mul_assoc]
    rw [Nat.mul_comm (k.val * d) M]
    exact Nat.add_mul_mod_self_left r M (k.val * d)
  · simpa [Nat.cast_add, Nat.cast_mul] using hk

/-- Odd primes meet the cardinality hypothesis of the fiber lemma.  This is
the application-facing form: `q` is prime and odd, and `d*M` is invertible
modulo `q` (expressed minimally as nonzero). -/
theorem odd_prime_fiber_has_allowed_lift
    {q M d r : ℕ} (hqPrime : q.Prime) (_hqOdd : Odd q)
    (power forbidden : ZMod q) (hstep : (d * M : ZMod q) ≠ 0) :
    ∃ k : Fin q,
      (r + k.val * (d * M)) % M = r % M ∧
        ((r + k.val * (d * M) : ℕ) : ZMod q) - power ≠ forbidden := by
  letI : NeZero q := ⟨hqPrime.ne_zero⟩
  apply exists_natural_lift_avoiding (q := q) (M := M) (d := d) (r := r)
    hqPrime.two_le
    power forbidden hstep

/-- Finite-list existence induction for an abstract lift operation.

`holds state constraint` says that a state avoids one constraint.  If lifting
can satisfy the newly added constraint while preserving every old one, then
every finite list of constraints has a simultaneous witness.  Instantiating
`lift` with the selected modular fiber lift turns the one-prime lemma above
into the finite-prime induction used by the theorem shadow. -/
theorem finite_list_avoiding_of_extension
    {State Constraint : Type*}
    (holds : State → Constraint → Prop) (seed : State)
    (lift : State → Constraint → State)
    (new_constraint : ∀ state constraint,
      holds (lift state constraint) constraint)
    (preserves_old : ∀ state new old,
      holds state old → holds (lift state new) old) :
    ∀ constraints : List Constraint,
      ∃ state, ∀ constraint ∈ constraints, holds state constraint := by
  intro constraints
  induction constraints with
  | nil =>
      exact ⟨seed, by simp⟩
  | cons new rest ih =>
      obtain ⟨state, hstate⟩ := ih
      refine ⟨lift state new, ?_⟩
      intro constraint hconstraint
      simp only [List.mem_cons] at hconstraint
      rcases hconstraint with rfl | hrest
      · exact new_constraint _ _
      · exact preserves_old state new constraint (hstate constraint hrest)

#print axioms exists_fin_affine_avoiding
#print axioms exists_natural_lift_avoiding
#print axioms odd_prime_fiber_has_allowed_lift
#print axioms finite_list_avoiding_of_extension

end OeisA231201
