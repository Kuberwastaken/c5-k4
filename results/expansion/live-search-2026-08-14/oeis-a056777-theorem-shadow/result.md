# A056777 theorem shadow: the partner-escape arm is empty

**Status:** exact mathematical reduction, with a finite grid audit
**Scope:** OEIS A056777 development above `10^12`; no search, candidate,
novelty claim, or publication action is recorded here.

Let

```text
C(x) = x - phi(x),
S(x) = sigma(x) - x,
K(x) = S(x) - C(x) = sigma(x) + phi(x) - 2x.
```

For `m=n+12`, the two A056777 equalities are exactly

```text
phi(m) - phi(n) - 12   = C(n) - C(m),
sigma(m) - sigma(n) - 12 = S(m) - S(n).
```

Thus a solution has `C(m)=C(n)`, `S(m)=S(n)`, and in particular
`K(m)=K(n)`.  The last equality is a strong factor-shape filter, not merely a
numerical score.

## Exact characterization of the small K levels

For coprime `a,b>1`, multiplicativity of `phi` and `sigma` gives

```text
S(ab) = a S(b) + b S(a) + S(a)S(b),
C(ab) = a C(b) + b C(a) - C(a)C(b),
K(ab) = a K(b) + b K(a) + S(a)S(b) + C(a)C(b).       (1)
```

For a prime power,

```text
S(p^e) = 1+p+...+p^(e-1),
C(p^e) = p^(e-1),
K(p)   = 0,
K(p^e) = 1+p+...+p^(e-2)  for e>=2.                  (2)
```

Factor any integer `x>1` into its pairwise-coprime prime-power blocks.
With one block, (2) says that `K` is `0` for a prime, `1` for a prime
square, and at least `3` for exponent at least three.  With two blocks, (1)
is `2` when both blocks are primes, because then `S=C=1` and both block
`K` values vanish.  If either block is powered, its positive `K`, multiplied
by the other block, together with the two positive cross terms in (1), makes
the result at least `4`.  With at least three blocks, first combine any two:
their `K` is at least `2`; adjoining the third block makes the first term in
(1) alone at least `4`, and all other terms are nonnegative.

Consequently, for every integer `x>1`,

```text
K(x)=1  iff  x=p^2 for a prime p;
K(x)=2  iff  x=pq for two distinct primes p,q.
```

This accounts for all prime powers and all numbers of distinct prime
factors; it is not a bounded computational observation.

## Semiprime-partner impossibility

If `n=pq` is a squarefree semiprime, then `K(n)=2`.  Both A056777 equalities
together force `K(n+12)=2`, so the characterization above forces `n+12`
to be a squarefree semiprime too.  Therefore the proposed domain

```text
n squarefree semiprime, n+12 not squarefree semiprime
```

is globally empty.  It must be theorem-pruned rather than assigned search
shards.

For completeness, write `n=pq`, `n+12=rs`, with each pair increasing.  The
`C` (equivalently `S`) equality gives `p+q=r+s`.  If `g=q-p` and `h=s-r`,
the product difference gives

```text
g^2-h^2=48.
```

The positive integral possibilities are `(g,h)=(13,11),(8,4),(7,1)`.
An odd prime gap forces one endpoint to be `2`; the gap-13 and gap-7 cases
then end at `15` and `9`.  The even case yields
`(p,q,r,s)=(p,p+8,p+2,p+6)`, exactly the prime-quadruple family.  Hence the
entire squarefree-semiprime lower-endpoint stratum is theorem-locked.

## Prime-square pruning

If `n=p^2`, then `K(n)=1`, so a solution would have `n+12=q^2` for a prime
`q`.  But

```text
(q-p)(q+p)=12.
```

The only positive same-parity factor pair is `(2,6)`, giving `(p,q)=(2,4)`,
not two primes.  Thus prime squares can also be pruned globally without
enumerating the roughly half-million bases in the numerical band.

## Replacement finite arm: PURE_PRIME_POWER

Use the value band

```text
L = 10^12 + 1,   U = 10^14.
```

Declare the finite domain to be every `n=p^e` in `[L,U]`, with `p` prime and
`e>=2`.  The exponent-two part is exhausted by the proof above.  Since
`2^47>U`, the computational tuples are exactly

```text
e = 3,...,46,
ceil_root(L,e) <= p <= floor_root(U,e),
p prime.
```

Order tuples lexicographically by `(e,p)`.  Give global zero-based ordinal
`j` to shard `j mod 24`.  This is canonical, duplicate-free, and balanced:
there are 3,970 computational tuples, hence 165 or 166 per shard.  Construct
`n` from the tuple, factor only `n+12`, and retain a row only after every
factor is proved prime and its product is checked.  A replay ledger should
record `(e,p)`, the global ordinal, the complete factorization of `n+12`, the
two signed residuals, and the strict best-so-far key

```text
(max(abs(R_phi),abs(R_sigma)),
 abs(R_phi)+abs(R_sigma),
 abs(K(n+12)-K(n)), n).
```

The accompanying certificate fixes the per-exponent counts and SHA-256 of
the canonical tuple stream.  `verify.py` rebuilds the prime sieve and roots
independently and checks all 3,970 tuples.

## Lean status

[`lean/FactorDefect.lean`](lean/FactorDefect.lean) is a warning-clean,
no-`sorry` formalization of the complete algebraic theorem shadow. It proves
defect preservation from both A056777 equalities, the coprime-product defect
recurrence, the exact prime-power formula, and the full small-defect
classification. In particular, it proves both converse characterizations:
`K(x)=2` forces a product of two distinct primes, while `K(x)=1` forces a
prime square. Its axiom audit uses only standard Lean/mathlib foundations.

## Limitations

The theorem completely removes the semiprime/non-semiprime partner arm and
the prime-square slice.  The replacement grid completely exhausts pure prime
powers only in the declared value band.  It does **not** exhaust general
nonsquarefree integers: shapes such as `p^e q`, `p^e q^f`, or shapes with
three or more distinct prime factors remain outside it.  Likewise an
exactly-three-prime squarefree grid does not cover squarefree integers with
four or more prime factors.  No terminal record for one of these slices may
be described as exhaustion of an entire A056777 escape stratum or of the
integer interval.
