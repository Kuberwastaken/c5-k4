# Next DeepMind rotation after A231201

**Audit time:** 2026-08-14 UTC
**Disposition:** `RANKED_NOT_FROZEN_NOT_EVALUATED`
**Recommended next target:** OEIS A056777

This is a read-only target-selection report. It does not authorize or record a
search, candidate, proof, release, issue, pull request, or public claim.
Written on the Wall I is outside DeepMind's corpus and was neither ranked nor
used.

## Current pin and subtraction

The audited upstream is
[`google-deepmind/formal-conjectures@05ea0345d09375efac830fac93bf083b654e317e`](https://github.com/google-deepmind/formal-conjectures/commit/05ea0345d09375efac830fac93bf083b654e317e),
the live `main` tip resolved independently by `git ls-remote` and a sparse
checkout. All three ranked declarations below still contain `sorry` and are
tagged `@[category research open]` at that commit.

The ranking subtracts completed project work. In particular, it does not
recycle the exhausted A063880 factor-core universe, the A105720 finite grids,
the A105565 theorem shadow, A108081 through its recorded state-growth wall, or
any A231201 version. It also excludes source/formalization errata,
answer-placeholder questions without the required resolution shape, and every
target with an existing local result or current resolving upstream claim.

| rank | declaration | current file locks | live duplicate/status audit |
|---:|---|---|---|
| 1 | `OeisA56777.comesFromPrimeQuadruple_of_a` | `FormalConjectures/OEIS/56777.lean`; Git blob `a6dd44fb981be19a5a8bc19de54ef8e533519627`; SHA-256 `2539ce34a7417a5b482d3c6f21a8327198e4890df7f67e6458a522293b1d099c` | no open PR returned for `56777`, `ComesFromPrimeQuadruple`, or the exact declaration; statement PR #1867 and later closed/merged items prove only tests, the forward implication, or congruence lemmas; the reverse implication remains open |
| 2 | `OeisA67720.prime_add_one_of_a` | `FormalConjectures/OEIS/67720.lean`; Git blob `c43381687cfcf605679ad268fefcab70ae01bc64`; SHA-256 `af8ae5ba8ebed4d7252b9cee3d6cb7e304f7971282db7f8954ce2f0da99d249e` | no open target PR; merged PR #1878 introduced the statement and proved only the forward prime construction |
| 3 | `OeisA108569.conjecture` | `FormalConjectures/OEIS/108569.lean`; Git blob `daf4427246c28b56a429646958a2c38ca4cf04fa`; SHA-256 `0e62b2d15f41a2b2dbcc568a63abd3644e8429fa7befdec7cc2d0e96cc6244f8` | no open target PR; merged batch PR #4450 introduced the current declaration; no resolving path change was found |

The GitHub audit covered current files, exact-path history, and open/closed PR
searches. It is a point-in-time public audit, not evidence about private or
unpushed work, and must be refreshed immediately before dispatch.

## 1. A056777 — factor-shape escape from the prime-quadruple wall

### Literal resolution shape

The formal predicate is

```text
A(n) := not Prime(n), 1<n,
        phi(n+12)=phi(n)+12,
        sigma(n+12)=sigma(n)+12.
```

The conjecture says every such `n` is `p(p+8)` for primes
`p,p+2,p+6,p+8`. Its negation has a compact finite certificate: one labelled
factorization of `n` and `n+12`, exact `phi` and `sigma` products establishing
both equalities, and a proof that no prime `p` realizes `n=p(p+8)`. This is a
direct finite universal; no answer placeholder or asymptotic quantifier is
involved.

### Residual wall and theorem subtraction

Use the two-coordinate residual

```text
R_phi(n)   = phi(n+12)   - phi(n)   - 12,
R_sigma(n) = sigma(n+12) - sigma(n) - 12.
```

The known family sits exactly at `(0,0)`. More importantly, the obvious
factor class can be subtracted before searching. If

```text
n = a*b,       n+12 = c*d
```

with both endpoints squarefree semiprimes, then the two residual equations
both reduce to `a+b=c+d`. Writing the two factor gaps as `g` and `h`, the
product difference gives

```text
g^2 - h^2 = 48.
```

The integral gap pairs are `(g,h)=(8,4)`, `(13,11)`, and `(7,1)`. The latter
two have odd gaps and cannot make both pairs prime: the wider prime pair would
have to start at `2`, giving respectively `2,15` or `2,9`. The even-gap pair
is exactly

```text
(a,b,c,d) = (p,p+8,p+2,p+6).
```

Thus a counterexample cannot be obtained by merely moving along the
squarefree-semiprime equality manifold. At least one endpoint must introduce
a repeated prime power or three-or-more-prime factor geometry. This is the
precise obstruction identity and separating coordinate the method asks for.

### Source and database-sanity gate

The pinned OEIS source record is `oeisdata@8872fa543438401edd424a57b67ad5e0737bebfb`,
`seq/A056/A056777.seq`, SHA-256
`67a9fd6b1b5114a4aa09f4d01967d15e54266dd09902699fe40ce4d8b9e54d63`.
It says the reverse implication and the `65 mod 72` observation were verified
through `10^12`. The current 166-row b-file has SHA-256
`8a4d205fea5761af6deac8c2bf23d709c4e7844e792f48bf8616135376835ccf`
and ends at `967164068009`.

Before construction, independently factor and replay all 166 rows, their
prime-quadruple witnesses, both arithmetic-function equalities, and the named
controls `65`, `209`, and `11009`. Any candidate at or below `10^12` is a
historically covered control, not a discovery. A source mismatch, incomplete
factorization, or failure of either exact equality stops the lane.

### Proposed equal-cap arms

1. **Catalogue/control:** replay the source table and algebraically exhaust the
   squarefree-semiprime gap equation. It may validate the implementation but
   cannot emit a candidate.
2. **Repeated-power surgery:** enumerate a frozen list of coprime prime-power
   block shapes for one endpoint, derive/factor the other endpoint exactly,
   and score `(R_phi,R_sigma)`. The prime list, exponent list, block count,
   order, and size interval above `10^12` must be fixed before evaluation.
3. **Factor-block wall navigation:** parameterize `n=A*B` and
   `n+12=C*D` with small frozen block offsets around the `(8,4)` gap wall,
   allow one block to be powerful or composite, and retain only exact
   multiplicative `phi`/`sigma` rows. This tests the predicted escape rather
   than scanning consecutive integers.

Each arm gets a 54-second internal horizon inside an external process-group
cap of exactly 60 seconds. Factoring children have their own subcaps; only
proved-prime factors and complete factorizations may enter a terminal row.
Append-only rows must be flushed incrementally.

**Stop rule:** stop after the frozen factor-shape universe or the cap. Do not
add a prime, exponent, factor block, offset, backend, or size band after seeing
the result. A hit in the semiprime class is a control/theorem-shadow failure;
an unfactored endpoint is `INCOMPLETE_FACTOR_CERTIFICATE`, never a candidate.

**Why this is the best method test:** it starts on an exact two-invariant wall,
proves the visible family cannot cross, identifies the missing factor-shape
coordinate, and asks a new construction to separate it. It is also
qualitatively different from A231201's residue-cover lane.

## 2. A067720 — escape the unique composite-successor exception

### Literal resolution shape and wall

The declaration asserts

```text
phi(k^2+1) = k*phi(k+1) and k != 8  ==>  Prime(k+1).
```

A counterexample is one explicit `k != 8` with complete factorizations of
`k+1` and `k^2+1`, exact totient products proving the equality, and a
nontrivial factor of `k+1`. The residual is the exact integer

```text
R(k) = phi(k^2+1) - k*phi(k+1).
```

When both `k+1` and `k^2+1` are prime, `R=0` automatically. The only known
composite-successor equality is the structurally different seed

```text
k=8,  k+1=3^2,  k^2+1=5*13,
phi(65)=48=8*phi(9).
```

The separating coordinate is therefore the prime-exponent profile of `k+1`,
not a larger flat prefix.

### Source gate, arms, cap, and stop

The pinned OEIS record `seq/A067/A067720.seq` has SHA-256
`13c478e7850f14ecf1f3ed5a78a28ffee42ef6429539943b87a068fe3c761aa4`.
Its 10,000-row b-file has SHA-256
`c50d6120a72dfda1f6bf82642407007ea68604c76788a8e98c2f43cfeb9bb928`
and ends at `1548870`. The gate must replay every row, prove the totient
identity, and verify that `8` is the only table row with composite `k+1`.
Rows within that table are controls only.

Run three frozen arms: source catalogue; `k+1=q^e`/two-prime exponent-profile
surgery seeded by `3^2`; and an exact meet-in-the-middle search over reduced
totient-factor ratios. Every arm has a 54-second internal and 60-second
external cap with incremental exact-factor receipts.

**Stop rule:** stop at the frozen exponent/profile universe or cap. No
probable-prime or partially factored `k^2+1` may be promoted, and no profile
may be added after observing the nearest residual.

This ranks second because the certificate is smaller and the exceptional seed
is sharp, but the prospective obstruction is not yet as fully reduced as the
A056777 gap theorem.

## 3. A108569 — odd-core escape from an even totient family

### Literal resolution shape and wall

The underlying membership predicate is

```text
A(k) := 0<k and phi(k)=phi(k+phi(k)).
```

The declaration says every enumerated member after the first is even. An odd
member `k>1` is the mathematical crossing. To refute the literal Lean theorem,
the certificate must additionally bind the exact index
`i = count(A,{0,...,k-1})` and prove `a(i)=k` with `i>0`; membership alone is
not enough because `a` is defined through `Nat.nth`.

The exact residual is

```text
R(k) = phi(k+phi(k)) - phi(k).
```

Known source families are even and closed under powers-of-two lifts. The
separating transformation is to strip that lift, freeze odd prime-exponent
cores, and ask whether totient-collision geometry survives without the factor
two.

### Source gate, arms, cap, and stop

The OEIS record `seq/A108/A108569.seq` has SHA-256
`66a98eb6032c98c12f6bf8250c30356775c434fae4ca4cc2b8ed98eb04d83d9f`.
The current b-file has 384 rows through `997694` and SHA-256
`a84aa7eb3295768365d07e081bcaf7b4f0b6d412b6e0615128d615148c238544`.
The gate must replay all rows, the source's even lift identities, and the exact
index convention; all table rows are historical controls.

Use source catalogue, frozen odd powerful-core enumeration, and odd-core
surgery obtained by removing the maximal power of two from known even
families. Each process has the same 54/60-second cap and complete factorization
requirements.

**Stop rule:** stop at the fixed odd-core universe. A mathematical odd member
without a complete `Nat.nth` rank replay is `SEMANTIC_CANDIDATE_ONLY`, not a
formal counterexample.

This ranks third because it tests a clean parity-separation idea, but the
enumeration-index certificate is materially heavier than the direct
implications above.

## Deferred, not ranked for execution

- A034693 has a finite negation, but the stronger bound is source-verified
  through `10^9`; a counterexample certificate would have to certify
  compositeness of an enormous whole interval. A finite small-prime periodic
  cover has the same unavoidable escape-class obstruction exposed by the
  A231201 theorem shadow.
- A103151 has a literal finite Goldbach-type miss, but no comparably sharp
  obstruction identity or transformation is currently known.
- A063880, A105720, A105565, A108081, and A231201 already have terminal local
  evidence and are not rotations.

## Selection

Freeze **A056777 only** as the next execution lane, after one fresh live
status/duplicate check. Preserve A067720 and A108569 as ordered reserves. A
zero on A056777 is still useful method evidence because the squarefree
semiprime theorem subtraction and the specified non-semiprime escape are
prospective; it is not evidence that the global conjecture is true.
