# Wave 3: answer-wrapped finite-certificate search

Date: 2026-08-14 UTC. Frozen source:
`google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.

## Terminal outcome

Three fresh `answer(sorry) ↔ RHS` declarations whose right-hand sides admit
finite positive certificates passed the selection, status, and source gates.
All nine discovery arms were separately run under the same hard 60-second
wall-clock cap and exited normally. No certificate crossing was found.

The outcome is therefore **three bounded zeroes**, not three negative answers:
none of these existential right-hand sides has a finite nonexistence
certificate. Conversely, had a witness appeared, it would have determined the
intended answer as positive; it would not by itself have been a refutation of
the opaque biconditional containing `answer(sorry)`.

## Freshness and status gate

An exact scan of all 18 pre-existing
`results/expansion/live-search-2026-08-14/*.md` files found no occurrence of
`Erdos850`, `erdos_850`, `AlmostPerfectNumbers`, `AlmostPerfect`,
`BetrothedNumbers`, or `same_parity_betrothed`. The three selected files are
present at the pin and are tagged `@[category research open]`.

| declaration | pinned blob | file SHA-256 | finite certificate shape |
|---|---|---|---|
| `Erdos850.erdos_850` | `23052cee4106a9d6c58475230d41c9632294fc1f` | `5128fc19d679a8b7f31c9a894c997a66173138192840531b763c4f3df8f06eaa` | two explicit naturals `x ≠ y` and three decidable prime-support equalities |
| `AlmostPerfectNumbers.exists_almost_perfect_not_power_of_two` | `386be0ef02f579bcb56735e98a62c894f4934a69` | `000c6f8df556e3372802fc7497094be21c35ee903a85fb90fab9b7408da9bb4d` | one explicit `n`, an exact divisor sum, and a finite power-of-two rejection |
| `BetrothedNumbers.same_parity_betrothed` | `f74baaf21ab0825a4c233a8a31a1fef12636b97a` | `e5ab80f43ee1408179131eeb0f6432e1bab9217040cd77f2bb4aa8886ef6ae4b` | two explicit naturals, two exact divisor sums, and a parity check |

Exact GitHub issue/PR searches were run for every module and declaration name,
including open, closed, and merged results. The only matching activity was
statement introduction/materialization: PR #1211 for Erdős 850, PR #2419 and
issue #2240 for almost-perfect numbers, and PR #2264 for betrothed numbers.
Closed PR #2965 concerns only the weaker two-shift Erdős 850 fact; its diff
does not solve the selected three-shift RHS. No later pinned-tree change or
preempting solution was found for any selected declaration.

The literal right-hand sides are:

```lean
-- ErdosProblems/850.lean
∃ x y : ℕ, x ≠ y ∧ x.primeFactors = y.primeFactors
  ∧ (x + 1).primeFactors = (y + 1).primeFactors
  ∧ (x + 2).primeFactors = (y + 2).primeFactors

-- Wikipedia/AlmostPerfectNumbers.lean
∃ n : ℕ, (1 + σ 1 n = 2 * n) ∧ ¬ ∃ k : ℕ, n = 2 ^ k

-- Wikipedia/BetrothedNumbers.lean
∃ m n : ℕ, (σ 1 m = m + n + 1 ∧ σ 1 n = m + n + 1) ∧
  (Even m ↔ Even n)
```

## Target-specific walls fixed before compute

### Erdős 850: radical-signature collision

For positive integers, equality of `Nat.primeFactors` is exactly equality of
the squarefree radical. Thus a witness must be a collision of

```text
S(n) = (rad(n), rad(n+1), rad(n+2)).
```

The implementation represents the empty supports of both `0` and `1` by the
same sentinel, so the natural-number boundary is included rather than silently
discarded. The wall arm first groups integers by `rad(n)` and only compares the
two remaining coordinates inside repeated-radical classes.

### Almost-perfect: odd-part divisor-sum equation

Write `n = 2^r m`, with `m` odd, and put `A = 2^(r+1)`. Multiplicativity of
the divisor sum changes `σ(n) = 2n - 1` into the exact necessary equation

```text
(A - 1)(σ(m) - m) = m - 1,
A = 1 + (m - 1)/(σ(m) - m), and A must be a power of two.
```

For `m = 1` this recovers all power-of-two calibrations. A sought witness must
have `m > 1`, so the wall arm enumerates odd parts rather than flat `n`.

### Betrothed same parity: square/twice-square wall

The common betrothed sum is `σ(m) = σ(n) = m+n+1`. If `m,n` have the
same parity, this value is odd. The classical exact parity criterion for the
divisor sum therefore forces each endpoint to be a square or twice a square.
The wall arm enumerates only

```text
m = a^2 or m = 2a^2,
n = σ(m) - m - 1,
```

then requires `n` to have the same square/twice-square shape and verifies its
divisor sum independently.

## Equal-cap arm receipts

Every row below is a distinct invocation of `timeout -s KILL 60s`. Times are
wall-clock seconds reported by `/usr/bin/time`; every exit status was zero.

| target | arm | exact work | elapsed | outcome |
|---|---|---|---:|---|
| Erdős 850 | `CATALOGUE` | all `0 ≤ n ≤ 1,000,000`; exact three-coordinate support signature | 1.05 s | 1,000,001 distinct signatures; no collision |
| Erdős 850 | `GENERIC` | seed `0x850`; 500,000 uniform draws from `0..5,000,000` | 2.62 s | 475,549 unique inputs; no collision |
| Erdős 850 | `WALL_NAVIGATION` | all `0..5,000,000`, partitioned by the necessary first radical coordinate | 8.29 s | 775,287 repeated-radical classes and 2,735,655 class members checked; no collision |
| almost-perfect | `CATALOGUE` | exact divisor-sum sieve for every `0 ≤ n ≤ 3,000,000` | 6.13 s | 22 power-of-two calibrations; no non-power hit |
| almost-perfect | `GENERIC` | seed `0xA1A057`; 1,000,000 smooth-factor proposals from primes through 43 | 6.83 s | 708,104 unique integers, 9 power-of-two calibrations; no non-power hit |
| almost-perfect | `WALL_NAVIGATION` | exact odd-part equation for every odd `3 ≤ m ≤ 10,000,000` | 10.11 s | 4,999,999 odd parts; 665,234 gave integral `A`; none gave power-of-two `A` |
| same-parity betrothed | `CATALOGUE` | exact divisor-sum sieve with both endpoints in `0..5,000,000` | 15.12 s | no same-parity pair; 35 opposite-parity calibration pairs |
| same-parity betrothed | `GENERIC` | seed `0xBE7007`; 700,000 draws with both endpoints in `0..8,000,000` | 18.18 s | 670,232 unique starts, 10 opposite-parity hit-draws; no same-parity pair |
| same-parity betrothed | `WALL_NAVIGATION` | both square/twice-square families for `1 ≤ a ≤ 1,000,000` | 6.27 s | 2,000,000 shape starts (`m ≤ 2·10^12`); only 29 derived `n` had an admissible shape; none verified |

Incremental controls behaved as expected. The almost-perfect catalogue found
exactly the powers of two in range. The betrothed catalogue began with
`(48,75)`, `(140,195)`, `(1050,1925)`, and `(1575,1648)`, matching the frozen
module's `(48,75)` test and the external tables. Erdős 850's generic and wall
arms strictly enlarged the catalogue universe rather than replaying its prefix.

## Current source/database reconciliation

- The current Erdős Problems #850 page still marks the three-shift question
  open and records the two-shift examples as a weaker result. This agrees with
  the GitHub status gate and with rejecting PR #2965 as a preemption.
- MathWorld currently states that the only known almost-perfect numbers are
  powers of two and that the converse remains open. The bounded zero is
  consistent with, and far weaker than, that research record.
- OEIS A003503 records that all known betrothed pairs have opposite parity and
  gives the same square/twice-square necessary form used by the wall arm. It
  also records prior lower-bound work, so this run is a method replay rather
  than a claimed record improvement.

## Classification

- `Erdos850.erdos_850`: **HOLD_BOUNDED**; no finite positive certificate in
  the catalogue, seeded, or radical-wall searches.
- `AlmostPerfectNumbers.exists_almost_perfect_not_power_of_two`:
  **HOLD_BOUNDED**; no non-power witness in the flat, smooth, or exact odd-part
  searches.
- `BetrothedNumbers.same_parity_betrothed`: **HOLD_BOUNDED**; no same-parity
  witness in the flat, seeded, or parity-wall searches.

No answer is asserted for any of the three opaque biconditionals, and no
bounded zero is promoted to a proof of nonexistence.
