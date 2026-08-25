# A107247 — REPAIR CANDIDATE (round-2 opportunity developed)

**Class: COMPLETE FORMALIZATION-REPAIR CANDIDATE (textbook-sorry closable).
Gates: a ✓, b ✓, c ✓ (third independent path), d ✓ (no competing fix found).**

## Target

`known_prime_and_semiprimes` in `FormalConjectures/OEIS/A107247.lean`
@ `2411d22e`, category `textbook`, body `sorry`:

```
(a 8).Prime ∧ (a 9).IsSemiprime ∧ ... ∧ (a 27).IsSemiprime   -- 9 conjuncts
```

## Verification (all 9 conjuncts, third code path)

Round 2 verified twice (sympy factorint; pure-Python trial division). This
round adds a structurally different path: iterative sliding-window nonacci
generation + smallest-factor trial-division certification
(`scripts/a107247_third_path.py`, log `a107247_run3.log`):

| Lean index | value | certification |
|---|---|---|
| a(8) = 2 | prime | — |
| a(9) = 6 | 2 · 3 | both prime |
| a(10) = 22 | 2 · 11 | both prime |
| a(11) = 86 | 2 · 43 | both prime |
| a(13) = 1366 | 2 · 683 | both prime |
| a(14) = 5462 | 2 · 2731 | both prime |
| a(16) = 87382 | 2 · 43691 | both prime |
| a(17) = 348503 | 37 · 9419 | both prime |
| a(27) = 358201316657 | 71 · 5045088967 | both prime |

**All nine conjuncts verify. No crossing against the textbook claim.**

## Mathlib API for the proof

Mathlib.NumberTheory.AlmostPrime defines `Nat.IsAlmostPrime k n : n ≠ 0 ∧ Ω n = k`
and `abbrev IsSemiprime n := IsAlmostPrime 2 n`, with

```
theorem Nat.Prime.mul_isAlmostPrime_two (hp : p.Prime) (hq : q.Prime) :
    IsAlmostPrime 2 (p * q)
```

## Proof sketch (repair text)

```lean
private lemma prime2 : (2 : ℕ).Prime := by decide
private lemma prime37 : (37 : ℕ).Prime := by decide
private lemma prime71 : (71 : ℕ).Prime := by decide
-- 683, 2731, 43691, 9419: one-line primality certificates
--   (Nat.prime_def_lt' + explicit non-divisibility by primes ≤ √n),
--   or decide if kernel budget allows.
private lemma prime5045088967 : (5045088967 : ℕ).Prime := by
  -- √n < 71,008; certificate list of trial divisors, or native_decide.

theorem known_prime_and_semiprimes : ... := by
  refine ⟨by decide, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · -- a 9 = 6:
    have h : a 9 = 6 := by norm_num [a, nonacci]   -- equation-lemma unfolding
    rw [h]; exact Nat.Prime.mul_isAlmostPrime_two prime2 (by decide)
  · ... -- identical shape for the remaining seven semiprime conjuncts
```

Note on evaluation: `nonacci`/`a` compile via well-founded recursion, so
`decide` alone may not reduce a(27); use the generated equation lemmas
(`simp only [a, nonacci]`) to reach numerals, then `norm_num`. The largest
primality obligation is 5045088967 (< 2^33): recommend an explicit
trial-division certificate rather than bare `decide`.

## Status

Repair candidate complete (witnesses + tactic plan). Not filed upstream from
this agent; handed to campaign maintainers per protocol. The research-open
conjecture (next prime) remains open; round-2 bracket n ≤ 699 stands.
