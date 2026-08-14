# A231201 theorem shadow: finite prime assignments never cover all exponents

Date: 2026-08-14 UTC

Classification: proved structural stop for the frozen finite-prime mechanism;
not an A231201 counterexample, conjecture resolution, held-out result, release,
or authorization for upstream action

## Result

Let `P` be the exact frozen set of the 55 primes at most 257.  For every
selection of one residue `a_q (mod q)` for each `q in P`, there are infinitely
many positive integers `x` such that

```text
x - 2^x != a_q (mod q)  for every q in P.
```

More precisely, modulo the frozen combined period

```text
249728679334046128590697275594786190851950664265138725258656853072581268625525551538208526056090039506543200
```

every assignment leaves exactly

```text
24963582149641753219210436584574955917125360656305982149531359816631810495288659339640832000000000000000000
```

avoiding residue classes.  The count is assignment-independent.

Therefore `COMPLETE_PERIODIC_COVER` is structurally impossible for this exact
55-prime universe.  This does **not** imply that a finite interval
`1 <= x < n` cannot be covered: every avoiding class may have least-positive
representative at least `n`.  A231201 remains open, and a bounded-minimum
escape computation remains meaningful if it is compared with a constructed
candidate `n`.

## Correction to the scout's proposed condition

The sufficient condition suggested in the v3 design scout,

```text
ord_q(2) | lcm_{p<q}(p * ord_p(2)),
```

is false.  Its first failure is `q=5`, where `ord_5(2)=4` and the old modulus
is 6.  In the frozen list it also fails at

```text
5, 17, 19, 97, 101, 163, 193, 197.
```

The conclusion nevertheless follows from a stronger lift argument that does
not require this divisibility.

## Universal lift lemma

Suppose an avoiding class `r (mod M)` has been constructed for the earlier
primes, and let `q` be the next prime.  Put

```text
o = ord_q(2),  g = gcd(M,o),  d = o/g,
L = lcm(M,q*o) = M*q*d.
```

For ascending primes, `q` does not divide `M`: every factor of an earlier
`p*ord_p(2)` is less than `q`.  Consequently `d*M` is invertible modulo `q`.

The `q*d` lifts of `r (mod M)` to classes modulo `L` are represented by

```text
r + t*M,  0 <= t < q*d.
```

They split into `d` exponent fibers.  In one fiber write
`t=t_0+k*d`, `0<=k<q`.  Since `o` divides `d*M`, all `q` lifts have the same
exponent modulo `o`, hence the same value of `2^x (mod q)`.  Their `x (mod q)`
coordinates are all different because the step `d*M` is invertible modulo
`q`.  They therefore attain every value of `x-2^x (mod q)` exactly once.
Exactly one lift in the fiber equals the assigned `a_q`; the other `q-1`
avoid it.  Thus every old avoiding class has exactly `d*(q-1)` avoiding lifts.

The base `q=2` uses the frozen positive-exponent convention `o_2=1`.
For positive `x`, `2^x=0 (mod 2)`, so `x-2^x` is just the parity of `x`.
Exactly one of the two parity lifts is forbidden and the other survives.  No
evaluation at the out-of-domain exponent zero is used.

Induction through all 55 primes proves nonemptiness and the exact product
count above.  Each surviving class modulo the positive combined period has
infinitely many positive representatives, proving the stated result.

A deterministic constructor is immediate: at each odd prime inspect the
single fiber `t=k*d`, `k=0,...,q-1`, and take the least `k` whose lift avoids
`a_q`; at `q=2`, take the unassigned positive parity.  This requires at most
`sum(q)` small checks rather than enumeration of the combined period.

## Exact finite certificate

[`divisibility-certificate.json`](divisibility-certificate.json) records, for
all 55 frozen primes, `o`, the old and new moduli, `g`, `d`, the lift count,
the exact survivors per old class, and the status of the scout's simpler
condition.  Its SHA-256 is
`7d3a3a5135346529813b8c0613260664cfb35d17dc99e02bfd5b43a7bd72e6e7`.

