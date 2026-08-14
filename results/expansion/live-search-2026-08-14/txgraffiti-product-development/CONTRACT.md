# TxGraffiti Conjecture 3: frozen DEVELOPMENT campaign

Status: **FROZEN, UNEXECUTED, DEVELOPMENT ONLY**  
Freeze date: 2026-08-14 UTC

This contract fixes a counterexample search for Conjecture 3 of Randy Davila,
*Automated conjecturing with TxGraffiti*, arXiv:2409.19379v2 (11 May
2026). The current source states that connected graphs `G,H` of orders at
least two satisfy

```text
gamma_t(G square H) >= gamma(G direct H).
```

Here `square` is the Cartesian product (one coordinate equal and the other an
edge), while `direct` is the tensor/categorical product (an edge in both
coordinates). `gamma` uses closed neighborhoods. `gamma_t` uses open
neighborhoods, so every selected vertex must have a selected neighbor. These
four definitions are independent gates and must never be exchanged.

## Chronology and prior coverage

The repository corpus transcribes the same statement at
`corpora/txgraffiti.json:82`, but points only to the 2024 v1 snapshot. The
primary record now has v2 and a related journal DOI
`10.1007/s10472-026-10005-5`. Version 2 still labels the statement
“Conjecture 3 (TxGraffiti),” describes it as table-true on curated data with
many sharp instances, and supplies the definitions above.

Repository-wide filename, statement, formula, symbol, and product-name
searches found no earlier campaign or resolution of this target. The tracked
Graffiti³ Conjecture 2 campaign is unrelated: it concerns `alpha` and the
RGA2 index, not products or domination. Public exact-statement and formula
searches through 2026-08-14 found no proof or counterexample. This is a
documented negative search, not a guarantee of novelty. Any hit remains
`CANDIDATE_FOUND`, and requires a fresh status search and independent replay.

No target proposal was evaluated while preparing this freeze. Only Atlas
counts/fingerprints and standard named identity checks were computed.

## Mandatory gate

Every arm runs the same gate before its first target row:

- source attestation must pin `2409.19379v2`, its revision date, Conjecture 3,
  and status `OPEN_NO_PUBLIC_RESOLUTION_FOUND`;
- NetworkX Graph Atlas connected counts for orders 2..7 must be
  `1,2,6,21,112,853` (995 total), with the frozen ordered graph6 SHA-256;
- independently implemented products must establish `K2 square K2 ~= C4`,
  `K2 direct K2 ~= 2K2`, `K2 square K3 ~=` the triangular prism, and
  `K2 direct K3 ~= C6`;
- exact enumeration must give both compared parameters equal to 2 for the
  pairs `(K2,K2)` and `(K2,K3)`.

Failure is terminal `DB_SOURCE_GATE_FAILED`; target rows following a failed
gate are invalid.

## Three frozen arms

1. `CATALOGUE` uses unordered pairs from all 30 connected Atlas graphs of
   orders 2..5 whose product order is at most 25, followed by fixed pairs of
   paths, cycles, complete graphs, and stars through factor order 7 with
   product order at most 36.
2. `GENERIC` uses exactly 4,000 fixed-seed labelled factor pairs. Factor
   orders are 2..6; each factor begins as a deterministic random labelled
   tree, then receives deterministic Bernoulli chords in five density strata.
3. `WALL_NAVIGATION` starts from the fixed equality/tight pairs `(K2,K2)` and
   `(K2,K3)`. It applies, on the left, right, and both factors, the fixed moves
   leaf attachment, false-twin addition, true-twin addition, first-edge
   subdivision, and a two-edge pendant parity path. No move or seed may be
   added after seeing target values.

The graph identity is the exact sorted edge list, vertex/edge counts, labelled
graph6 serialization, and SHA-256 of the labelled adjacency record. The
campaign makes no isomorphism-canonical uniqueness claim.

## Exact candidate certificate

For each factor pair, a deterministic greedy set-cover pass supplies an
explicit total dominating set `D` of size `k` in the Cartesian product. Every
search receipt distinguishes `total_subsets` from the combinations actually
visited in `subsets_examined`; an early witness can never be recorded as an
exhausted search. A crossing is accepted only after exhaustive enumeration of
every `k`-subset of the direct product finds no dominating set. The certificate
additionally contains the explicitly requested exhaustive proof for every
`(k-1)`-subset.
Thus it proves

```text
gamma_t(G square H) <= k < gamma(G direct H),
```

which is stronger than merely showing that no `(k-1)`-set dominates. The
standalone verifier is an independent implementation: it does not import the
search worker, validates applicability and every graph identity field,
reconstructs both products from the factor edge lists using separate
constructors, validates the witness and stored exhaustion receipts, and
replays both exhaustive checks. Floating point, ILP tolerances, and heuristic
lower bounds cannot decide a candidate.

## Runtime and evidence discipline

Each worker stops internally at 54 seconds and is externally capped at 60
seconds. Every gate, evaluated-pair, error, and summary row is appended to a
canonical-JSON SHA-256 chain, flushed, and `fsync`ed immediately. The terminal
receipt is separately canonicalized, created exclusively, flushed, and
`fsync`ed. Terminal reasons are exactly `CANDIDATE_FOUND`,
`DOMAIN_EXHAUSTED`, `DEADLINE_PREFIX`, `DB_SOURCE_GATE_FAILED`,
`CERTIFICATE_FAILED`, and `ERROR`. A deadline preserves only its durable
prefix and never means exhaustion.

The workflow is manual `workflow_dispatch`, grants only `contents: read`,
requires a literal 40-hex commit, checks out that commit with credentials
disabled, verifies a clean exact checkout, uses pinned action revisions and
Python/dependency versions, checks frozen file hashes before testing, and
uploads all arm evidence even on failure. It is not invoked by this freeze.

No issue, PR, release, README edit, public claim, or novelty count is
authorized by a candidate.
