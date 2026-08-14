## Classification first

This release records an asymptotically inert definition/source mismatch in the
formal Bateman–Horn counting helper. It is **not** a counterexample to the
Bateman–Horn conjecture and is not counted as a mathematical kill.

## Exact endpoint mismatch

`CountSimultaneousPrimes` filters `Finset.range (floor x + 1)`, so it includes
`n=0`. The theorem documentation and cited source count positive integers; the
source uses `n<x`, while the local prose uses `n<=x`.

For `f(X)=X+2`, the formal helper returns one at `x=0` because `f(0)=2` is
prime. Both intended positive-integer readings return zero. At `x=1`, the
formal, positive-`<=`, and positive-`<` counts are respectively `2,1,0`.

Changing these endpoints changes the count only by a bounded amount for a
fixed polynomial family, so it does not change the asymptotic equivalence at
infinity.

## Immutable artifacts

- [Full domain audit](https://github.com/Kuberwastaken/c5-k4/blob/8b17c46/results/expansion/live-search-2026-08-14/wave3-domain-boundaries.md)
- [Dedicated classification audit](https://github.com/Kuberwastaken/c5-k4/blob/bc93e57/results/expansion/live-search-2026-08-14/bateman-horn-count-endpoint.md)
- [No-`sorry` Lean endpoint certificate](https://github.com/Kuberwastaken/c5-k4/blob/bc93e57/lean/BatemanHornCountEndpoint.lean)
- [Independent executable replay](https://github.com/Kuberwastaken/c5-k4/blob/bc93e57/scripts/verify_bateman_horn_count_endpoint.py)
- [Audited upstream module](https://github.com/google-deepmind/formal-conjectures/blob/b33d8678a28118c95d8d4f60b11faaf39ccff1e6/FormalConjectures/Wikipedia/BatemanHornConjecture.lean)

The Lean certificate passes Lean 4.27.0 warning-as-error elaboration at the
frozen upstream commit.

## Method consequence

Definition alignment and theorem truth are now separate result channels. An
endpoint defect in an asymptotic helper is useful validation work, but the
pipeline must not promote it to a conjecture crossing.

## Status and AI assistance

Exact upstream issue/PR searches found no prior report on 2026-08-14. No
upstream issue or PR is opened by this release.

OpenAI Codex and delegated coding agents assisted with audit, source/status
checks, exact replay, Lean certification, and release preparation. The
repository owner remains responsible for the classification.
