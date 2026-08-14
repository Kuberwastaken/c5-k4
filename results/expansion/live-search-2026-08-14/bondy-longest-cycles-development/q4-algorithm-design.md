# Exact `q_4` algorithm and replay certificate design

**Scope:** frozen Bondy peripheral graphs `H` with `|V(H)|=20` and `k=4`

**Status:** design note only; no frozen target row was evaluated

**Purpose:** remove CBC-status ambiguity and make candidate replay comfortably fit the independent 60-second cap

## Result

For every vertex subset `S`, compute the exact minimum number `p(S)` of
pairwise vertex-disjoint nonempty paths that partition the induced graph
`H[S]`. A single endpoint subset dynamic program computes `p(S)` for all
`2^20` subsets. It directly decides both obligations:

```text
q_4(H) <= 16

and

there is a four-set Q supporting a simple four-vertex path
such that p(V(H) \ Q) <= 4.
```

The table uses about 21 MiB and, for a 4-regular graph, performs about 10.5
million endpoint-state updates and roughly 20 million neighbor probes. It has
no optimizer, tolerance, solver status, child process, or lazy cycle cut.

## Definitions

Paths are nonempty, singleton paths count, and their vertex sets must be
pairwise disjoint. For `S subseteq V(H)`, let

```text
p(S) = the minimum number of paths partitioning H[S],
p(empty) = 0.
```

Equivalently, `p(S) <= 4` exactly when `H[S]` has a spanning linear forest
with at most four components. Define

```text
q_4(H) = max { |S| : p(S) <= 4 }.
```

Only the predicate `p(S) <= 4` is needed, so all dynamic-program values may be
saturated at `5`, where `5` means "at least five paths."

## Endpoint subset dynamic program

For nonempty `S` and `v in S`, define `d(S,v)` to be the minimum number of
paths in an ordered path cover of `H[S]` whose last path ends at `v`. The order
and orientation of the paths are bookkeeping only. Put

```text
R = S \ {v}.
```

Then

```text
d(S,v) = min(
    p(R) + 1,
    min { d(R,u) : u in R and uv in E(H) }
)

p(S) = min { d(S,v) : v in S }.
```

All additions and stored values are saturated at `5`. The empty-neighbor
minimum is infinity, represented by `5`. With `p(empty)=0`, the recurrence
also handles singleton sets: `d({v},v)=1`.

### Correctness proof

Consider a cover counted by `d(S,v)`.

- If its last path is the singleton `v`, deleting that path leaves an
  arbitrary cover of `R`, giving the transition `p(R)+1`.
- Otherwise `v` is an endpoint of a nontrivial last path. Delete `v`; its
  predecessor `u` is adjacent to `v` and becomes the endpoint of the last
  path in a cover of `R`. The number of paths is unchanged, giving the
  transition `d(R,u)`.

Conversely, the first transition appends the singleton path `v`, and the
second appends `v` to the endpoint `u`. Both produce valid covers counted by
`d(S,v)`. Every unordered path cover can be ordered and each path can be
oriented, so minimizing over endpoints loses nothing. Induction on `|S|`
proves the recurrence and `p(S)=min_v d(S,v)`.

Saturation is exact for the required predicate. Neither transition can turn a
true value greater than four into one at most four: starting a new path adds
one, while extending an endpoint leaves the path count unchanged. Thus the
saturated value is at most four exactly when the unsaturated value is.

### Concrete C++ data layout and pseudocode

Use 20-bit masks and adjacency masks:

```text
M = 1 << 20
end[M][20] : uint8, initialized to 5
pc[M]      : uint8, initialized to 5
pc[0] = 0

for S from 1 to M-1:
    for each set bit v of S:
        R = S xor (1 << v)
        z = min(5, pc[R] + 1)
        candidates = R & adjacency[v]
        while candidates != 0:
            u = least_set_bit_index(candidates)
            z = min(z, end[R][u])
            candidates &= candidates - 1
        end[S][v] = z
        pc[S] = min(pc[S], z)
```

Numeric mask order is a valid topological order because `R<S`. A flat
row-major `uint8_t` allocation for `end` occupies
`20 * 2^20 = 20 MiB`; `pc` adds 1 MiB. There are
`20 * 2^19 = 10,485,760` reachable endpoint states. In a 4-regular graph an
endpoint state examines about two retained neighbors on average, so the core
work is about 20 million byte comparisons plus mask iteration. Even a dense
20-vertex graph remains a small bounded computation. This is expected to fit
well inside 60 seconds without relying on an optimizer; the verifier must
still record elapsed time and fail closed on its own deadline.

