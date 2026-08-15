# OEIS open-declaration counterexample hunt — Part 2 (ids >= 130000)

**Date:** 2026-08-15 UTC
**Corpus:** `google-deepmind/formal-conjectures`, pinned commit `2411d22e1bd550d050d0eac6c1fb379a76a3e7c5`
(`upstream/main`, 2026-08-14 19:16:38 +0000), read via `git show upstream/main:<path>`.
**Target list:** `results/expansion/open_targets_oeis_erdos_20260815.json`, `corpus == "OEIS"`,
ids sorted ascending, second half (`id >= 130000`).
**Skipped:** A231201 (`previously_touched == true`).
**Method gates:** `METHOD.md` v1.0 — Phase 0A certificate shape, Phase 0B provenance freeze,
Phase 7 candidate verification. 60-second hard cap on every computation.
**Publication:** none. No upstream issue/PR/comment opened. Local records only.

## Running summary

| # | OEIS | Lean file | open decls | certificate shape | verdict | refuting integer |
|---|---|---|---|---|---|---|
| 1 | A167604 | `FormalConjectures/OEIS/167604.lean` | 1 (`answer(sorry)`) | fixed-answer placeholder | `CERTIFICATE_SHAPE_FAIL` (NOT_FINITELY_REFUTABLE) | — |

_(table extended after each target)_

---

## 1. A167604 — Chua / Euclid–Mullin variant

**Lean file:** `FormalConjectures/OEIS/167604.lean` (2243 bytes, 1 `answer(sorry)`, 1 `category research open`).
**OEIS:** <https://oeis.org/A167604>

### Verbatim open declaration

```lean
/-- Does Chua's sequence contain every prime? -/
@[category research open, AMS 11]
theorem conjecture :
    answer(sorry) ↔ ∀ p : ℕ, p.Prime → ∃ n ≥ 1, a n = p := by
  sorry
```

with

```lean
def next (n : ℕ) : ℕ := Nat.minFac (∏ d ∈ n.divisors, (d + n / d))
def product : ℕ → ℕ | 0 => 1 | n + 1 => product n * next (product n)
def a : ℕ → ℕ | 0 => 1 | n + 1 => next (product n)
```

### OEIS ground truth

- NAME: "A variant of Euclid-Mullin (A000945): a(1)=2, a(n+1) is the least prime dividing
  [Product_{i in I} a(i) + Product_{i in I'} a(i)], minimized over all subsets I of {1..n}."
- OFFSET: 1,1
- DATA (first 14): `2, 3, 5, 11, 37, 13, 7, 29, 17, 19, 43, 23, 47, 41`
- COMMENT: "By Euclid's argument, the terms are distinct." / "One can ask whether all primes occur
  in this sequence."
- MAPLE program in the entry uses exactly the divisor form
  `p:=proc(N) ... for d in divisors(N) while d^2<=N do S:=S, divisors(d+N/d)[2] od : return(min(S))`.

### Faithfulness check (Phase 0B)

Subset-product form and divisor form agree because the terms are distinct primes, so the total
product is squarefree and its divisors are exactly the subset products; the OEIS entry's own Maple
code uses the divisor form. `Nat.minFac (∏ (d + n/d)) = min_d Nat.minFac (d + n/d)` because every
factor is `>= 2`.

Independent recomputation (subset enumeration over the distinct primes, not the divisor helper):

```
Lean-a(1..14): [2, 3, 5, 11, 37, 13, 7, 29, 17, 19, 43, 23, 47, 41]
OEIS a(1..14): [2, 3, 5, 11, 37, 13, 7, 29, 17, 19, 43, 23, 47, 41]
MATCH: True
```

The Lean `a` is faithful to A167604 (with the harmless extension `a 0 = 1`; Lean `a n` = OEIS `a(n)`
for `n >= 1`).

### Certificate shape (METHOD G0 / Phase 0A)

`answer(sorry) ↔ P` is the fixed-answer class. Its literal negation is not a finite object, and the
right-hand side `∀ p prime, ∃ n >= 1, a n = p` is a `∀∃` statement over an unbounded sequence: a
finite artifact can witness membership of finitely many primes but can never refute the universal.
No finite integer can settle it.

### Verdict

`CERTIFICATE_SHAPE_FAIL` / **NOT_FINITELY_REFUTABLE**. No formalization defect found; the Lean
definition reproduces the OEIS DATA exactly. Not carried further.
