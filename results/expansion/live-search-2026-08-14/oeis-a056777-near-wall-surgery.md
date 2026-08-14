# A056777 near-wall block surgery

**Status:** algebraic development note with bounded diagnostics
**Scope:** the observed point immediately above `10^12`; no candidate,
exhaustive interval claim, novelty claim, publication action, or change to the
frozen development search is made here.

## Observed wall point

The best observed search point was

```text
n     = 1000000000002 = 2 * 3 * 166666666667 = 6p,
n+12  = 1000000000014 = 2 * 3 * 166666666669 = 6(p+2),
R_phi = -8,
R_sigma = 12,
Delta K = 4.
```

Here and below, with `m=n+12`,

```text
C(x) = x - phi(x),
S(x) = sigma(x) - x,
K(x) = S(x) - C(x) = sigma(x) + phi(x) - 2x,

R_phi(n)   = phi(m) - phi(n) - 12 = C(n) - C(m),
R_sigma(n) = sigma(m) - sigma(n) - 12 = S(m) - S(n),
Delta K    = K(m) - K(n) = R_phi(n) + R_sigma(n).
```

For a prime `p` coprime to `6`,

```text
C(6p) = 4p + 2,
S(6p) = 6p + 12.
```

Replacing `p` by `p+2` therefore changes `C` by `8` and `S` by `12`.
This gives the displayed signed residuals exactly; they are not numerical
noise that can be improved by moving farther along the same prime line.

## Exact fixed-block algebra

Consider a proposed surgery

```text
n = A p,
m = B q = A p + 12,
```

where `p,q` are prime, `gcd(A,p)=gcd(B,q)=1`, and the representation is made
canonical by requiring the terminal prime to exceed every prime factor in its
block.  Put

```text
alpha = phi(A),       a = sigma(A),
beta  = phi(B),       b = sigma(B),
k_A = a + alpha - 2A,       h_A = a - alpha,
k_B = b + beta  - 2B,       h_B = b - beta.
```

Multiplicativity gives the block-linear identities

```text
C(Ap) = (A-alpha)p + alpha,
S(Ap) = (a-A)p + a,
K(Ap) = k_A p + h_A.                                      (1)
```

Since `q=(Ap+12)/B`, preservation of `K` is equivalent to

```text
D_K p = N_K,                                               (2)

D_K = B k_A - A k_B,
N_K = B(h_B-h_A) + 12 k_B.
```

Thus every fixed ordered block pair `(A,B)` normally supplies at most one
candidate:

```text
p = N_K / D_K,
q = (Ap+12)/B.                                             (3)
```

The independent totient equation is

```text
(beta A - alpha B)p = B(12+beta-alpha) - 12 beta.          (4)
```

Once (2) gives `Delta K=0`, it is enough to check (4), because then
`R_sigma=-R_phi`.  This is the main search reduction: factor blocks are
enumerated, but terminal primes are solved rather than scanned.

The exact per-pair stops are:

1. If `D_K != 0`, reject unless `N_K/D_K` is a positive integer.  Then reject
   unless `q` is a positive integer, both terminal values are prime and
   coprime to their blocks, the representation is canonical, the value is in
   the declared band, and (4) holds.
2. If `D_K = 0` but `N_K != 0`, reject the pair identically.
3. If `D_K = N_K = 0`, apply (4).  A nonzero coefficient again gives at most
   one `p`; a zero coefficient with a nonzero constant rejects the entire
   line; only zero coefficient and zero constant define a genuinely
   parametric block line.

These are algebraic stops, not heuristic score cutoffs.

## The common-block wall is theorem-blocked

If `A=B`, the product translation requires

```text
q-p = 12/A.
```

There is no integral line unless `A` divides `12`.  On every integral line
with `A>1`, multiplicativity gives

```text
R_phi   = 12(phi(A)/A - 1) < 0,
R_sigma = 12(sigma(A)/A - 1) > 0.                          (5)
```