No parent table is required for the upper bound. To recover a positive cover,
backtrack equalities in the recurrence, choosing the least valid predecessor
at every tie. A `p(R)+1` equality creates a path boundary; a `d(R,u)` equality
adds the current vertex after `u`. The resulting paths must still be directly
replayed against `H` before serialization.

## The 1,351-deletion equivalence

For `|V(H)|=20`,

```text
q_4(H) <= 16
  iff
for every X subseteq V(H) with |X|<4, p(V(H)\X)>4.
```

If `q_4(H)>16`, some covered set `S` has at least 17 vertices. Taking
`X=V(H)\S` gives `|X|<=3` and makes `H-X=H[S]` coverable by at most four
paths. Conversely, any such deletion set has `|V(H)\X|>=17` and immediately
witnesses `q_4(H)>16`.

The complete deletion catalogue has exactly

```text
C(20,0) + C(20,1) + C(20,2) + C(20,3)
  = 1 + 20 + 190 + 1140
  = 1351
```

sets. After filling the table, the verifier enumerates these sets in fixed
cardinality-then-lexicographic order and requires

```text
pc[ALL xor X] == 5
```

for every one. Equivalently, it may scan all masks and compute

```text
q4_exact = max(popcount(S) for S with pc[S] <= 4).
```

Doing both is inexpensive and gives a useful internal consistency check. On
failure, the checker should return the least removed mask and reconstruct its
at-most-four-path cover. This is a normal proof that the row is not a
candidate, not a timeout or gate failure.

## The 4,845-set positive witness search

There are `C(20,4)=4,845` possible four-sets `Q`. Enumerate them
lexicographically. For each `Q`:

1. Test whether `H[Q]` contains a simple path using all four vertices. Trying
   the 24 vertex permutations is sufficient; identify a path with its reverse
   and retain the lexicographically least orientation.
2. Read `pc[ALL xor Q]`. If it is at most four, backtrack the DP to obtain a
   spanning path cover of `H-Q`.
3. Directly replay the path order, disjointness, and exact vertex union.

The path in `H[Q]` need not be induced: chords among its four support vertices
are allowed by the formal target. What matters is a simple walk with four
distinct support vertices and three consecutive graph edges.

The complete candidate condition is

```text
q_4(H) <= 16
and
there exists such a Q with p(V(H)\Q) <= 4.
```

The explicit complement cover proves `q_4(H)>=16`, while the deletion check
proves `q_4(H)<=16`; hence `q_4(H)=16`. Stitching the complement cover through
the four universal hubs gives a cycle of length 20. The general join bound
gives every cycle length at most `4+q_4(H)=20`, so the stitched cycle is
globally longest. Its off-cycle graph contains the recorded four-vertex path.
In the Lean statement's convention this has
`P.support.length=4` and `P.support.length+1=5>4`.

## Compact candidate certificate

A compact canonical JSON certificate can have this logical shape:

```json
{
  "schema": "bondy-q4-certificate-v1",
  "n": 20,
  "k": 4,
  "edges_h": [[0, 1]],
  "edges_g": [[0, 1]],
  "roles": [],
  "Q_mask": 0,
  "Q_path": [0, 1, 2, 3],
  "cover_H_minus_Q": [[4, 5]],
  "cycle_C": [20, 4, 5, 21, 22, 23, 20],
  "upper": {
    "method": "capped-endpoint-path-cover-dp-v1",
    "cap": 5,
    "deletion_order": "cardinality-then-lexicographic",
    "deletion_counts_by_size": [1, 20, 190, 1140],
    "deletion_sets_checked": 1351,
    "q4_upper": 16,
    "q4_exact": 16,
    "state_table_sha256": "..."
  },
  "replay": {
    "source_sha256": "...",
    "binary_sha256": "...",
    "elapsed_milliseconds": 0
  }
}
```

The displayed arrays are schematic, not candidate data. The actual artifact
must retain the already frozen constructor parameters, complete canonical
edge lists, role map, degree/connectivity/claw evidence, ledger binding, and
process provenance required by the contract.

