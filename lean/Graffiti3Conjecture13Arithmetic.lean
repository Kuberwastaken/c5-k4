import Mathlib.Data.Nat.Totient
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.NormNum.GCD
import Mathlib.Tactic.NormNum.Prime
import Mathlib.Tactic.ReduceModChar

/-!
# Graffiti³ Conjecture 13: arithmetic counterexample certificate

Graffiti³ Conjecture 13 asks, for base two, whether

`19 * Nat.totient n <= 9 * n`

implies that `n` is not a Fermat pseudoprime.  This standalone Mathlib module
certifies the finite arithmetic witness `n = 81,722,145` without importing or
claiming any declaration from `google-deepmind/formal-conjectures`.

The search establishes separately that this is the smallest hit in its frozen
enumeration.  Minimality is not asserted here: this file certifies only the
displayed witness, including its complete squarefree factorization,
compositeness, exact totient, base-two Fermat residue, and strict ratio margin.
-/

namespace Graffiti3.Conjecture13

/-- The finite counterexample candidate. -/
def witness : ℕ := 81722145

/-- The complete product reconstruction recorded by the search certificate. -/
theorem witness_factorization :
    witness = 3 * (5 * (17 * (29 * (43 * 257)))) := by
  norm_num [witness]

/-- Every factor in the displayed reconstruction is prime. -/
theorem witness_factor_primality :
    Nat.Prime 3 ∧ Nat.Prime 5 ∧ Nat.Prime 17 ∧ Nat.Prime 29 ∧
      Nat.Prime 43 ∧ Nat.Prime 257 := by
  norm_num

/-- The proper divisor three certifies compositeness without asking a
primality decision procedure to factor the full eight-digit number. -/
theorem witness_not_prime : ¬Nat.Prime witness := by
  apply Nat.not_prime_of_dvd_of_lt (m := 3)
  · norm_num [witness]
  · norm_num
  · norm_num [witness]

/-- Exact Euler-totient reconstruction from the six pairwise coprime prime
factors. -/
theorem witness_totient : Nat.totient witness = 38535168 := by
  rw [witness_factorization]
  rw [Nat.totient_mul
    (by norm_num : Nat.Coprime 3 (5 * (17 * (29 * (43 * 257)))))]
  rw [Nat.totient_mul
    (by norm_num : Nat.Coprime 5 (17 * (29 * (43 * 257))))]
  rw [Nat.totient_mul
    (by norm_num : Nat.Coprime 17 (29 * (43 * 257)))]
  rw [Nat.totient_mul
    (by norm_num : Nat.Coprime 29 (43 * 257))]
  rw [Nat.totient_mul (by norm_num : Nat.Coprime 43 257)]
  rw [Nat.totient_prime (by norm_num : Nat.Prime 3)]
  rw [Nat.totient_prime (by norm_num : Nat.Prime 5)]
  rw [Nat.totient_prime (by norm_num : Nat.Prime 17)]
  rw [Nat.totient_prime (by norm_num : Nat.Prime 29)]
  rw [Nat.totient_prime (by norm_num : Nat.Prime 43)]
  rw [Nat.totient_prime (by norm_num : Nat.Prime 257)]

/-- Fast, proof-producing modular exponentiation in `ZMod witness`.  The
`reduce_mod_char` tactic uses repeated squaring and does not construct the
astronomical natural number `2 ^ 81722144`. -/
theorem witness_base_two_zmod :
    ((2 : ZMod 81722145) ^ 81722144) = 1 := by
  reduce_mod_char

/-- The exact base-two Fermat residue in the source's natural-number form. -/
theorem witness_base_two_residue :
    2 ^ (witness - 1) % witness = 1 := by
  have hcast :
      ((2 ^ (witness - 1) : ℕ) : ZMod witness) = (1 : ZMod witness) := by
    simpa only [witness, Nat.cast_pow, Nat.cast_ofNat, Nat.cast_one] using
      witness_base_two_zmod
  have hmod : 2 ^ (witness - 1) ≡ 1 [MOD witness] :=
    (ZMod.natCast_eq_natCast_iff _ _ _).mp hcast
  exact Nat.mod_eq_of_modEq hmod (by norm_num [witness])

/-- The ratio premise holds with exact positive margin `3,331,113`. -/
theorem witness_ratio_margin :
    9 * witness = 19 * Nat.totient witness + 3331113 := by
  rw [witness_totient]
  norm_num [witness]

/-- Source-normalized non-strict ratio premise. -/
theorem witness_ratio_inequality :
    19 * Nat.totient witness ≤ 9 * witness := by
  rw [witness_totient]
  norm_num [witness]

/-- The base-two Fermat-pseudoprime predicate needed for the finite logical
wrapper. -/
def IsBaseTwoFermatPseudoprime (n : ℕ) : Prop :=
  ¬Nat.Prime n ∧ 2 ^ (n - 1) % n = 1

/-- The arithmetic data certify that the witness is a base-two Fermat
pseudoprime. -/
theorem witness_is_base_two_fermat_pseudoprime :
    IsBaseTwoFermatPseudoprime witness := by
  exact ⟨witness_not_prime, witness_base_two_residue⟩

/-- The source-normalized implication fails at the displayed witness. -/
theorem conjecture13_implication_fails_at_witness :
    ¬(19 * Nat.totient witness ≤ 9 * witness →
      ¬IsBaseTwoFermatPseudoprime witness) := by
  intro h
  exact h witness_ratio_inequality witness_is_base_two_fermat_pseudoprime

end Graffiti3.Conjecture13
