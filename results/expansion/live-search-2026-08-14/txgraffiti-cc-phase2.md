# TxGraffiti C-C phase two: extremal-reservoir freeze

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**; this is not part of the held-out Method v1.5
benchmark.

This contract reuses the exact statement, source/status audit,
database-sanity gate, candidate publication conditions, nauty authority, and
scientific JSONL format frozen in
[`txgraffiti-cc-phase0.md`](txgraffiti-cc-phase0.md). Phase one required a new
construction carrying a structural certificate for a small minimum maximal
matching. Phase two makes only that preregistered change.

No phase-two target graph was evaluated before this contract and worker were
frozen. Only syntax, import, constructor, regularity, connectivity, and
structural-certificate checks are allowed before the three discovery arms are
run.

## Prior scratch scouting disclosure

Before this freeze, an explicitly exploratory scratch program outside the
repository sampled this construction at coordinates `t=2,3,4`. It evaluated
360 random-pair states and 480 adjacent-versus-distant-pair states. It found
no negative residual, observed many equality rows, and suggested distant
edge pairing as a useful wall initializer. One order-20 equality row was
independently replayed. Those inspected graphs are development scouting, are
not benchmark evidence, and are not copied into this phase-two denominator.

The frozen worker uses the fresh seed `0xCC20260820`. Its generic coordinates
`t=5,6` were not inspected in the scratch run. Its wall instances are freshly
generated from this new seed; coordinates `t=3,4` were previously scouted in
aggregate, while `t=5` is new. The fixed named catalogue is a database arm and
is not claimed to be unseen.

## Construction and exact structural wall

For an integer `t >= 1`, take a connected cubic base graph `H` on `4t`
vertices. Subdivide each of its `6t` edges once, producing a set `X` of `6t`
new vertices, and add a perfect matching `P` on `X`. Call the resulting graph
`G(H,P)`.

The graph is connected, cubic, and has `10t` vertices. The original vertices
of `H` are an independent set left unmatched by `P`, so `P` is a maximal
matching of size `3t`.

Conversely, let `M` be any maximal matching in any cubic graph and let `U` be
its unmatched vertices. Maximality makes `U` independent. Every vertex of
`U` sends three edges to endpoints of `M`, while each of the `2|M|` endpoints
has at most two such edges because one incident edge belongs to `M`. Hence

```text
3|U| <= 4|M|
n = 2|M| + |U| <= (10/3)|M|.
```

For `G(H,P)`, `n=10t`, so every maximal matching has at least `3t` edges and
the displayed `P` proves

```text
mu*(G(H,P)) = 3t.
```

This certificate is checked on every proposed child. The phase-two exact
residual is therefore

```text
R(G) = 3t - i(G).
```

Only the child's independent domination number is optimized. The exact binary
MILP uses the literal independence and closed-neighborhood domination
constraints, has a per-solve cap of four seconds, and must report a proved
integer optimum. Parent witness sets are never read or scored.

If `R<0`, an independent PySAT/CaDiCaL encoding checks that no independent
dominating set of size at most `3t` exists, the structural matching proof is
replayed, a crossing checkpoint is appended, and the arm stops. A replay
failure invalidates the candidate.

## Frozen arms

Every arm is a distinct process under the existing hard 60-second
process-group cap, stops internally at 54 seconds, repeats the complete
phase-zero Graph Atlas and named-control gate, and writes a fresh hash-chained,
fsynced Method v1.5 JSONL stream. Exact identity is supplied only by the
frozen nauty `labelg` executable.

### `CATALOGUE`

Use the fixed connected cubic bases `K4`, cube, `CL6`, Frucht, and
Möbius--Kantor. For each base, evaluate exactly two deterministic subdivision
matchings:

1. a maximum-total-line-graph-distance perfect matching;
2. a perfect matching consisting of adjacent base-edge pairs.

This is a fixed ten-row construction catalogue before nauty deduplication.

### `GENERIC`

With seed `0xCC20260820 xor 0x47454E45524943`, repeatedly choose
`t` uniformly from `{5,6}`, generate a connected labeled cubic base uniformly
through NetworkX's seeded regular-graph generator, and uniformly shuffle the
`6t` subdivision vertices into a perfect matching. The proposal distribution
never sees `i`, `R`, or any parent state.

### `WALL_NAVIGATION`

With seed `0xCC20260820 xor 0x57414C4C`, generate two fresh connected cubic
bases at each `t in {3,4,5}` and initialize each with a
maximum-total-line-graph-distance pairing. Every seed is evaluated exactly.

For an expanded state, generate two certificate-preserving move classes:

- **pairing exchange:** choose two edges of `P` and replace them by either
  alternate perfect pairing on their four endpoints;
- **base two-switch:** apply a valid connected cubic two-switch to `H` and
  transport `P` to the corresponding subdivision vertices.

The per-state proposal list is deterministically shuffled from the exact
state encoding. At most 24 proposals of each move class are evaluated. A
width-24 beam retains children by the lexicographic key

```text
(exact child R ascending, exact child i descending, canonical SHA-256).
```

Thus every navigation decision uses the exact child's residual; there is no
parent-witness proxy. Depth is at most three and at most 24 states are
expanded.

## Stops and interpretation

- Each independent-domination MILP receives at most four seconds.
- Each worker receives a hard 60-second process-group cap and an internal
  54-second stop.
- A nonoptimal solver status terminates the worker. It is not a bounded hold.
- A hard timeout leaves only the already-fsynced exact prefix.
- No seed, coordinate, family, pairing rule, move count, beam width, depth, or
  ranking rule may change after this freeze.
- Zero crossings are a bounded development result, never a proof.
- No issue, pull request, release, or other outward action is authorized by
  this contract.

Frozen artifacts:

- [`txgraffiti-cc-phase2-manifest.json`](txgraffiti-cc-phase2-manifest.json)
- [`../../../scripts/search_txgraffiti_cc_phase2.py`](../../../scripts/search_txgraffiti_cc_phase2.py)
