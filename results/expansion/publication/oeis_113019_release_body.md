## Result

The literal OEIS A113019 function has exactly three fixed points:

`1, 32, and 387420489 = 9^9`.

The source names `1` and `32` and asks whether there are others. The third
value answers that intended question affirmatively: it has nine decimal digits
and digital root nine, so the function sends it to `9^9`, itself.

## Why the list is complete

For any positive fixed point, let `d` be its decimal digit count and `r` its
digital root. The definition forces `n=d^r`, where `1 <= r <= 9`.

Exact enumeration for `1 <= d <= 10` gives only `(1,1)`, `(2,5)`, and `(9,9)`.
For `d>=11`, `d^9 < 10^(d-1)`: the inequality holds at 11, and its induction
ratio is bounded by `(12/11)^9 < 10`. Hence `d^r` has fewer than `d` digits and
cannot be fixed.

## Formal-declaration caveat

The DeepMind module encodes the unknown answer as
`answer(sorry) ↔ <only 1 or 32>`. The witness falsifies that proposed RHS and
determines the intended answer. It does not refute the opaque biconditional;
filling its answer placeholder as false would make the wrapper correct.

## Immutable artifacts

- [Derivation, source/status audit, and three-arm receipts](https://github.com/Kuberwastaken/c5-k4/blob/ebd82bb/results/expansion/live-search-2026-08-14/wave2-fresh-deepmind.md)
- [Dedicated result and classification audit](https://github.com/Kuberwastaken/c5-k4/blob/7bc2a0c/results/expansion/live-search-2026-08-14/oeis-113019.md)
- [Complete no-`sorry` Lean witness](https://github.com/Kuberwastaken/c5-k4/blob/7bc2a0c/lean/Oeis113019Counterexample.lean)
- [Independent exhaustive verifier](https://github.com/Kuberwastaken/c5-k4/blob/7bc2a0c/scripts/verify_oeis_113019_fixed_points.py)
- [Audited upstream module](https://github.com/google-deepmind/formal-conjectures/blob/b33d8678a28118c95d8d4f60b11faaf39ccff1e6/FormalConjectures/OEIS/113019.lean)
- [OEIS A113019](https://oeis.org/A113019)

The Lean witness passes Lean 4.27.0 warning-as-error elaboration in 6.12
seconds at the frozen upstream commit.

## Discovery-method relevance

Flat enumeration through one million and a 50,000-point stratified random arm
found only the known values. Wall navigation reduced every possible fixed
point to the exact coordinates `n=d^r`, where the third fixed point appeared
in a 100,000-pair structured sweep. This is a prospective wall-derived hit,
not a retrospective carrier match.

## Priority and AI assistance

The current source still poses the question. Dated GitHub and web searches for
A113019 with `387420489`, `9^9`, and fixed-point terminology found no prior
report. “Apparently unrecorded as of 2026-08-14” is not absolute priority.

OpenAI Codex and delegated coding agents assisted with target selection,
search, exact reduction, source/status checks, Lean certification, independent
verification, and release preparation. The repository owner remains
responsible for the claim and attribution.
