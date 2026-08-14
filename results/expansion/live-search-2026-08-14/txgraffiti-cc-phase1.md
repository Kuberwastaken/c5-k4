# TxGraffiti C-C phase one: replacement-collapse correction

Date: **2026-08-14 UTC**

Evidence split: **DEVELOPMENT**; this is not part of the held-out Method v1.5
benchmark.

This addendum reuses the exact statement, source/status coordinates,
database-sanity gate, residual, solver limits, and publication gate frozen in
[`txgraffiti-cc-phase0.md`](txgraffiti-cc-phase0.md).  It changes only the
proposal arms in response to the phase-zero result.  No phase-one graph was
evaluated before this contract and its worker were committed.

## Observation being tested

Phase zero placed `21/37` targeted rows on equality but did not cross.  Its
ranking coordinate—how many minimum independent dominating sets of the parent
a switch destroys—failed because a child can acquire new, smaller sets.

Phase one therefore makes two preregistered changes:

1. graph covers provide a nonlocal move away from the local replacement sets;
2. the wall arm expands a child only after exact evaluation proves both
   `mu*(child)-i(child)=0` and `i(child)>=i(parent)`.

The second condition is the exact child-side guard forced by replacement-set
collapse.  It is not inferred from the parent's witness list.

## Frozen arms

Every arm runs as a separate process under the existing hard 60-second
process-group cap, repeats the database-sanity gate, and writes a fresh
hash-chained, fsynced Method v1.5 JSONL stream.

### `CATALOGUE`

Enumerate the 512 signed two-lifts of labeled `K3,3` in increasing mask order.
Connectivity, regularity, exact `i`, exact `mu*`, and nauty identity are
replayed for every retained graph.  Isomorphic masks are evaluated once.

### `GENERIC`

With seed `0xCC20260815`, repeatedly select one of `K3,3`, Petersen, `CL5`, or
`CL6`, then sample a uniformly random edge-sign mask and evaluate its two-lift.
The proposal distribution never sees an objective value.

### `WALL_NAVIGATION`

Start from equality seeds `K3,3`, Petersen, `CL5`, `CL6`, and `CL9`.  For each
expanded state, generate all valid degree-preserving connected two-switches,
shuffle them with a deterministic seed derived from the parent's graph6 bytes,
and evaluate at most 16.  A child enters the breadth-first queue only if exact
optimization proves both

```text
mu*(child) - i(child) = 0
i(child) >= i(parent).
```

Depth is at most three and at most 24 states are expanded.  The old
parent-witness destruction score is not computed.

## Stops

- Each binary ILP remains capped at eight seconds and each worker at 60.
- A non-optimal solver result terminates the worker and is not a hold.
- A negative residual receives the phase-zero independent exhaustive replay,
  appends a crossing checkpoint, and stops that arm.
- A timeout prefix remains evidence only for its already-fsynced exact rows.
- Zero crossings are a bounded development result, never a proof.
- No family, depth, child cap, seed, or expansion rule may change after this
  freeze.  Any further revision is a new phase.
