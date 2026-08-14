## Classification first

This release records an exact counterexample to the **merged Lean declaration**
for OEIS A109074. It is a formalization/source erratum, not a disproof of the
corrected number-theory identity, and it is not counted as a mathematical
conjecture kill.

## Literal counterexample

The module defines

`frac n = C(6n-2,2n) / (2 C(4n-1,2n))`

and

`b n = C(3n,n) div (2n+1)`,

then asserts `frac n = b(n+1)/b(n)` for every `n >= 1`. At `n=1`, exact
evaluation gives

- `frac 1 = 1`;
- `b 1 = 1`;
- `b 2 = 3`;
- therefore the asserted right side is `3`.

So the exact merged declaration implies `1 = 3` at its first allowed input.

## Why this is an erratum

The authoritative A005156 values begin `1, 1, 3, 26, 646, ...`. The ratio
printed for A109074 is shifted one step upward; the observed identity instead
uses `A005156(n)/A005156(n-1)` for `n >= 1`. Independently, the Lean module's
local `b` is not A005156: it gives `b 3 = 12`, while A005156(3) is `26`.

This release therefore makes no claim against the corrected identity.

## Immutable artifacts

- [Source/status/classification audit](https://github.com/Kuberwastaken/c5-k4/blob/65859c4/results/expansion/live-search-2026-08-14/oeis-109074.md)
- [Complete no-`sorry` Lean certificate](https://github.com/Kuberwastaken/c5-k4/blob/65859c4/lean/Oeis109074Counterexample.lean)
- [Independent exact verifier](https://github.com/Kuberwastaken/c5-k4/blob/65859c4/scripts/verify_oeis_109074_counterexample.py)
- [Upstream module at the audited commit](https://github.com/google-deepmind/formal-conjectures/blob/b33d8678a28118c95d8d4f60b11faaf39ccff1e6/FormalConjectures/OEIS/109074.lean)
- [OEIS A005156 b-file](https://oeis.org/A005156/b005156.txt)

The Lean certificate passes Lean 4.27.0 warning-as-error elaboration in 5.81
seconds at the frozen upstream commit. The independent verifier reproduces
the same exact values without Lean.

## Method consequence

The useful discovery here is procedural: literal lower-endpoint evaluation
and authoritative first-term replay should precede catalogue, generic, or
wall-navigation search. These cheap gates found both transcription defects
immediately.

## Status and AI assistance

The declaration entered through merged upstream PR #4450 on 2026-08-13.
Repository-wide issue/PR search for `109074` returned no record on 2026-08-14.
No upstream issue or PR is opened by this release.

OpenAI Codex and delegated coding agents assisted with live target search,
source reconciliation, formal certification, independent verification, and
release preparation. The repository owner remains responsible for the claim
and its classification.
