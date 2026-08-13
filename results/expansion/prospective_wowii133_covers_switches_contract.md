# Frozen prospective WOWII #133 covers-and-switches trial

Frozen: **2026-08-13 UTC**, before evaluating any graph in this lane.

## Target

Only the current DeepMind declaration
`FormalConjectures/WrittenOnTheWallII/GraphConjecture133.lean` is in scope.
For a connected nontrivial graph define

```text
R133(G) = path(G) - radius(G) - floor(l(G))^cC4(G).
```

`path` is maximum induced-path order, `l` is average open-neighborhood
independence, and `cC4=1` exactly when there is no not-necessarily-induced
four-cycle.  A negative exact residual is an apparent crossing.

This trial is independent of the previous alternate-handle lane: it performs
no pendant-path, edge-subdivision, or shifted-endpoint attachment.

## Frozen prediction

Covering transformations preserve degree and do not decrease girth, while
they may increase radius.  The desired separation is a C4-free cover or
C4-safe degree-preserving switch for which radius grows faster than maximum
induced-path order, with `floor(l)` pinned.

## Frozen construction lanes

1. **Named C4-free controls:** Heawood, Möbius--Kantor, Tutte--Coxeter,
   Pappus, Desargues, Dodecahedron, McGee, and generalized Petersen
   `G(n,k)` for `5 <= n <= 20`, `1 <= k < n/2`, filtered for connectedness and
   C4-freeness.
2. **Incidence covers:** Levi graphs of projective planes of prime order
   `q in {2,3}`.
3. **Cyclic covers:** connected `Z_3` voltage lifts of `C5`, `C6`, Petersen,
   and Heawood.  Spanning-tree voltages are gauge-fixed to zero.  All
   assignments are used for `C5`, `C6`, and Petersen; for Heawood use the
   first 300 nonzero lexicographic cotree assignments.
4. **C4-safe switches:** enumerate deterministic one-switch descendants of
   Petersen and the first 40 connected Petersen `Z_3` covers, retaining only
   connected C4-free graphs with the same degree multiset.  Keep at most 500
   switch descendants total, ordered lexicographically by deleted and added
   edge tuples.

Exact graph6 duplicates are removed globally.  No family may be added after
evaluation begins.

## Bounds and exactness

- at most 1,500 distinct discovery graphs and order at most 42;
- each operating-system process at most 60 seconds;
- each endpoint-extension induced-path solve at most 10 seconds and each
  discovery batch at most 55 seconds;
- exact C4 test by common-neighbor pairs, exact radius by all-source BFS,
  exact local neighborhood independence by subset enumeration, and exact
  maximum induced path by exhaustive endpoint extension;
- a timeout is unresolved and cannot support either a crossing or a hold.

Every row is appended immediately to
`results/expansion/prospective_wowii133_covers_switches_ledger.jsonl`.

## Mandatory database gate

Before discovery, reproduce a nonnegative exact residual on every connected
Graph Atlas graph of orders two through seven and on `C5--C9`, `P7`,
Petersen, `K3,3`, `K7`, stars `K1,2--K1,7`, and `K2,3`, `K2,4`, `K3,4`,
`K4,4`.  Any negative row or timeout stops the lane.

## Crossing protocol and status gate

For every apparent crossing:

1. independently recompute every invariant using descending subset
   enumeration for induced paths;
2. preserve graph6, a maximum path witness, all local values, a center, and
   an explicit C4-free certificate check;
3. re-read the current DeepMind declaration and search current issues/PRs;
4. search the historical/source record and web for the graph/formula pairing;
5. classify `NEW`, `ALREADY_KNOWN`, `SOURCE_ERRATUM`, `READING_DEPENDENT`, or
   `STATUS_UNCLEAR` before alerting the parent.

No commit, push, issue, PR, release, or other public action is authorized.

## Verdicts

- `CROSSING_VERIFIED`: an exact negative residual survives every gate.
- `HOLD_BOUNDED`: all frozen candidates complete and are nonnegative.
- `HOLD_WITH_TIMEOUTS`: no verified crossing, but some exact solves time out.
- `GATE_FAIL`: the database sanity phase fails.
