# Graffiti³ energy Conjecture 3: frozen DEVELOPMENT contract

Status: **FROZEN, UNRUN**

Freeze date: 2026-08-14 UTC

Source/status authority:
[`graffiti3-energy-c3-source-status.md`](graffiti3-energy-c3-source-status.md).

## Resolution card

```json
{
  "logical_class": "FINITE_UNIVERSAL",
  "target_negation": "one finite applicable graph has rounded energy below the literal closed-d2 radical sum",
  "negation_certificate": "labelled graph, planar embedding, diameter paths, d2 table, characteristic polynomial, Sturm root intervals, rational radical intervals",
  "finite_witness_suffices": true,
  "answer_placeholder": false,
  "eventual_quantifier": false,
  "global_constant_quantifier": false,
  "unbounded_auxiliary_search": false
}
```

For the only admitted reading,

```text
R(G) = round(Energy(G))
       - 3*sum_{uv in E(G)} 1/sqrt(d2_closed(u)*d2_closed(v)).
```

A candidate requires `R(G)<0`. The center-excluding implementation reading is
computed for audit only and can never trigger a candidate.

## Equality-recovery and sanity gate

Before any target row, every worker must:

1. hash-check the immutable 335-row source CSV;
2. recover its 97 eligible rows, zero scalar violations, and exactly the nine
   implementation-equality ids frozen in the source attestation;
3. enumerate exactly 995 connected Graph Atlas graphs of orders 2--7;
4. confirm zero literal closed-ball violations and zero literal equalities;
5. recover `K2` (`A_`) and `K3` (`Bw`) as the two center-excluding violations.

Any mismatch is `DB_GATE_FAILED`. The source equalities do not migrate across
readings. The literal wall begins from least-positive-slack controls, with
`K2` at gap `1/2`, rather than inventing an equality.

## Frozen wall geometry

For diameter-two graphs, `d2_closed(v)=n` and the right side collapses to
`3m/n`. Moving to diameter three can make selected closed radius-two balls
smaller, raising reciprocal edge terms. Low-rank planar false-twin additions
can simultaneously add zero eigenvalues or keep the energy inside its current
nearest-integer shelf. The prospective sign table is:

| coordinate | predicted move |
|---|---|
| connected, planar | preserved by embedded book/2-tree constructions |
| diameter | two to at most three |
| selected `d2_closed` values | decrease relative to order |
| radical right side | increase |
| exact energy | unknown, but screened for a pinned rounding shelf |
| literal residual | decrease |

The prediction is developmental: the literal reading has a least-slack wall,
not a recovered equality wall.

## Frozen arms

Every arm is deterministic, internally capped at 54 seconds, externally killed
at 60 seconds, exact-serialization-deduplicated by graph6, and incrementally writes a
SHA-256 chained `fsync` ledger plus a separately hashed terminal receipt.

1. `CATALOGUE`: paths, cycles, stars, wheels, ladders, double stars, planar
   books, and two-book chains, orders 8--32. This deliberately narrow named
   catalogue replaces an impractical all-planar order-10 enumeration under the
   60-second cap.
2. `GENERIC`: 1,800 fixed-seed Apollonian planar graphs of orders 8--32 with a
   deterministic unguided edge-deletion quota. No target residual affects
   construction or order.
3. `WALL_NAVIGATION`: the fixed two-book-chain false-twin quotient family
   through order 36, plus fixed book and double-star extensions of source
   equality shapes. The family is frozen despite the source equalities being
   rejected-reading calibration only.

No constructor, size, seed, score, or reading may be added after observing a
target value. An incomplete arm is `DEADLINE_PREFIX`, never exhaustion.

## Exact-enough candidate gate

Floating eigensolvers only screen rows with a `1e-7` strict margin. A row can
become `CANDIDATE_ONLY` only after it stores and independently replays:

- a labelled edge list and graph6 checksum;
- connectivity, a combinatorial planar rotation, and a path of length at most
  three for every vertex pair;
- both closed and center-excluding `d2` tables;
- the integer adjacency characteristic polynomial;
- rational Sturm-isolating intervals for every eigenvalue, with multiplicity;
- a rational energy interval strictly inside `(k-1/2,k+1/2)`;
- outward 96-bit dyadic bounds for every radical term;
- a rational lower bound proving the literal right side is strictly above `k`.

The independent verifier reconstructs the graph, checks the graph6 checksum
and complete unordered-pair path coverage, recomputes and exactly compares
every stored Sturm/energy and radical interval and term, and binds the exact
candidate bytes to the ledger row's `certificate_sha256`.

Avoiding both shelf boundaries makes half-up and ties-to-even agree. A numeric
crossing without this certificate is `NO_CERTIFIED_CROSSING`.

## Output discipline

The workflow is manual, read-only, and accepts only an exact 40-hex commit. It
checks out that commit cleanly, runs constructor/control-only tests and the freeze
verifier, fetches the immutable source CSV, then runs one arm per isolated job.
Any candidate is verified in the same invocation as its terminal and chained
ledger so the three artifacts cannot pass independently while disagreeing.
No README update, release, issue, PR, or public count follows automatically.
