import Mathlib.Data.Nat.Totient
import Mathlib.Data.Nat.Factorization.Induction
import Mathlib.NumberTheory.ArithmeticFunction.Misc
import Mathlib.Tactic.Linarith
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

/-- A coprime-product identity exposing four nonnegative contributions to the defect. -/
lemma factorDefect_mul_of_coprime {a b : ℕ} (h : a.Coprime b) :
    factorDefect (a * b) = (a : ℤ) * factorDefect b + (b : ℤ) * factorDefect a +
      ((ArithmeticFunction.sigma 1 a : ℤ) - a) *
        ((ArithmeticFunction.sigma 1 b : ℤ) - b) +
      ((a : ℤ) - Nat.totient a) * ((b : ℤ) - Nat.totient b) := by
  rw [factorDefect, ArithmeticFunction.isMultiplicative_sigma.map_mul_of_coprime h,
    Nat.totient_mul h]
  simp only [factorDefect]
  push_cast
  ring

/-- On a prime power of exponent at least two, the defect is a truncated geometric sum. -/
lemma factorDefect_prime_pow_succ_succ {p k : ℕ} (hp : p.Prime) :
    factorDefect (p ^ (k + 2)) =
      (∑ j ∈ Finset.range (k + 1), (p : ℤ) ^ j) := by
  rw [factorDefect, ArithmeticFunction.sigma_one_apply_prime_pow hp,
    Nat.totient_prime_pow hp (by positivity)]
  rw [show k + 2 - 1 = k + 1 by simp]
  rw [Finset.sum_range_succ, Finset.sum_range_succ]
  push_cast [hp.one_lt.le]
  rw [pow_succ, pow_succ]
  ring

lemma sigma_one_sub_self_eq_sum_properDivisors (n : ℕ) :
    (ArithmeticFunction.sigma 1 n : ℤ) - n =
      (n.properDivisors.sum id : ℕ) := by
  rw [ArithmeticFunction.sigma_one_apply,
    Nat.sum_divisors_eq_sum_properDivisors_add_self]
  push_cast
  simp

lemma one_le_sigma_one_sub_self {n : ℕ} (hn : 1 < n) :
    (1 : ℤ) ≤ (ArithmeticFunction.sigma 1 n : ℤ) - n := by
  rw [sigma_one_sub_self_eq_sum_properDivisors]
  have hone : ({1} : Finset ℕ) ⊆ n.properDivisors := by
    simpa using Nat.one_mem_properDivisors_iff_one_lt.2 hn
  have hnat : 1 ≤ n.properDivisors.sum id := by
    calc
      1 = ({1} : Finset ℕ).sum id := by simp
      _ ≤ n.properDivisors.sum id := Finset.sum_le_sum_of_subset hone
  exact_mod_cast hnat

lemma sigma_one_sub_self_eq_one_iff_prime {n : ℕ} (_hn : 1 < n) :
    (ArithmeticFunction.sigma 1 n : ℤ) - n = 1 ↔ n.Prime := by
  rw [sigma_one_sub_self_eq_sum_properDivisors]
  exact_mod_cast Nat.sum_properDivisors_eq_one_iff_prime

lemma one_le_self_sub_totient {n : ℕ} (hn : 1 < n) :
    (1 : ℤ) ≤ (n : ℤ) - Nat.totient n := by
  have h := Nat.totient_lt n hn
  have hcast : ((Nat.totient n + 1 : ℕ) : ℤ) ≤ n := by
    exact_mod_cast Nat.succ_le_iff.2 h
  push_cast at hcast
  linarith

lemma self_sub_totient_eq_one_iff_prime {n : ℕ} (hn : 1 < n) :
    (n : ℤ) - Nat.totient n = 1 ↔ n.Prime := by
  constructor
  · intro h
    apply (Nat.totient_eq_iff_prime (by positivity)).mp
    have hn1 : 1 ≤ n := hn.le
    push_cast at h
    have heq : (Nat.totient n : ℤ) = (n : ℤ) - 1 := by linarith
    apply Nat.cast_injective (R := ℤ)
    rw [Nat.cast_sub hn1]
    exact heq
  · intro hp
    rw [Nat.totient_prime hp]
    push_cast [hp.one_lt.le]
    ring

lemma three_le_factorDefect_prime_pow_succ_succ_succ {p k : ℕ} (hp : p.Prime) :
    (3 : ℤ) ≤ factorDefect (p ^ (k + 3)) := by
  rw [show k + 3 = (k + 1) + 2 by simp]
  rw [factorDefect_prime_pow_succ_succ hp]
  have htail : (0 : ℤ) ≤ ∑ j ∈ Finset.range k, (p : ℤ) ^ (2 + j) := by
    exact Finset.sum_nonneg fun _ _ ↦ pow_nonneg (by positivity) _
  rw [show k + 2 = 2 + k by simp [Nat.add_comm]]
  rw [Finset.sum_range_add]
  norm_num
  have hp2 : (2 : ℤ) ≤ p := by exact_mod_cast hp.two_le
  linarith

