# Live search: newly added DeepMind OEIS declarations

Started: 2026-08-14 UTC

This is a live development lane, not part of the uncontaminated Method v1.5
benchmark.  It uses current upstream
`google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.
Every subprocess is capped at 60 seconds.  A bounded zero is not a truth claim.

## Upstream delta and target gate

The current upstream tip adds 64 OEIS modules relative to the earlier finite-
graph manifest commit `d16e05aded22b8c467a0a27c14b2311f53185006`.
The main-agent lane selected direct universal statements with executable exact
definitions; answer-valued questions and asymptotic/existential statements are
not treated as counterexample candidates without a certificate-shape gate.

## Catalogue/generic arm: OEIS A001157

Declaration: `FormalConjectures/OEIS/1157.lean`, conjecturing that for every
`k >= 2` the fractional parts of `sigma_k(n) / n^k` are pairwise distinct over
positive `n`.

- Status gate: introduced by upstream PR #4450; no matching open or merged
  solution PR was returned by the repository search at lane start.
- Exact evaluator: Python `Fraction`; divisor-pair enumeration by integer square
  root; no floating point.
- Frozen grid: `2 <= k <= 12`, `1 <= n <= 20,000`.
- Budget/result: 4.0 seconds; no collision in any of the 11 rows.
- Classification: `HOLD_BOUNDED`, not a proof and not a release candidate.
- Structural observation: since `1 < sigma_k(n)/n^k < 2` for `k >= 2`, the
  tested fractional part is exactly the proper reciprocal-divisor sum.  Future
  wall work should operate on prime-exponent vectors and equality of the
  multiplicative products, rather than extend a flat `n` scan.

## Catalogue/generic arm: OEIS A109908/A109909

Declarations: `FormalConjectures/OEIS/109908.lean` and `109909.lean`.  Both
assert that for every `n > 3` at least one distinct value `k(n-k)-1` is prime.

- Exact evaluator: byte-sieve primality through the largest tested quadratic
  value, followed by complete `1 <= k <= floor(n/2)` enumeration.
- Frozen grid: `4 <= n <= 30,000`.
- Budget/result: 2.7 seconds; every `n` has a prime witness.
- Classification: one correlated `HOLD_BOUNDED` cluster, not two results.
- Structural observation: flat enumeration is extremely cheap at this range;
  the useful wall coordinate is the least witnessing `k`.  A next arm should
  target residue classes where all small `k` are forced composite, rather than
  merely increasing the same prefix.

## Direct exact checks on five further clusters

All rows below were independent executable checks of the literal Lean
definitions, not values copied from OEIS.

| declaration cluster | exact frozen range | wall / result |
|---|---|---|
| A112521 NOR diagonal | `1 <= n <= 500`; direct alternating binomial sum versus a separately memoized two-dimensional `T(n,k)` recurrence | 6.3 s; equality throughout; `HOLD_BOUNDED` |
| A112970 generalized Stern identities | all three declarations for `0 <= n <= 10,000`; memoized recurrence evaluated at the exponentially indexed arguments | 4.3 s; all equalities throughout; `HOLD_BOUNDED` |
| A113250/A113252/A113255 odd-index squares | each recurrence through index 1,999, testing `0 <= n <= 999` by integer square root | 0.24 s; every odd term square; one correlated `HOLD_BOUNDED` family |
| A110475 exceptional sums | exact characterization of `a(x)=1` from prime-factor exponent vectors, Boolean convolution through `m=1,000,000`, followed by direct witness replay | 11.7 s; exactly the nine stated exceptions; `HOLD_BOUNDED` |
| A108866 prime congruence | incremental exact rational sum and reduced integer numerator for every `4 <= n <= 20,000`, compared with independent trial-division primality | 40.3 s; biconditional holds throughout; `HOLD_BOUNDED` |

These rows exposed a useful selector rule: the three square declarations share
one recurrence-family explanation and must count once, while the A112970
exponential-looking indices remain computationally cheap because the recursive
arguments contract immediately.  Parameter magnitude alone is therefore a
poor budget proxy; recursion-state count and certificate shape should control
the generic schedule.
