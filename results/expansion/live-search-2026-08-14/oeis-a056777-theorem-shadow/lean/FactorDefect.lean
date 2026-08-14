import Mathlib.Data.Nat.Totient
import Mathlib.NumberTheory.ArithmeticFunction.Misc
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

namespace OeisA056777TheoremShadow

open Nat
open scoped ArithmeticFunction.sigma

/-- The signed excess of the divisor sum and Euler totient over twice the input. -/
def factorDefect (n : ℕ) : ℤ :=
  (ArithmeticFunction.sigma 1 n : ℤ) + (Nat.totient n : ℤ) - 2 * (n : ℤ)

/-- The divisor sum at a prime is `p + 1`. -/
lemma sigma_one_prime {p : ℕ} (hp : p.Prime) :
    ArithmeticFunction.sigma 1 p = p + 1 := by
  simpa using
    (ArithmeticFunction.sigma_one_apply_prime_pow (p := p) (i := 1) hp)

/-- The divisor sum at the square of a prime is `1 + p + p²`. -/
lemma sigma_one_prime_sq {p : ℕ} (hp : p.Prime) :
    ArithmeticFunction.sigma 1 (p ^ 2) = 1 + p + p ^ 2 := by
  rw [ArithmeticFunction.sigma_one_apply_prime_pow hp]
  norm_num [Finset.sum_range_succ]

/-- The defect is exactly two at a product of two distinct primes. -/
theorem factorDefect_mul_distinct_primes {p q : ℕ}
    (hp : p.Prime) (hq : q.Prime) (hpq : p ≠ q) :
    factorDefect (p * q) = 2 := by
  have hcop : p.Coprime q := (Nat.coprime_primes hp hq).mpr hpq
  rw [factorDefect,
    ArithmeticFunction.isMultiplicative_sigma.map_mul_of_coprime hcop,
    Nat.totient_mul hcop, sigma_one_prime hp, sigma_one_prime hq,
    Nat.totient_prime hp, Nat.totient_prime hq]
  push_cast [hp.one_lt.le, hq.one_lt.le]
  ring

/-- The defect is exactly one at the square of a prime. -/
theorem factorDefect_prime_sq {p : ℕ} (hp : p.Prime) :
    factorDefect (p ^ 2) = 1 := by
  rw [factorDefect, sigma_one_prime_sq hp,
    Nat.totient_prime_pow hp (by decide : 0 < 2)]
  push_cast [hp.one_lt.le]
  ring

/-- The two defining A056777 translation equalities preserve the defect. -/
theorem factorDefect_add_twelve_eq
    {n : ℕ}
    (hTotient : Nat.totient (n + 12) = Nat.totient n + 12)
    (hSigma : ArithmeticFunction.sigma 1 (n + 12) =
      ArithmeticFunction.sigma 1 n + 12) :
    factorDefect (n + 12) = factorDefect n := by
  unfold factorDefect
  rw [hTotient, hSigma]
  push_cast
  ring

/-- Application-facing packaging of the semiprime result. -/
theorem factorDefect_eq_two_of_exists_distinct_prime_factors {n : ℕ}
    (h : ∃ p q : ℕ, p.Prime ∧ q.Prime ∧ p ≠ q ∧ n = p * q) :
    factorDefect n = 2 := by
  obtain ⟨p, q, hp, hq, hpq, rfl⟩ := h
  exact factorDefect_mul_distinct_primes hp hq hpq

#print axioms factorDefect_mul_distinct_primes
#print axioms factorDefect_prime_sq
#print axioms factorDefect_add_twelve_eq
#print axioms factorDefect_eq_two_of_exists_distinct_prime_factors

end OeisA056777TheoremShadow
