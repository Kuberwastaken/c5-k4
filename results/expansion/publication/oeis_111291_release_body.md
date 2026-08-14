## Classification first

This release records an exact counterexample to the **merged Lean declaration**
for OEIS A111291. It is a real-domain formalization/endpoint erratum, not a
disproof of the intended integer or eventual refactorable-number conjecture,
and it is not counted as a mathematical conjecture kill.

## Literal counterexample

The module asserts for every real `x > 1` that

`countRefactorable(x) >= x / (2 log x)`.

At `x=3/2`, the formal counting function floors the input and counts only the
refactorable integer 1, so its value is exactly 1. The standard inequality
`0 < log(3/2) < 1/2` gives

`(3/2) / (2 log(3/2)) > 3/2 > 1`.

Therefore the exact merged declaration is false.

## Why this is an endpoint erratum

A111291 records counts at the integer thresholds `10^n`. Translating the
informal size variable into every real `x>1` creates a step-function interval
where the denominator tends to zero. This witness says nothing against an
integer-threshold or sufficiently-large version.

As calibration, the independent verifier exhaustively checked every integer
`2 <= x <= 1,000,000` and found no violation. The smallest sampled slack is
approximately 0.20136 at `x=7`. This bounded zero is classification evidence,
not a proof of the intended universal statement.

## Immutable artifacts

- [Source/status/classification audit](https://github.com/Kuberwastaken/c5-k4/blob/892826d/results/expansion/live-search-2026-08-14/oeis-111291.md)
- [Complete no-`sorry` Lean certificate](https://github.com/Kuberwastaken/c5-k4/blob/892826d/lean/Oeis111291Counterexample.lean)
- [Independent verifier and integer calibration](https://github.com/Kuberwastaken/c5-k4/blob/892826d/scripts/verify_oeis_111291_counterexample.py)
- [Upstream module at the audited commit](https://github.com/google-deepmind/formal-conjectures/blob/b33d8678a28118c95d8d4f60b11faaf39ccff1e6/FormalConjectures/OEIS/111291.lean)
- [OEIS A111291 b-file](https://oeis.org/A111291/b111291.txt)

The Lean certificate passes Lean 4.27.0 warning-as-error elaboration in 7.04
seconds at the frozen upstream commit.

## Method consequence

Boundary checks must inspect the quantified domain, not just the first integer.
Step-counting functions divided by terms tending to zero should be ranked
before expensive catalogue, generic, or wall-navigation search.

## Status and AI assistance

The declaration entered through merged upstream PR #4450 on 2026-08-13.
Repository-wide issue, PR, review-comment, and commit searches found no prior
fix on 2026-08-14. No upstream issue or PR is opened by this release.

OpenAI Codex and delegated coding agents assisted with live search, exact
formal certification, status checks, independent verification, and release
preparation. The repository owner remains responsible for the claim and its
classification.
