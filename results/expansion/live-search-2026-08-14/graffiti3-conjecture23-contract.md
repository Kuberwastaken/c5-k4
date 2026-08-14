# Graffiti³ Conjecture 23: frozen DEVELOPMENT contract

**Frozen before evaluating any order-256/order-512 group or wall lift.**

This campaign tests the DOI-qualified statement and literal integer residual
specified in [`graffiti3-conjecture23-source-status.md`](graffiti3-conjecture23-source-status.md).
It is adaptive DEVELOPMENT evidence, not a held-out benchmark.

## Equality wall and prospective coordinate

Every extraspecial 2-group of order `2^(1+2r)` has

```text
|G'| = |Z(G)| = 2,
|G/G'| = 2^(2r),
k(G) = 2^(2r) + 1,
W(G) = 0.
```

After division by `|G|`, the wall is

```text
W(G)/|G| = 1 + 2/|G'| + 2|Z(G)|/|G| - 4 cp(G).
```

The frozen directional prediction is: lifting the commutator image from order
2 to order 4 decreases `2/|G'|` by `1/2`; a sparse lift can cross if it retains
enough of the extraspecial commuting probability without increasing the center
proportion comparably. No different wall is substituted after seeing results.

## Mandatory database-sanity gate

Before any development row, a dedicated preparation job must:

1. enumerate the trivial group and every SmallGroup whose order is a prime
   power at most 128, exactly 2,732 rows in total;
2. compute `W` literally and find no negative source-snapshot row;
3. recover exact equality on `D8=SmallGroup(8,3)` and `Q8=SmallGroup(8,4)`;
4. partition the frozen coordinate sequence into 96 consecutive chunks, with
   every individual GAP query still capped at four seconds;
5. content-address every chunk, the full coordinate domain, all residual rows,
   the source and manifest, and the exact campaign commit in one preparation;
6. upload that preparation once for reuse by all 72 target workers.

A timeout, missing GAP package, malformed marker, source mismatch, or failed
control prevents preparation and therefore prevents every target worker from
starting. Each worker independently verifies the downloaded artifact checksum,
its internal content hash, complete ordered 2,732-row coverage, all 96 chunk
bindings, the zero-negative result, both equality controls, the source digest,
the manifest digest, and its campaign commit before evaluating a target row.
A missing, partial, reordered, stale, or tampered preparation ends that worker
as `SANITY_GATE_FAILED` and admits zero target rows.

The pre-correction run
[`31794768947`](https://github.com/Kuberwastaken/c5-k4/actions/runs/31794768947)
repeated one monolithic gate in every worker and produced no `@@GATE@@` marker;
all affected workers stopped with zero proposals. It is `INVALID_RUN`
preparation evidence and carries no mathematical inference.

## Three frozen arms

All arms use 24 immutable shards. Every worker has an internal 54-second
deadline inside an external process-group cap of 60 seconds. Every GAP query
is separately capped at four seconds and a timed-out proposal is durably
recorded without mathematical inference.

### `CATALOGUE`

The 56,092 GAP `SmallGroup(256,id)` coordinates are split into 24 contiguous,
disjoint intervals by the standard quotient/remainder partition. Each shard
visits its complete interval in increasing id order until exhaustion or its
deadline. Order 256 is the first full 2-group catalogue layer beyond the
source's order-128 snapshot.

### `GENERIC`

Each shard generates candidate ids for `SmallGroup(512,id)`, where GAP has
10,494,213 groups, by hashing
`graffiti3-c23-generic-v1:shard:cursor`, reducing the digest modulo the group
count, and rejecting repeats. It is target-blind and deterministic. Each
shard stops at 4,096 proposals or the deadline.

### `WALL_NAVIGATION`

The wall arm constructs class-two central extensions on
`V x W = F2^d x F2^2` with multiplication

```text
(v,z)(v',z') = (v+v', z+z'+f(v,v')).
```

For `d in {6,8}`, begin with the standard symplectic-pair upper-triangular
cocycle. Assign each pair commutator one of the three nonzero vectors of
`F2^2`, require the assignments to span `F2^2`, and partition the complete
assignment domain by SHA-256 modulo 24. These are the frozen sparse
commutator-image lifts. The evaluator obtains `|G'|`, `|Z|`, `|G/G'|`, and
`k(G)` exactly from binary ranks; no floating point or heuristic proxy enters
the residual.

## Durable evidence and terminal rules

Every proposal appends a canonical-JSON row to a fresh SHA-256 hash chain,
then flushes and `fsync`s it. The terminal receipt binds its final row hash,
ledger SHA-256, counters, campaign commit, arm, and shard. Allowed terminals:

- `DOMAIN_EXHAUSTED`;
- `PROPOSAL_LIMIT`;
- `DEADLINE_PREFIX`;
- `CERTIFICATE_FOUND`;
- `SANITY_GATE_FAILED`;
- `WORKER_ERROR`.

A strict negative residual is only a candidate. The worker must serialize a
complete Cayley table and profile into the certificate, and the independent
standard-library verifier must reconstruct the group law, center, derived
subgroup, abelianization order, conjugacy classes, prime-power premise, and
strict integer inequality. Failure to produce that certificate is not a
crossing.

No workflow writes repository contents, opens an issue or pull request,
creates a tag, or publishes a release. Dispatch is manual and requires an
exact 40-hex commit with a clean checkout.
