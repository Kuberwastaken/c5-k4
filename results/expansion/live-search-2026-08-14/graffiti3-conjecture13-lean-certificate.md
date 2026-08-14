# Graffiti³ Conjecture 13: standalone Lean arithmetic certificate

Date: **2026-08-14 UTC**

Scope: **complete finite arithmetic witness; no DeepMind declaration or
minimality claim**

## Certified witness

The candidate is

```text
n = 81,722,145
  = 3 * 5 * 17 * 29 * 43 * 257,
phi(n) = 38,535,168.
```

All six displayed factors are prime and pairwise coprime.  The exact source
premise has positive integer margin

```text
9*n - 19*phi(n) = 3,331,113,
```

so `19*phi(n) <= 9*n`.  The base-two Fermat computation is

```text
2^(n-1) mod n = 1.
```

Because `3` is a proper divisor of `n`, the witness is composite.  It is
therefore a base-two Fermat pseudoprime satisfying the premise of Graffiti³
Conjecture 13, contradicting the printed implication.

## Lean scope

[`lean/Graffiti3Conjecture13Arithmetic.lean`](../../../lean/Graffiti3Conjecture13Arithmetic.lean)
imports Mathlib directly and contains no `sorry`.  It proves:

1. the complete six-prime product reconstruction and primality of every
   factor;
2. compositeness from the proper divisor three;
3. the exact totient value by repeated multiplicativity over the pairwise
   coprime factors;
4. the modular power with Mathlib's proof-producing repeated-squaring
   reduction, followed by conversion to the natural-number remainder form;
5. the exact ratio margin, the non-strict source premise, the pseudoprime
   predicate, and failure of the source-normalized implication at `n`.

The frozen search reports this as its smallest candidate.  The Lean module
does not formalize the enumeration or assert global minimality; it certifies
the finite witness only.

Graffiti³ Conjecture 13 is not declared in
`google-deepmind/formal-conjectures`.  The module accordingly has no
`FormalConjectures` import and makes no claim about a DeepMind declaration.

## Replay status

Local warning-as-error replay **passed** against
`leanprover-community/mathlib4@a3a10db0e9d66acbebf76c5e6a135066525ac900`
(Lean `v4.27.0`) with:

```text
lake env lean -DwarningAsError=true \
  /Users/kuber.mehta/Projects/c5-k4/lean/Graffiti3Conjecture13Arithmetic.lean
```

Only the dependency closures of `Mathlib.Data.Nat.Totient`,
`Mathlib.Tactic.NormNum`, `Mathlib.Tactic.NormNum.GCD`,
`Mathlib.Tactic.NormNum.Prime`, and `Mathlib.Tactic.ReduceModChar` were
unpacked for this replay.  The regenerable local oleans were removed again
after the successful check to preserve VPS storage.

The generic mathlib-only workflow
[`standalone-mathlib-certificate.yml`](../../../.github/workflows/standalone-mathlib-certificate.yml)
checks out an immutable campaign commit and that exact Mathlib commit, rejects
a `FormalConjectures` import, retrieves only the five imported Mathlib
dependency closures, and compiles the certificate with
`-DwarningAsError=true`.  The workflow has not yet been dispatched because
these files are intentionally left uncommitted for the parent campaign agent.
This note must be updated with the immutable successful Actions run before a
release cites CI replay.
