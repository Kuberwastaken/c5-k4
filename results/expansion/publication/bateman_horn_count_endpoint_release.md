# Bateman--Horn count-endpoint release checklist

Date: **2026-08-14 UTC**

## Eligibility and classification

- Scope: `BatemanHornConjecture.CountSimultaneousPrimes` at
  `google-deepmind/formal-conjectures@b33d8678a28118c95d8d4f60b11faaf39ccff1e6`.
- Exact defect: the formal helper includes `n=0`, while the theorem prose and
  cited source count positive integers; the source also uses `<x` rather than
  the local `<=x` convention.
- Exact witness: for `f(X)=X+2`, formal count at `x=0` is one, while both
  positive-integer readings give zero.
- Classified as an **asymptotically inert formalization/source defect**.  It
  neither falsifies the open theorem nor attacks Bateman--Horn mathematics.
- Exact upstream searches found no matching issue, PR, or prior fix on
  2026-08-14.
- No upstream issue, PR, or comment will be opened under the current policy.

## Durable artifacts

- Full domain audit and independent replay: `8b17c46`.
- Dedicated classification audit, independent verifier, and no-`sorry` Lean
  endpoint certificate: `bc93e57`.
- Lean 4.27.0 warning-as-error elaboration: pass under seven seconds at the
  frozen upstream commit.

## Planned release

- Tag: `bateman-horn-count-endpoint-v1`.
- Title: `Bateman–Horn formalization: counting helper includes n=0`.
- Explicitly not marked Latest, so the A113019 mathematical result remains the
  repository's Latest release.
- No generated binary assets.

## Release lock and publication readback

Pending creation of the preflight commit and release.  A follow-up commit will
record the exact tag target and readback.
