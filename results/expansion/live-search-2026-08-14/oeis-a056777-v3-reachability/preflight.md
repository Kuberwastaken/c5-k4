# OEIS A056777 v3 squarefree-triple reachability preflight

**Audit date:** 2026-08-14 UTC

**Disposition:** `STRICT_STOP_CROSSING_UNREACHABLE`

**Evidence class:** target-free `DEVELOPMENT` constructor audit

**Target evaluations:** zero

This preflight audits only the proposed squarefree-triple / squarefree-triple
sum-neighbor surgery in
[`oeis-a056777-near-wall-surgery.md`](../oeis-a056777-near-wall-surgery.md).
It does not evaluate `OeisA56777.comesFromPrimeQuadruple_of_a`, test terminal
values for primality, compute `phi` or `sigma`, inspect sequence membership,
or form a mathematical counterexample candidate. It creates no frozen target
workflow and authorizes no dispatch, release, issue, pull request, or other
public action.

## Frozen constructor domain being audited

The proposed pilot uses ordered prime blocks

```text
P = r*s,  R = r+s,
Q = t*u,  T = t+u,
```

where `r<s` and `t<u` are drawn from prime ranks `97..1024`, namely the
928 primes from `509` through `8161`. It restricts the block-sum displacement

```text
d = T-R,  1 <= |d| <= 64.
```

All block primes are odd, so `R`, `T`, and `d` are even. Both endpoint
orientations are already represented by allowing positive and negative `d`.
No rank, displacement, or block shape was added after the diagnostic.

The constructor equations proposed in the development note are

```text
E = Q-P,
p = T-E/d,
q = R-E/d,
d * (Q*R-P*T-12) = E^2.                         (1)
```

The reachability gate asks only whether an allowed second prime block
`(t,u)` can satisfy this integer/product geometry. Terminal `p,q` are outside
this gate: their primality and all target invariants remain unevaluated.

## Exact discriminant reduction

Substituting `T=R+d` and `Q=P+E` into (1) gives

```text
E^2 - d*R*E + d^2*P + 12*d = 0.
```

Because `R^2-4P=(s-r)^2`, integer `E` requires

```text
z^2 = d^2*(s-r)^2 - 48*d.                       (2)
```

Write `h=s-r`. Equation (2) has a finite divisor certificate. For `d>0`,

```text
(d*h-z) * (d*h+z) = 48*d;
```

for `d=-e<0`,

```text
(z-e*h) * (z+e*h) = 48*e.
```

Enumerating the divisors of `48*|d|` for the 64 allowed nonzero even values
of `d` yields only 16 positive `(d,h,z)` triples. Since a difference of two
odd block primes is even, only four survive:

| `d` | `h=s-r` | `z` |
|---:|---:|---:|
| `-4` | `2` | `16` |
| `4` | `4` | `8` |
| `12` | `2` | `0` |
| `16` | `2` | `16` |

These four cases close symbolically:

- `d=16,h=2` makes `E=8(R+1)` or `8(R-1)`. Since `R` is even, neither is
  divisible by 16, so `p,q` are not integral.
- `d=-4,h=2` gives second-block discriminant `-12` for one root and `52`
  for the other; neither reconstructs integer `t,u`.
- `d=12,h=2` gives second-block discriminant `148`, not a square.
- `d=4,h=4` gives discriminant `48` for one root. The other reconstructs
  `t=r+2` and `u=s+2=r+6`. But `s=r+4`, so it would require
  `r,r+2,r+4` all prime. For `r>=509`, these are three consecutive odd
  residue classes modulo three, one of which is divisible by three. This is
  impossible.

Therefore no state in the proposed pilot can even construct its second
allowed prime block. The failure precedes terminal primality and the formal
target predicate.

## Independent finite replay

Two exact integer enumerators independently reproduced the symbolic stop:

1. a direct scan over all block pairs and all allowed even `d`, followed by
   `isqrt` tests for (2), exact divisibility for `E/d`, and quadratic
   reconstruction of `t,u`;
2. divisor enumeration of `48*|d|`, followed by an exact join against the
   prime-gap table and the same reconstruction.

The complete counters were:

| Stage | Exact count |
|---|---:|
| ordered source block pairs `(r,s)` | 430,128 |
| `(r,s,d)` rows | 27,528,192 |
| rows with square discriminant (before root orientation) | 604 |
| integral oriented `(r,s,d,z,E)` rows | 749 |
| reconstructed allowed prime blocks `(t,u)` | **0** |
| terminal-primality calls | **0** |
| `phi`/`sigma` or formal-target calls | **0** |

Both implementations produced exactly the same 749-row intermediate set.
Canonical sorted-row hashes are:

```text
16 divisor-derived (d,h,z) triples:
  70bd7e8910c4bef515bcf3f355d7cbf016e772c1723e4e660305455ed20748b6

749 integral oriented algebraic rows:
  262dc21717948c17c5ea0b791e54589ab58611e2913facde7fa9fc90355d9f60

0 reconstructed prime-block rows:
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Among the 749 intermediate rows, the only represented displacements were
`d=-4` (306 rows), `d=4` (290 rows), and `d=12` (153 rows); the `d=16`
case fails the `E/d` integrality test as predicted. The only represented
prime gaps were two and four.

## Gate decision

The decision is **`STRICT_STOP_CROSSING_UNREACHABLE`** for this entire frozen
pilot domain. It is stronger than a bounded target zero: target evaluation
would be guaranteed to receive no constructed state. Increasing worker count,
changing a solver, widening the terminal-value band, or extending prime ranks
while retaining `|d|<=64` cannot repair the symbolic obstruction.

There is consequently no v3 target-domain proposal and no reason to build or
dispatch a workflow for this arm. Any continuation must be a separately
designed transformation that changes the block exponent shape or the frozen
sum-displacement geometry and must pass its own target-free reachability gate.
The exponent-asymmetric power/triple construction listed later in the
development note is such a qualitatively different reserve, but it was not
audited or authorized here.

