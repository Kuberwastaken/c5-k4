# Bateman--Horn formal counting helper includes zero

Date: **2026-08-14 UTC**  
Disposition: **FRESH FORMALIZATION/SOURCE DEFECT; asymptotically inert**

## Exact defect

At frozen upstream commit
`b33d8678a28118c95d8d4f60b11faaf39ccff1e6`,
`BatemanHornConjecture.CountSimultaneousPrimes` filters

```text
Finset.range (floor(x) + 1),
```

so its candidate integers begin at zero.  The theorem documentation and cited
Bateman--Horn source count **positive** integers; the source uses `n<x`, while
the local prose describes `n<=x`.

For the admissible test polynomial `f(X)=X+2`, `f(0)=2` is prime.  Therefore
at `x=0`:

```text
formal helper count = 1,
positive n<=x count = 0,
positive n<x count  = 0.
```

At `x=1`, the three counts are respectively `2`, `1`, and `0`.  This
separates both convention changes: inclusion of zero and `<` versus `<=`.

## Mathematical classification

This does not refute Bateman--Horn.  Removing `n=0` and changing the treatment
of the single upper endpoint changes the counting function by a bounded amount
for a fixed polynomial family.  Such a finite perturbation does not change the
asymptotic-equivalence statement at infinity.

The finding is instead an exact mismatch between the formal helper and its
intended/source counting domain.  It should not enter any conjecture-kill
count.

## Status and verification

- Live searches for `BatemanHorn`, `CountSimultaneousPrimes`, and the exact
  module found no matching open, closed, or merged upstream issue/PR as of
  2026-08-14.
- The full domain audit, two bounded-zero control clusters, commands, budgets,
  and independent replay are in `wave3-domain-boundaries.md`.
- Independent executable replay:
  `python3 scripts/verify_bateman_horn_count_endpoint.py`.
- No-`sorry` Lean endpoint certificate:
  `lean/BatemanHornCountEndpoint.lean`.
- Lean 4.27.0 warning-as-error elaboration passes in 6.95 seconds at the frozen
  upstream commit.

## Method lesson

For asymptotic declarations, a finite endpoint mismatch usually cannot refute
the theorem even when it falsifies the helper's prose.  The search gate must
therefore retain two separate outputs: definition-alignment defects and
truth-value crossings.  Finding the former is useful validation work, but it
must never be marketed as the latter.
