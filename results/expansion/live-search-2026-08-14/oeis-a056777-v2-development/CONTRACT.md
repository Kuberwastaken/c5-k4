# OEIS A056777 v2 DEVELOPMENT surgery contract

This is a contaminated, duplicate-aware development lane, not a benchmark
sample, novelty claim, proof, disproof, interval exhaustion, or publication
path. It inherits the exact source/table boundary and exclusion registry from
the frozen v1 lane, re-attests them in this freeze, and evaluates no target
before the freeze is immutable.

## Frozen algebraic domain

Only Rank 1 `MIXED_RESONANT_SQUARE_TRIPLE` is owned. For prime ranks
`385 <= r_rank <= 640` and `1 <= t_rank < u_rank <= 640`, both ordered
orientations are searched in the band `10^12+1 <= n < n+12 <= 10^14+12`:

* `REPEATED_LOWER`: `n=r^2 p`, `n+12=t u q`;
* `REPEATED_UPPER`: `n=t u p`, `n+12=r^2 q`.

Put `T=t+u` and `Q=tu`. The runner solves, without a flat `n` scan or
factorization search,

```text
REPEATED_LOWER:
  p = [24 + Q(2T-2r-1)] / [Q-2r^2]                 (8)
  q = (p+2r+1-2T)/2
  r p+r(r-1) = (T-1)q+(Q-T+1)                      (9)

REPEATED_UPPER:
  p = [12+r^2(2r+1-2T)] / [2r^2-Q]                (10)
  q = 2p+2T-2r-1
  (T-1)p+(Q-T+1) = r q+r(r-1).              (9 reversed)
```

The first 640 primes are used to build one sorted semiprime-block index
`(Q,t_rank,u_rank)`. Each `r` consults it only through a conservative,
band-implied denominator window about `Q=2r^2`, then applies exact stops for
zero denominator, `K` numerator divisibility/sign, partner integrality,
product translation, canonical order, lower-band membership, deterministic
64-bit primality, and the `C` identity. Candidate factor products are known
from their tuple coordinates; arbitrary translated integers are never
factored.

Coordinates include orientation and both endpoint exponent signatures. They
are canonical (`r<p`, `t<u<q` or `t<u<p`, `r<q`) and cannot collide across
orientations. `r_rank>=385` makes `REPEATED_LOWER` disjoint from the v1
repeated-power base ranks. `REPEATED_UPPER` performs an exact coordinate skip
for every v1 `SQUAREFREE_THREE_BLOCK` tuple; the pure-prime-power v1 domain is
shape-disjoint. A skipped prior coordinate is recorded as a stop, never
evaluated as a target.

Shards own `r_rank-385 modulo 24`. `DOMAIN_EXHAUSTED` means only exhaustion of
one arm/shard tuple domain. It does not activate later grids or imply a theorem.

## Evidence and failure rules

Search stops internally at 48 seconds, its shell cap is 54 seconds, and the
independent verifier cap is 60 seconds. Every progress checkpoint is canonical
JSON in an incremental SHA-256 predecessor chain and is flushed and fsynced.
The terminal binds its exact row count, final row hash, and ledger hash.
The independent reader treats the ledger as raw bytes: it must be nonempty
ASCII ending exactly in a newline, every physical row must have the exact
progress/chain key set, and every row must byte-match the runner's canonical
serialization including `row_sha256`. The terminal likewise has an exact key
set; whitespace variants, partial rows, missing final newlines, and extra keys
fail closed.
Once a certificate is atomically renamed, the runner never appends to the
ledger again. The certificate is the final state commit; the terminal records
its final tuple/count state, and the verifier replays the preceding durable
ledger prefix followed by that independently checked certificate. It also
requires the certificate coordinate to equal the terminal's last coordinate,
the last outcome to be `SURVIVOR`, and the first survivor to occur at exactly
`visited-1`, proving that the runner stopped immediately.

The verifier separately implements the prime sieve, Miller--Rabin test,
semiprime index/window construction, formulas, prior-domain test, exact stop
order, prefix replay, and candidate arithmetic. It does not call the runner's
enumerator or algebra routines.

`SIGALRM` is blocked around each complete state/checkpoint/certificate
transition and each atomic terminal write. Temporary files use exclusive
creation, file fsync, atomic rename, and parent-directory fsync. An unexpected
exception becomes `WORKER_ERROR` with a typed, hashed message and nonzero exit;
it is never mislabeled as a deadline. Certificate-write failure leaves the
previous committed prefix authoritative. There is no post-certificate ledger
checkpoint and therefore no late append/fsync ambiguity after candidate state
becomes durable.
The workflow has manual dispatch
only, read permissions, immutable commit checkout, always-upload evidence, and
no release, issue, PR, README, repository-dispatch, or upstream mutation step.