Neither residual can vanish because `phi(A)<A<sigma(A)` for `A>1`.
Consequently every same-block translation is theorem-blocked.  In particular,
`A=6` makes (5) exactly `(-8,12)` and `Delta K=4` for every admissible
`p`; the wall cannot be crossed by searching more primes `p,p+2`.

The cheapest asymmetric one-block checks retain one copy of `6`.  Since
`k_6=2` and `h_6=10`, they reduce to

```text
A=6:  p = [B(h_B-10) + 12 k_B] / [2B - 6k_B],             (6)
B=6:  p = [6(10-h_A) + 24] / [6k_A - 2A].                 (7)
```

Equations (6)--(7), followed by the stops above, are the exact one-off grid.
They are cheap but low-likelihood: a large terminal prime requires a rigid
near-cancellation in the denominator.

## Ranked disjoint grids

All grids use the frozen value band

```text
L = 10^12 + 1,   U = 10^14.
```

They must skip every lower-endpoint coordinate already belonging to a frozen
`REPEATED_POWER_SURGERY`, `SQUAREFREE_THREE_BLOCK`, or `PURE_PRIME_POWER`
tuple stream.  Direction and endpoint exponent signature are part of a
coordinate, so the grids below are mutually disjoint.

### 1. Mixed repeated-square / squarefree-triple resonance

This is the highest-priority genuine shape change.  Let

```text
n = r^2 p,
m = t u q,
T = t+u,
Q = tu,
```

for primes `r,t,u`.  Since

```text
K(r^2 p) = p + 2r + 1,
K(tu q)  = 2(q+t+u),
```

the candidate is forced to be

```text
p = [24 + Q(2T-2r-1)] / [Q-2r^2],
q = (p+2r+1-2T)/2.                                      (8)
```

The remaining exact equality is

```text
r p + r(r-1) = (T-1)q + (Q-T+1).                         (9)
```

Large `p` in (8) occurs only near the resonance `Q=2r^2`; denominator sign,
divisibility, primality, canonical ordering, band membership, and (9) are
hard stops.

The reverse direction

```text
n = tu p,
m = r^2 q
```

has

```text
p = [12 + r^2(2r+1-2T)] / [2r^2-Q],
q = 2p + 2T - 2r - 1,                                   (10)
```

followed by the reversed version of (9).

Concrete pilot grid:

```text
r: prime ranks 385..640,
t,u: prime ranks 1..640 with t<u,
orientation: repeated lower or repeated upper.
```

The lower repeated-prime rank begins after the frozen ranks `1..384`.
Implementations should index semiprime blocks `Q` and use the band-implied
denominator window around `2r^2`, rather than factor arbitrary translated
integers.  Extend `r` by consecutive blocks of 256 ranks only when the prior
block has survivors after integrality and `K` filtering.  Two consecutive
rank blocks with no such survivors stop this lane as a bounded development
rule, not as a theorem.

### 2. Squarefree triple / squarefree triple sum-neighbor surgery

This preserves the factor shape of the observed point while separating its
common `6` block.  Put

```text
P = rs,   R = r+s,
Q = tu,   T = t+u,
d = T-R.
```

For

```text
n = rs p,
m = tu q,
```

the simultaneous `C` and `K` equalities force

```text
p = T + (P-Q)/d,
q = R + (P-Q)/d,                                         (11)
```

and the product gap is exactly the block identity

```text
d(QR-PT-12) = (Q-P)^2.                                   (12)
```

If `d=0`, the product equation leaves only tiny divisors and is a hard stop
in the target band.  Otherwise (11)--(12), positivity, divisibility,
primality, canonical ordering `r<s<p`, `t<u<q`, and band membership are a
complete exact test.  Also

```text
gcd(n,n+12) divides 12,
```

so a prime greater than `3` shared across endpoints is an immediate reject.
The common pair block `rs=tu` is already covered by the common-block theorem.

