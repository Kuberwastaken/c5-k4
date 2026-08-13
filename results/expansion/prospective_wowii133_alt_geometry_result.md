# Prospective WOWII #133 alternate-geometry result

Date: 2026-08-13 UTC

Frozen contract SHA-256:
`ca7e13b019bb5316169771d8f859d08cdfa816174a530cd73065f6f4c3ddb1b3`

## Gate-classified verdict

`HOLD_WITH_TIMEOUTS` — no crossing was found.

This is the verdict required by the frozen contract.  Exact maximum-induced-
path enumeration completed on 382 of 405 distinct evaluated construction
candidates.  The other 23 exact maximum computations timed out, so the frozen
protocol does not relabel those rows as exact holds.

No source/status/novelty audit and no public action were triggered because
there was no crossing.

## Database-sanity gate

The gate passed all 1,014 predeclared controls:

- negative residuals: 0;
- timeouts: 0;
- elapsed evaluator time: 0.579 seconds.

The gate covered every connected Graph Atlas graph on orders two through
seven and all named C4-present/C4-free controls in the contract.  It exercised
the full exponent reading, rather than only the C4-free search reduction.

## Construction search

All 405 evaluated candidates were connected, simple, C4-free graphs on 10 to
55 vertices.  No construction failed the C4 gate.  Results by stratum were:

| Stratum | Exact maxima | Exact timeouts | Minimum exact residual | Equalities |
|---|---:|---:|---:|---:|
| cage bases | 7 | 1 | 0 | 1 |
| incidence bases | 6 | 1 | 1 | 0 |
| clean edge substitutions | 39 | 3 | 2 | 0 |
| sparse shifted attachments | 330 | 18 | 2 | 0 |
| **Total** | **382** | **23** | **0** | **1** |

The sole equality was the Petersen graph:

```text
path = 5, radius = 2, floor(l) = 3, R133 = 0.
```

Its maximum path was independently recomputed by descending vertex subsets.
All 27 evaluated clean-substitution or pendant-attachment descendants moved
away from the wall, with residual at least 2.

Closest exact residuals by lineage were:

| Lineage | Evaluated exactly | Minimum residual |
|---|---:|---:|
| Petersen | 28 | 0 |
| Heawood | 28 | 1 |
| PG(2,2) Levi | 28 | 1 |
| Desargues | 28 | 3 |
| Möbius--Kantor | 28 | 4 |
| Pappus | 28 | 4 |
| Dodecahedron | 28 | 4 |
| PG(2,3) Levi | 28 | 4 |
| `S(K5)` | 34 | 4 |
| `S(K6)` | 34 | 6 |
| `S(K7)` | 31 | 7 |
| `S(K8)` | 31 | 9 |
| Tutte--Coxeter | 28 | 12 |

The 23 exact-max timeouts were confined to Hoffman--Singleton (15 rows) and
`S(K9)` (8 rows).

## Decision-level timeout diagnosis

Although the frozen exact-invariant verdict remains `HOLD_WITH_TIMEOUTS`, all
23 timed-out candidates can be ruled out as counterexamples without knowing
their maximum induced-path order.  For each graph, a separate checker found
and validated an induced path of order at least

```text
radius + floor(l).
```

The checker needed at most nine endpoint-extension states per graph.  For the
Hoffman--Singleton base it certifies the induced path

```text
[0, 1, 12, 5, 10, 18, 32, 23, 14]
```

of target order 9.  For the `S(K9)` base it certifies

```text
[0, 9, 1, 17, 2, 24]
```

of target order 6.  The auxiliary checker reproduces all 23 certificates:

```bash
timeout 60s python3 scripts/prospective_wowii133_alt_timeout_witnesses.py
```

Thus every evaluated row is decision-level noncrossing, while 23 rows remain
without the stronger exact maximum value demanded by the frozen contract.

## Reusable obstruction data

The frozen prediction did not survive this family test.  Sparse clean-handle
surgery failed for two coupled reasons:

1. Every base used here is triangle-free.  Therefore each open neighborhood
   is independent and `l(G)` is exactly the average degree.  Edge subdivision
   and pendant attachment introduce low-degree vertices, so they tend to pin
   or lower `floor(l)` instead of retaining a large correction term.
2. The same surgery supplies clean induced-path extensions.  Radius can rise,
   but the maximum induced-path order rose at least as quickly in every exact
   row.  Starting from the Petersen equality, every tested local move created
   at least two units of slack.

The incidence sequence also moves monotonically away from the desired wall in
the tested range: the minimum exact residuals for `S(K5)`, `S(K6)`, `S(K7)`,
and `S(K8)` were 4, 6, 7, and 9.  Increasing a globally spread incidence
structure is therefore not behaving like the requested shifted-endpoint
separation.

For a future #133 lane, the right decision oracle is not exact longest-path
optimization on every candidate.  First search for any induced path of target
order `radius + floor(l)`; such a witness rejects the candidate immediately.
Only graphs for which this target search fails need an exact maximum proof.
The 23 timeouts demonstrate the gain sharply: an expensive exact computation
was replaced by a 6--9-state certificate.

The remaining structural target is consequently global rather than local: a
C4-free graph must keep average local independence high and radius large while
blocking every induced path of their summed order.  Sparse attachments work
against both requirements.  Promising future constructions would need a
mechanism that suppresses induced paths without adding C4s or diluting average
degree; otherwise #133's persistent wall is better treated as theorem evidence.

## Artifacts

- Frozen contract: `results/expansion/prospective_wowii133_alt_geometry_contract.md`
- Incremental 1,497-line ledger:
  `results/expansion/prospective_wowii133_alt_geometry_ledger.jsonl`
- Frozen evaluator: `scripts/prospective_wowii133_alt_geometry.py`
- Timeout decision checker:
  `scripts/prospective_wowii133_alt_timeout_witnesses.py`

No commit, push, issue, PR, or release was made by this lane.
