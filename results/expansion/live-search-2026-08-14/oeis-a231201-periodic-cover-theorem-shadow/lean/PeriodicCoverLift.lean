import Mathlib.Data.ZMod.Basic
import Mathlib.FieldTheory.Finite.Basic
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

/-- The quotient by the gcd supplies exactly the missing factor needed to
make the shift a multiple of the multiplicative order. -/
theorem order_dvd_quotient_gcd_mul (M order : ℕ) :
    order ∣ (order / M.gcd order) * M := by
  let g := M.gcd order
  change order ∣ (order / g) * M
  have hgM : g ∣ M := Nat.gcd_dvd_left M order
  have hgOrder : g ∣ order := Nat.gcd_dvd_right M order
  obtain ⟨c, hc⟩ := hgM
  refine ⟨c, ?_⟩
  calc
    (order / g) * M = (order / g) * (g * c) := by rw [hc]
    _ = ((order / g) * g) * c := by
      rw [Nat.mul_assoc]
    _ = order * c := by rw [Nat.div_mul_cancel hgOrder]

/-- Shifting an exponent by any multiple of
`(orderOf 2 / gcd M (orderOf 2)) * M` preserves its power of two modulo `q`. -/
theorem pow_two_add_order_gcd_shift
    {q : ℕ} [NeZero q] (M r k : ℕ) :
    let order := orderOf (2 : ZMod q)
    let d := order / M.gcd order
    (2 : ZMod q) ^ (r + k * (d * M)) = (2 : ZMod q) ^ r := by
  dsimp only
  rw [pow_add]
  have horder : orderOf (2 : ZMod q) ∣
      k * ((orderOf (2 : ZMod q) / M.gcd (orderOf (2 : ZMod q))) * M) := by
    obtain ⟨c, hc⟩ := order_dvd_quotient_gcd_mul M (orderOf (2 : ZMod q))
    refine ⟨k * c, ?_⟩
    rw [hc]
    ac_rfl
  rw [orderOf_dvd_iff_pow_eq_one.mp horder, mul_one]

/-- For a fresh prime `q > 2`, the order/gcd step is nonzero, and indeed a
unit, modulo `q`.  Freshness is exactly the condition `q ∤ M`. -/
theorem order_gcd_step_nonzero_and_isUnit
    {q M : ℕ} (hqPrime : q.Prime) (hqTwo : 2 < q) (hFresh : ¬q ∣ M) :
    let order : ℕ := orderOf (2 : ZMod q)
    let d : ℕ := order / M.gcd order
    ((d * M : ℕ) : ZMod q) ≠ 0 ∧ IsUnit (((d * M : ℕ) : ZMod q)) := by
  letI : NeZero q := ⟨hqPrime.ne_zero⟩
  letI : Fact q.Prime := ⟨hqPrime⟩
  dsimp only
  have htwo : (2 : ZMod q) ≠ 0 := by
    intro htwoZero
    have hqDvdTwo : q ∣ 2 :=
      (ZMod.natCast_eq_zero_iff 2 q).mp htwoZero
    exact (Nat.not_le_of_lt hqTwo) (Nat.le_of_dvd (by decide) hqDvdTwo)
  have horderDvd : orderOf (2 : ZMod q) ∣ q - 1 :=
    ZMod.orderOf_dvd_card_sub_one htwo
  have hqSubPos : 0 < q - 1 :=
    Nat.sub_pos_of_lt (lt_trans Nat.one_lt_two hqTwo)
  have horderPos : 0 < orderOf (2 : ZMod q) :=
    Nat.pos_of_dvd_of_pos horderDvd hqSubPos
  have horderLt : orderOf (2 : ZMod q) < q :=
    lt_of_le_of_lt (Nat.le_of_dvd hqSubPos horderDvd)
      (Nat.sub_lt hqPrime.pos Nat.zero_lt_one)
  have hgcdPos : 0 < M.gcd (orderOf (2 : ZMod q)) :=
    Nat.gcd_pos_of_pos_right M horderPos
  have hdPos : 0 < orderOf (2 : ZMod q) / M.gcd (orderOf (2 : ZMod q)) :=
    Nat.div_pos (Nat.gcd_le_right M horderPos) hgcdPos
  have hdLt : orderOf (2 : ZMod q) / M.gcd (orderOf (2 : ZMod q)) < q :=
    lt_of_le_of_lt (Nat.div_le_self _ _) horderLt
  have hqNotDvdD : ¬q ∣ orderOf (2 : ZMod q) / M.gcd (orderOf (2 : ZMod q)) :=
    Nat.not_dvd_of_pos_of_lt hdPos hdLt
  have hqNotDvdStep :
      ¬q ∣ (orderOf (2 : ZMod q) / M.gcd (orderOf (2 : ZMod q))) * M :=
    hqPrime.not_dvd_mul hqNotDvdD hFresh
  have hstep :
      (((orderOf (2 : ZMod q) / M.gcd (orderOf (2 : ZMod q))) * M : ℕ) :
        ZMod q) ≠ 0 := by
    rw [ne_eq, ZMod.natCast_eq_zero_iff]
    exact hqNotDvdStep
  exact ⟨hstep, isUnit_iff_ne_zero.mpr hstep⟩

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

/-- The complete one-prime arithmetic bridge used by the periodic-cover
induction.  For a fresh prime `q > 2`, set
`d = orderOf(2) / gcd M (orderOf(2))`.  Some lift in the canonical `q`-fiber
preserves the old residue modulo `M`, has the same power of two as `r`, and
avoids the assigned residue for the actual expression `x - 2^x`.  The fiber
step is additionally certified to be a unit modulo `q`. -/
theorem fresh_prime_order_fiber_has_allowed_lift
    {q M r : ℕ} (hqPrime : q.Prime) (hqTwo : 2 < q) (hFresh : ¬q ∣ M)
    (forbidden : ZMod q) :
    let order : ℕ := orderOf (2 : ZMod q)
    let d : ℕ := order / M.gcd order
    ∃ k : Fin q,
      (r + k.val * (d * M)) % M = r % M ∧
      (2 : ZMod q) ^ (r + k.val * (d * M)) = (2 : ZMod q) ^ r ∧
      (((r + k.val * (d * M) : ℕ) : ZMod q) -
        (2 : ZMod q) ^ (r + k.val * (d * M)) ≠ forbidden) ∧
      IsUnit (((d * M : ℕ) : ZMod q)) := by
  letI : NeZero q := ⟨hqPrime.ne_zero⟩
  have hstep := order_gcd_step_nonzero_and_isUnit hqPrime hqTwo hFresh
  dsimp only at hstep ⊢
  obtain ⟨k, hmod, havoid⟩ := exists_natural_lift_avoiding
    (q := q) (M := M)
    (d := orderOf (2 : ZMod q) / M.gcd (orderOf (2 : ZMod q))) (r := r)
    hqPrime.two_le ((2 : ZMod q) ^ r) forbidden (by
      simpa only [Nat.cast_mul] using hstep.1)
  have hpow := pow_two_add_order_gcd_shift (q := q) M r k.val
  dsimp only at hpow
  refine ⟨k, hmod, hpow, ?_, hstep.2⟩
  rw [hpow]
  exact havoid

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
#print axioms order_dvd_quotient_gcd_mul
#print axioms pow_two_add_order_gcd_shift
#print axioms order_gcd_step_nonzero_and_isUnit
#print axioms exists_natural_lift_avoiding
#print axioms odd_prime_fiber_has_allowed_lift
#print axioms fresh_prime_order_fiber_has_allowed_lift
#print axioms finite_list_avoiding_of_extension

end OeisA231201
