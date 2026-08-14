# OEIS A063880 DEVELOPMENT freeze

This directory freezes a prospective, target-specific search. It is not a
result, novelty claim, release, or authorization to dispatch the workflow.

## Exact target and historical boundary

At `google-deepmind/formal-conjectures@942fb149e...`, both
`OeisA63880.mod_216_of_a` and `OeisA63880.unique_primitive_108` remain
`research open`.  Write

`R(p,e) = (1+p+...+p^e)/(1+p^e)`.

For `n=prod p^e`, multiplicativity gives `sigma(n)/usigma(n)=prod R(p,e)`.
Exponent-one primes contribute one, so deleting them gives the exact powerful
primitive core. The worker searches powerful cores with exact rational product
two; it does not scan integers and hope that factoring volume finds a hit.

The locked OEIS source says that 108 is the only primitive term below
`10^18`. Therefore **every core strictly below `10^18` is a historical exclusion**,
not a claimable discovery. The source does not cover equality, so the frozen
universe begins at exactly `10^18`. The source
also reports the residue observation checked through `10^7`; the 10,000-row
b-file is independently replayed by the preparation gate.

## Finite meet-in-the-middle universe

Each arm selects zero or one frozen exponent for each frozen prime, splits its
prime list in half, enumerates both halves deterministically, and exact-matches
right-hand rational products against `2/left`. Products must lie in
`[10^18,10^36]`, use at least two prime factors, and respect the arm's factor
cap. Arms are disjoint by the largest prime in the core:

* `CATALOGUE`: largest prime at most 29; exponents 2..12; at most 4 factors.
* `GENERIC`: largest prime 31..43; exponents 2..8; at most 5 factors.
* `WALL_NAVIGATION`: largest prime 47..71; exponents 2..6; at most 6 factors.

This bounded universe is not all powerful numbers. `DOMAIN_EXHAUSTED` means
only that one frozen arm/shard finished this exact universe. A deadline records
`DEADLINE_PREFIX`; it cannot be upgraded to exhaustion. Left states are
assigned by deterministic ordinal modulo 24. Euler factors are traversed in
decreasing exact value so the wall arm preferentially explores products around
two, while certificate acceptance remains exact.

## Certificate and execution discipline

A certificate contains a canonical prime-power factorization. An independent
replay reconstructs `n`, `sigma`, `usigma`, the exact Euler-factor product,
the primitive-core reduction, every proper-divisor ratio needed for
primitivity, and both target conclusions. A witness is emitted only if it
disproves at least one named declaration and is outside the historical
exclusion. Search and verifier do not share the candidate arithmetic routine.

The source gate locks the Lean module, OEIS source record, and 10,000-row
b-file. Forty independently capped child chunks check contiguous table rows,
factor every term, verify `sigma=2*usigma`, residue 108 modulo 216, and reduction
to core 108. Every search row is hash-chained and fsynced. Workers have a
54-second internal deadline inside a 60-second external cap; each preparation
child has a four-second cap. Terminal receipts bind exact commit, source gate,
ordered-domain counters, final row hash, and ledger hash. Shell postprocessing
records and propagates every gate, search, verifier, terminal, status, and
checksum failure.