[`verify.py`](verify.py) independently recomputes every multiplicative order,
LCM, fresh-coordinate condition, exponent-fiber size, full `Z/qZ` traversal,
combined period, and survivor product from the frozen manifest.  It also
exercises the deterministic least-lift constructor on two fixed assignment
families, using least-positive representatives.  Its SHA-256 at the time of
this report is
`478252e98940d9436cdb012ed3cbc389eeee7277cb823e677a79985aad751c6d`.

The source manifest is
[`../oeis-a231201-development/manifest.json`](../oeis-a231201-development/manifest.json),
SHA-256
`bed3cb25993017d044ecb8559a7f84125479f171ad1e1ff4057c4026f3614f2b`.

Replay command, externally capped at 60 seconds:

```bash
timeout --signal=TERM --kill-after=6s 60s \
  python3 results/expansion/live-search-2026-08-14/oeis-a231201-periodic-cover-theorem-shadow/verify.py
```

Observed replay: 0.04 seconds wall time and 15,800 KiB maximum RSS.  No target
assignment search, ILP, candidate construction, primality scan, workflow, or
network access was performed.

## Lean status and remaining plan

[`lean/PeriodicCoverLift.lean`](lean/PeriodicCoverLift.lean) gives a
warning-clean, no-`sorry` formalization of the generic fiber-selection core.
It proves that a nonconstant affine `Fin q -> ZMod q` fiber avoids any one
forbidden residue, packages the selected natural lift while preserving its
old congruence, specializes this to odd primes, and proves the abstract
finite-list extension induction. It was checked with
`-DwarningAsError=true`; its axiom audit contains no `sorryAx`.

This is deliberately not labeled a complete Lean proof of the 55-prime
theorem. The remaining bridge must formalize that `d*M` fixes the
power-of-two term throughout each fiber, prove its nonzero residue modulo the
fresh prime, and instantiate the list induction with the ascending frozen
prime table. The clean completion path is:

1. Work in `ZMod q` for an odd prime `q`.  Assume `q` does not divide `M`, set
   `o := orderOf (2 : ZMod q)` and `d := o / gcd M o`, and prove
   `o | d*M` using the standard gcd quotient lemma.
2. For a prior natural representative `r` and assigned residue `a : ZMod q`,
   consider `r+k*d*M`, `k : Fin q`.  `pow_eq_pow_mod_orderOf` (or the
   corresponding `orderOf` divisibility lemma) makes the power-of-two term
   constant over this fiber.  Multiplication by the unit `d*M` permutes
   `ZMod q`; hence at most one `k` is forbidden.  Since odd prime `q` has at
   least three elements, construct a different `k` (equivalently solve for
   the forbidden `k` using the field inverse and add one).  This yields a lift
   preserving `r (mod M)` and avoiding `a`.
3. Prove the `q=2` positive-exponent base separately from parity, explicitly
   avoiding `2^0 mod 2`.
4. State an induction over an ascending list of primes whose current modulus
   is the LCM of `p*o_p`.  The finite side conditions for the frozen 55-prime
   list—primality, strict ordering, orders, fresh coordinates, and final
   combined period—can be discharged by `native_decide`/`norm_num` against a
   literal certificate table.
5. Conclude that for every residue assignment there is a residue `r` modulo
   the frozen combined period avoiding all 55 predicates.  Map `r=0` to the
   positive representative `L`; then `r+j*L` supplies infinitely many
   positive exponents.

For an exact-count corollary, strengthen step 2 from one chosen fiber to the
equivalence between the `q*d` lifts and `Fin d x Fin q`; each fiber loses
exactly one member.  The existential theorem is substantially shorter and is
the right first no-sorry milestone.  Neither theorem alone proves or disproves
A231201, because its finite interval may end before the first avoiding
representative.