/-- The complete small-defect classification, proved by prime-power/coprime induction. -/
theorem factorDefect_small_classification (n : ℕ) :
    0 ≤ factorDefect n ∧
      (factorDefect n = 1 → ∃ p : ℕ, p.Prime ∧ n = p ^ 2) ∧
      (factorDefect n = 2 →
        ∃ p q : ℕ, p.Prime ∧ q.Prime ∧ p ≠ q ∧ n = p * q) := by
  induction n using Nat.recOnPosPrimePosCoprime with
  | prime_pow p k hp hk =>
      rcases k with _ | k
      · simp at hk
      rcases k with _ | k
      · simp only [Nat.zero_add, pow_one]
        change 0 ≤ factorDefect p ∧
          (factorDefect p = 1 → ∃ q : ℕ, q.Prime ∧ p = q ^ 2) ∧
          (factorDefect p = 2 →
            ∃ q r : ℕ, q.Prime ∧ r.Prime ∧ q ≠ r ∧ p = q * r)
        have hD : factorDefect p = 0 := by
          rw [factorDefect, sigma_one_prime hp, Nat.totient_prime hp]
          push_cast [hp.one_lt.le]
          ring
        simp [hD]
      rcases k with _ | k
      · change 0 ≤ factorDefect (p ^ 2) ∧
          (factorDefect (p ^ 2) = 1 → ∃ q : ℕ, q.Prime ∧ p ^ 2 = q ^ 2) ∧
          (factorDefect (p ^ 2) = 2 →
            ∃ q r : ℕ, q.Prime ∧ r.Prime ∧ q ≠ r ∧ p ^ 2 = q * r)
        have hD : factorDefect (p ^ 2) = 1 := factorDefect_prime_sq hp
        constructor
        · linarith
        constructor
        · intro _
          exact ⟨p, hp, rfl⟩
        · intro h
          linarith
      · have h3 := three_le_factorDefect_prime_pow_succ_succ_succ (k := k) hp
        constructor
        · linarith
        constructor <;> intro h <;> linarith
  | zero => norm_num [factorDefect]
  | one => norm_num [factorDefect]
  | coprime a b ha hb hab iha ihb =>
      let A : ℕ → ℤ := fun m ↦ (ArithmeticFunction.sigma 1 m : ℤ) - m
      let B : ℕ → ℤ := fun m ↦ (m : ℤ) - Nat.totient m
      have hDa : 0 ≤ factorDefect a := iha.1
      have hDb : 0 ≤ factorDefect b := ihb.1
      have hAa : 1 ≤ A a := one_le_sigma_one_sub_self ha
      have hAb : 1 ≤ A b := one_le_sigma_one_sub_self hb
      have hBa : 1 ≤ B a := one_le_self_sub_totient ha
      have hBb : 1 ≤ B b := one_le_self_sub_totient hb
      have hmul : factorDefect (a * b) =
          (a : ℤ) * factorDefect b + (b : ℤ) * factorDefect a +
            A a * A b + B a * B b := factorDefect_mul_of_coprime hab
      have ha2 : (2 : ℤ) ≤ a := by exact_mod_cast ha
      have hb2 : (2 : ℤ) ≤ b := by exact_mod_cast hb
      constructor
      · rw [hmul]
        positivity
      constructor
      · intro h
        rw [hmul] at h
        nlinarith [mul_le_mul hAa hAb (by linarith) (by linarith),
          mul_le_mul hBa hBb (by linarith) (by linarith)]
      · intro h
        rw [hmul] at h
        have hAA : A a * A b ≥ 1 := by nlinarith
        have hBB : B a * B b ≥ 1 := by nlinarith
        have hAa1 : A a = 1 := by nlinarith
        have hAb1 : A b = 1 := by nlinarith
        have hpa : a.Prime := (sigma_one_sub_self_eq_one_iff_prime ha).mp hAa1
        have hpb : b.Prime := (sigma_one_sub_self_eq_one_iff_prime hb).mp hAb1
        exact ⟨a, b, hpa, hpb, (Nat.coprime_primes hpa hpb).mp hab, rfl⟩

/-- Defect one occurs only at the square of a prime. -/
theorem exists_prime_sq_of_factorDefect_eq_one {n : ℕ} (_hn : 1 < n)
    (h : factorDefect n = 1) :
    ∃ p : ℕ, p.Prime ∧ n = p ^ 2 :=
  (factorDefect_small_classification n).2.1 h

/-- Defect two occurs only at a product of two distinct primes. -/
theorem exists_distinct_primes_of_factorDefect_eq_two {n : ℕ} (_hn : 1 < n)
    (h : factorDefect n = 2) :
    ∃ p q : ℕ, p.Prime ∧ q.Prime ∧ p ≠ q ∧ n = p * q :=
  (factorDefect_small_classification n).2.2 h

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
#print axioms factorDefect_mul_of_coprime
#print axioms factorDefect_prime_pow_succ_succ
#print axioms factorDefect_small_classification
#print axioms exists_prime_sq_of_factorDefect_eq_one
#print axioms exists_distinct_primes_of_factorDefect_eq_two
#print axioms factorDefect_add_twelve_eq
#print axioms factorDefect_eq_two_of_exists_distinct_prime_factors

end OeisA056777TheoremShadow