Concrete pilot grid:

```text
r,s,t,u: prime ranks 97..1024,
1 <= |(t+u)-(r+s)| <= 64,
both ordered orientations.
```

Starting after rank 96 makes every lower triple disjoint from the frozen
smallest-prime ranks `1..96`.  Index pairs by their sum and extend the
sum-difference shells dyadically to `65..128`, then `129..256`, only when the
previous shell has exact-identity survivors.  A zero-survivor shell stops
only that declared shell sequence.

### 3. Exponent-asymmetric power / triple surgery

Replace `r^2` in grid 1 by `r^e`, for `e=3,4,5,6`.  The needed block terms are

```text
k_(r^e) = 1+r+...+r^(e-2),
h_(r^e) = sigma(r^e)-phi(r^e).
```

Use (2)--(4) with `A=r^e`, `B=tu`, and both orientations.  The concrete grid
is

```text
r: prime ranks 385..640,
e: 3..6,
t,u: prime ranks 1..640 with t<u.
```

It is disjoint from grid 1 by exponent and from the frozen repeated-power
coordinates by base rank, subject also to the explicit frozen-coordinate
skip.

### 4. Power / power surgery

Use

```text
A=r^e, B=s^f,
e,f in 2..6,
r,s: prime ranks 385..2048,
(e,r) != (f,s),
```

with ordered direction and (2)--(4).  Test `e!=f` first.  For the least
promising square/square subcase, `e=f=2`, `K` equality gives

```text
q-p = 2(r-s),
p = [12-2s^2(r-s)] / [s^2-r^2].                          (13)
```

Formula (13) normally keeps terminal size on the scale of the bases rather
than producing an unbalanced `6p`-like escape, hence its lower rank.

### 5. Higher composite blocks

Only after a preceding grid produces post-`K` survivors, enumerate blocks
such as `r^2s` and `rst` on either endpoint using (2)--(4).  Partition the
grid by the ordered pair of endpoint exponent multisets, for example
`((2,1),(1,1,1))`, so no coordinate belongs to more than one lane.  No
unbounded shape expansion is licensed by an empty lower grid.

## Bounded diagnostic

Two read-only local diagnostics enumerated ordered fixed blocks
`2 <= A,B <= 5000`, solved the exact block equations, and then applied
terminal primality checks.  The first run took approximately 27 seconds and
reported 1,459 algebraic exact pairs.  A second, narrower classification run
took approximately 13 seconds and found:

```text
prime terminal p and q with composite A or composite B: 0.
```

Every prime-terminal hit in that cap had prime `A` and prime `B`, hence was a
known prime-quadruple semiprime represented by choosing one endpoint prime as
the block and the other as the terminal prime.

This is only a development diagnostic.  The exploratory commands did not
emit a durable tuple certificate, and this report therefore does not include
a verifier or claim independently replayable exhaustion.  In particular,
the result is not a theorem beyond `A,B<=5000`, does not cover large or
parametric block pairs, and does not justify stopping the ranked grids above.

## Claim discipline and terminal rules

- Use `Delta K` first.  After it vanishes, test only one signed residual and
  derive the other from `R_phi+R_sigma=0`.
- Require canonical terminal primes larger than every prime in their blocks;
  otherwise the same integer receives multiple block coordinates.
- Skip squarefree-semiprime endpoints and prime-square endpoints using the
  existing exact `K=2` and `K=1` theorem shadows.
- Skip every coordinate in the frozen development tuple streams; this note
  does not amend or rerun those streams.
- A denominator, divisibility, sign, primality, shared-factor, identity, or
  band failure is an exact candidate stop.
- A rank, exponent, orientation, or sum-difference shell may report only
  exhaustion of that declared finite tuple grid.  It may not report interval
  exhaustion, exhaustion of a broad factor-shape stratum, or a proof of the
  A056777 conjecture.
