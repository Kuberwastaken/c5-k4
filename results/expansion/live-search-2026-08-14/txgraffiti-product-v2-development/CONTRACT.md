# TxGraffiti Conjecture 3: frozen exact-Cartesian DEVELOPMENT v2

Status: **FROZEN, UNEXECUTED, DEVELOPMENT ONLY**  
Freeze date: 2026-08-14 UTC

## Target and reason for revision

The source-faithful target remains Conjecture 3 of Randy Davila,
*Automated conjecturing with TxGraffiti*, arXiv:2409.19379v2:

```text
gamma_t(G square H) >= gamma(G direct H)
```

for connected factors of order at least two. `square` is the Cartesian
product, `direct` is the tensor product, `gamma_t` uses open neighborhoods,
and `gamma` uses closed neighborhoods.

The frozen v1 campaign evaluated 801 factor pairs without a certificate, but
used a deterministic greedy total-dominating set in the Cartesian product.
Its own result identified the method defect: a nonminimum greedy witness of
size `k` may coexist with a size-`k` direct-product dominating set even when a
smaller Cartesian total-dominating set would cross the conjectured wall.
V2 changes that coordinate only. No v2 target pair was evaluated before this
contract and its implementation were frozen.

## Resolution and candidate rule

One finite applicable pair suffices to refute the universal statement. For
each pair, v2:

1. constructs a valid greedy Cartesian total-dominating witness;
2. searches exactly at size `k-1`; a witness lowers `k` monotonically and the
   search repeats, while a complete absence proves the current `k` is exact;
3. computes `gamma(G direct H)` exactly, beginning at the certified degree
   lower bound `ceil(n/(Delta+1))`; and
4. admits a candidate only when the exact direct value is strictly greater
   than the certified Cartesian upper bound.

Every fixed-cardinality decision is a literal combination enumeration with a
hard cap of at most four seconds. A timeout cannot certify absence or an exact
parameter. It preserves the best explicit Cartesian witness, but the direct
value becomes unknown and the row cannot be a candidate. Thus a candidate
always contains the stronger certificate

```text
gamma_t(G square H) <= k < gamma(G direct H).
```

The direct value carries its exact witness, degree lower bound, and completed
absence steps. Cartesian exactness is reported separately and is not required
for the strict counterexample certificate.

## Mandatory source/database/product gate

Before any target row, every arm must establish:

- the pinned `2409.19379v2` source attestation and open-status snapshot;
- all 995 connected Graph Atlas graphs of orders 2 through 7, with counts
  `1,2,6,21,112,853` and ordered graph6 SHA-256
  `1cfb1c9688917d79dc59a9e9fc529af2780b9bceaa39f25bb61672c4ad4e72c3`;
- `K2 square K2 ~= C4`, `K2 direct K2 ~= 2K2`,
  `K2 square K3 ~=` the triangular prism, and `K2 direct K3 ~= C6`; and
- exact compared values `2,2` for both `(K2,K2)` and `(K2,K3)`.

Any failure is terminal `DB_SOURCE_GATE_FAILED`; no later target row is valid.

## Three deliberately smaller domains

The domains are fixed before evaluation and favor information per exact
subproblem over breadth:

1. **CATALOGUE (69 pairs):** all 45 unordered pairs of the nine connected
   Atlas graphs of orders two through four, followed by 24 named sparse,
   dense, bipartite-like, and equality-adjacent pairs from paths, cycles,
   complete graphs, and stars. Products have order at most 25.
2. **GENERIC (192 proposals):** fixed seed `820240919`, factor orders two
   through five, and four frozen chord-density strata. Each factor begins as
   a deterministic labelled random tree. The stream is fixed even when the
   worker retains only a deadline prefix.
3. **WALL_NAVIGATION (32 pairs):** `(K2,K2)` and `(K2,K3)`, every one-sided
   leaf, false-twin, true-twin, first-edge-subdivision, and two-edge parity
   move, plus the five matched two-sided moves. This is a strict subset of
   v1's exhausted 72-pair wall domain, replayed because the changed Cartesian
   optimization semantics—not a larger construction family—is the variable.

No domain may be enlarged or retuned after result inspection. A follow-up
requires a separately frozen contract.

## Evidence and independent replay

Every source gate, exact-size subproblem, evaluated pair, error, and summary
is appended immediately as canonical JSON to a SHA-256 chain, flushed, and
`fsync`ed. The separately created terminal receipt binds the final row hash
and count. Terminal reasons are `CANDIDATE_FOUND`, `DOMAIN_EXHAUSTED`,
`DEADLINE_PREFIX`, `DB_SOURCE_GATE_FAILED`, `CERTIFICATE_FAILED`, and `ERROR`.

The certificate stores full labelled factor and product edge lists, graph6,
identity digests, the Cartesian witness and descent record, and the exact
direct value and witness. The independent verifier imports no discovery code.
It reconstructs both products, identities, hypotheses and witnesses, replays
the decisive absent cardinality under its own four-second cap, and checks the
strict integer comparison.

## Runtime and execution lock

Each hard fixed-cardinality subproblem is capped at four seconds. Each arm
stops internally at 54 seconds under an external 60-second process cap. A
deadline means only a durable prefix, never domain exhaustion.

The workflow is manual `workflow_dispatch`, grants only `contents: read`,
requires a literal 40-hex commit, checks out that commit with credentials
disabled, verifies a clean exact checkout, verifies frozen hashes, runs only
constructor tests before the target process, and uploads all evidence even on
failure. This freeze does not dispatch it.

No issue, PR, release, README edit, novelty count, or public claim is
authorized by a candidate. Source/status/duplicate audit, independent replay,
formal certification, and the repository release protocol remain mandatory.