The graph plus the positive paths are the compact mathematical input. The
independent checker regenerates the DP table. Hash the canonical byte stream
of the complete `pc[0..2^20-1]` table, or both the endpoint and `pc` tables, to
make separate implementations and later reruns comparable. A table digest is
provenance, not an upper-bound proof by itself.

If a self-contained proof object rather than deterministic recomputation is
required, attach the capped endpoint table as bytes. It is about 20 MiB before
compression. A checker can validate every base case and recurrence and then
the 1,351 deletion entries. For the present 60-second replay requirement,
regenerating the table is simpler and keeps the certificate small.

## Independent replay requirements

The replay executable should be separately written and should not import a
discovery helper. It must:

1. Parse the complete input strictly: exact vertex range, canonical edge
   order, no duplicates, no self-loops, and no ignored trailing tokens.
2. Reconstruct adjacency masks from `edges_h` rather than trusting serialized
   derived state.
3. Recompute the capped endpoint DP from scratch in a fixed iteration order.
4. Check all 1,351 deletion masks and independently compute `q4_exact` by an
   all-mask scan.
5. Replay `Q_path`, the complement cover, the stitched cycle, support sets,
   and the literal target inequality.
6. Recompute and compare the state-table digest, source digest, and relevant
   constructor coordinates.
7. Return distinct terminals for verified upper bound, ordinary
   counter-witness to the upper bound, deadline, malformed input, and internal
   inconsistency. Only the first can support `CANDIDATE_FOUND`; an ordinary
   counter-witness rejects that row and permits the frozen search to continue.

For stronger implementation diversity, discovery and replay can use separate
source files and independently coded versions of the recurrence. An optional
second candidate-only acyclic degree-two branch-and-bound check may be retained
as defense in depth, but it should not be the sole upper-bound verifier under
the 60-second cap.

## Current-code observations

These observations refer to the prospective scripts as inspected without
executing target rows.

### CBC discovery path

`prospective_bondy_search.py` now isolates CBC children and directly replays a
feasible assignment. That makes a reported positive assignment usable as an
existence witness. Negative conclusions, however, still depend on parsing the
literal CBC text `Problem proven infeasible`, and every child is capped at two
seconds. In the worst case the evaluator can launch a solver child for each of
4,845 `Q` sets. This remains slower and more status-sensitive than the single
subset DP.

The current flow also stops at the first `Q` whose complement has a cover and
then invokes the upper replay. If that replay finds `q_4(H)>16`, its nonzero
rejection exit is currently converted to `TimeoutError` and then to
`CAP_PREFIX`. A proved upper-bound counterexample is neither a timeout nor a
gate failure. It should carry the removed mask and reconstructed cover, mark
the row noncandidate, and allow the search to continue.

### Existing independent branch-and-bound

`prospective_bondy_replay.cpp` separately tests each of the 1,351 deletion
sets by branching over active edges with a rollback DSU. Its encoding is
sound: selecting `|S|-4` acyclic degree-at-most-two edges gives a spanning
linear forest with at most four components. Its worst-case search tree is
nevertheless unpredictable because essentially the same exponential search
is restarted for every deletion set.

Two implementation details weaken performance clarity without making the
answer unsound:

- its capacity bound sums residual degree capacity over all 20 vertices,
  including deleted vertices, so the bound is weaker than necessary; and
- `coverable()` sorts active edges using `degree[]` before resetting
  `degree` and the DSU. After a successful prior call, stale degrees can alter
  the next search order. The state is reset before DFS, so this affects search
  order and timing rather than logical correctness.

The parser also stops at the first failed integer extraction and therefore
should explicitly reject malformed trailing content. The endpoint DP avoids
the branch-order and repeated-search issues altogether.

## Recommended integration shape

- Use a native endpoint-DP evaluator for each applicable `H`.
- Reject immediately and normally when its exact `q4` is greater than 16.
- Only when `q4=16`, enumerate the 4,845 `Q` sets and recover the least
  positive witness from the same table.
- Before publishing a candidate, run a separately written independent checker
  that rebuilds the table, checks all deletion sets, and replays every explicit
  path and cycle.
- Preserve fail-closed deadline handling, but never translate a mathematically
  proved noncandidate into `CAP_PREFIX`.

This makes every accepted result exact and replayable while eliminating CBC
termination semantics from the `q_4` decision.
