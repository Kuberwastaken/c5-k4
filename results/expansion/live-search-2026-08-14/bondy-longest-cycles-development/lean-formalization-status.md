# Bondy C4-factor Lean formalization status

- Classification: `PARTIAL_FORMALIZATION / PROOF_ENGINEERING_STOP`
- Compiled no-`sorry` scope: exact frozen row 0
- General theorem formalized: no
- All 96 frozen rows formalized: no
- Candidate or release: none

The exact row-0 certificate is
[`BondyC4FactorHamiltonian.lean`](../../../../lean/BondyC4FactorHamiltonian.lean).
It compiles warning-as-error in approximately 4.4 seconds and proves
`rowZero.IsHamiltonian` from an explicit 20-cycle. Its exact axiom report is
`propext`, `Classical.choice`, `Lean.ofReduceBool`, `Lean.trustCompiler`, and
`Quot.sound`; it contains no `sorryAx`.
The reproduced build used formal-conjectures checkout
`9a1636c4030039f70cf78b866c216d8b6c5f35b0`, Lean 4.27.0, and mathlib revision
`a3a10db0e9d66acbebf76c5e6a135066525ac900`.

Two bounded attempts were made to package all 96 exact frozen rows into one
quantified Lean theorem. The first used one monolithic reflected graph-hom
check and hit the 60-second cap without a Lean diagnostic. The second split
the certificate into 20 transition checks, but the symbolic 400-case
graph-hom bridge encountered free-variable reflection errors and the 200,000
heartbeat limit. The second attempt exited before 60 seconds with no compiled
all-row theorem or trustworthy axiom report.

The unverified drafts are deliberately not committed. Their failure is proof
engineering around the generic `SimpleGraph.Hom` bridge, not a failed finite
cycle certificate: the independent executable replay still constructs and
checks Hamilton cycles for all 96 rows. The authoritative mathematical result
and replay remain the
[`C4`-factor Hamiltonicity theorem shadow](c4-factor-hamiltonicity-theorem.md)
and [`verify_bondy_c4_factor_theorem.py`](../../../../scripts/verify_bondy_c4_factor_theorem.py).

Formalizing the general theorem would require either a reusable compatible
Euler-tour development in mathlib or a more efficient bridge from the exact
finite cycle table to `SimpleGraph.IsHamiltonian`. Neither is claimed here.
