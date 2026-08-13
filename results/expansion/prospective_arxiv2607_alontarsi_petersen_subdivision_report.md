# Prospective arXiv 2607.06396 Petersen-edge subdivision trial

## Outcome

Primary outcome: **`THEOREM_SHADOW`**. Secondary coordinate verdict:
**`PREDICTION_CONFIRMED`**.

The frozen family does not cross the Alon--Tarsi shortest-cycle-cover wall.
For the graph obtained by replacing the fixed Petersen edge `(0,1)` by a path
with `t` new degree-two vertices,

```text
|E(G_t)| = 15+t,
scc(G_t) = 21+t,
R(G_t) = 7|E(G_t)| - 5 scc(G_t) = 2t.
```

All twelve preregistered coordinates `t=1,...,12` matched these formulas.
The transformation therefore moves strictly away from the equality wall.

## Phase 0: exact source and status

- Upstream repository: `google-deepmind/formal-conjectures`.
- Current upstream commit fetched before selection:
  `d16e05aded22b8c467a0a27c14b2311f53185006`.
- File:
  `FormalConjectures/Arxiv/2607.06396/AlonTarsi.lean`.
- Declaration: `Arxiv.2607.06396.alon_tarsi_short_cycle_cover`.
- Current category: `@[category research open, AMS 5]`.
- Source: Ferrarini and Mkrtchyan, arXiv:2607.06396v1, Conjecture 4.
- Reading: **`UNAMBIGUOUS`**. Both source and Lean say that every finite
  bridgeless graph has a list/multiset of simple cycles covering every edge,
  with total length at most `(7/5)|E|`. The source explicitly says the graph
  need not be cubic.
- Live GitHub gate: issue
  [#4813](https://github.com/google-deepmind/formal-conjectures/issues/4813)
  is closed and formulation PR
  [#4850](https://github.com/google-deepmind/formal-conjectures/pull/4850)
  merged on 2026-08-11. Searches for the source title, conjecture name,
  declaration name, and `2607.06396` found no proof, disproof, or competing
  solution issue/PR.

The local graph query and exact text search found only classification rows in
`formal_conjectures.md` and `method_v02_upstream_selection.md`. The earlier
sweep excluded this declaration because generic positive-instance evaluation
requires unbounded auxiliary cycle-cover search; it did not compute `scc`,
freeze a family, or cover this subdivision operation.

## Literature gate and theorem baseline

This is a longstanding open conjecture. Macajova and Skoviera (2021) state
that the constant `7/5` is sharp, that Petersen has `m=15` and `scc=21`, and
that infinite equality families of cyclic connectivity two and three are
known. This trial neither tests nor claims novelty for those equality families.
The frozen degree-two subdivision operation is distinct from them and from the
parallel Petersen 2-edge-sum/switch lane.

References used in the gate:

- N. Alon and M. Tarsi, *Covering multigraphs by simple circuits*, SIAM J.
  Algebraic Discrete Methods 6 (1985), DOI `10.1137/0606035`.
- E. Macajova and M. Skoviera, *Cubic Graphs with No Short Cycle Covers*, SIAM
  J. Discrete Math. 35 (2021), DOI `10.1137/21M1399208`.
- L. Ferrarini and V. Mkrtchyan, *Some new results on Sylvester colorings of
  cubic graphs*, arXiv:2607.06396v1 (2026), Conjecture 4.

## Frozen transformation and obstruction

The contract was frozen before any candidate evaluation. The base is the
labelled NetworkX Petersen graph, the selected edge is exactly `(0,1)`, and
the only permitted transformation replaces that edge by

```text
p0 -- x1 -- ... -- xt -- p1,       1 <= t <= 12.
```

Every row stores the full labelled edge list, graph6 checksum, role map,
edge-record digest, and role-record digest.

The exact obstruction proves the whole operation class, not merely the tested
range. In any cycle cover of `G_t`, a cycle meeting the internal degree-two
path must traverse the whole path. Suppress its `t` new vertices in every
cover cycle. This gives a Petersen cycle cover and decreases total length by
`t k`, where `k>=1` is the number of selected cycles using the path. Therefore

```text
scc(G_t) >= scc(Petersen) + t = 21+t.
```

The database fixture supplies an explicit length-21 Petersen cover in which
the selected labelled edge `(0,1)` occurs exactly once. Extending that cycle
through the subdivided path gives a cover of length `21+t`, so equality holds.
Consequently `R(G_t)=2t>0` for every `t>=1`. The natural subdivision direction
is closed by a theorem shadow.

## Database and implementation gates

The primary oracle enumerated undirected simple cycles and solved exact binary
set cover with SciPy/HiGHS (`mip_rel_gap=0`, 40-second internal cap). Positive
cycle lengths make duplicate cycles unnecessary even though the Lean/source
object is a multiset.

- Microfixtures passed: `C5` has `scc=5`, `R=10`; Petersen has `scc=21`,
  `R=0`.
- All 995 connected Graph Atlas graphs on 2--7 vertices were appended. Of
  these, 577 satisfy the nonempty bridgeless applicability predicate, and all
  have nonnegative residual.
- All named controls were appended: `C5`--`C9`, `P7`, Petersen, `K3,3`, `K7`,
  stars, `K2,3`, and `K2,4`. Inapplicable bridge-bearing graphs are explicitly
  marked `NOT_APPLICABLE`.
- An independent oracle enumerated cycles as connected 2-regular edge subsets
  and solved set cover by dynamic programming over edge masks. It agreed on
  all 75 applicable connected Atlas graphs through order six and on the C5 and
  Petersen fixtures (77 audit rows total).

The first independent-oracle invocation stopped before its first graph row
because the installed Python lacks `int.bit_count`. Its phase-start row is
preserved and classified `PROTOCOL_DEVIATION`. A separately identified literal
replay replaced that compatibility call by `bin(mask).count("1")`; graph,
cycle, optimization, bounds, and verdict semantics were unchanged. The replay
passed before the family was unlocked.

## Frozen family results

| `t` | vertices | edges | exact `scc` | scaled residual `R` |
|---:|---:|---:|---:|---:|
| 1 | 11 | 16 | 22 | 2 |
| 2 | 12 | 17 | 23 | 4 |
| 3 | 13 | 18 | 24 | 6 |
| 4 | 14 | 19 | 25 | 8 |
| 5 | 15 | 20 | 26 | 10 |
| 6 | 16 | 21 | 27 | 12 |
| 7 | 17 | 22 | 28 | 14 |
| 8 | 18 | 23 | 29 | 16 |
| 9 | 19 | 24 | 30 | 18 |
| 10 | 20 | 25 | 31 | 20 |
| 11 | 21 | 26 | 32 | 22 |
| 12 | 22 | 27 | 33 | 24 |

No solve took one second; no timeout or numerical bracket occurred. Every
process was externally capped below 60 seconds. No parameter was extended,
no alternate edge or graph was substituted, and no commit, push, release,
issue, PR, or other public write was performed as part of the trial.

## Artifacts

- `prospective_arxiv2607_alontarsi_petersen_subdivision_contract.json`:
  immutable contract SHA-256
  `8dbac70194303bf9163ecbc85733cc5150c9a737c7ada3cd74e36855c2aa9703`.
- `prospective_arxiv2607_alontarsi_petersen_subdivision_oracle_addendum.json`:
  independent-audit addendum SHA-256
  `4a09dfd82c53e67070c77641cecac91bd1e9f8b419199e1b97e9a69f457b591f`.
- `prospective_arxiv2607_alontarsi_petersen_subdivision_ledger.jsonl`:
  1,110 append-only rows; SHA-256
  `9f972ce3d7b4ba02d9d5a272ec16b755451e68279d42fe3548ed7c9bca2ca889`.
- `scripts/prospective_arxiv2607_alontarsi_petersen_subdivision.py`:
  primary oracle, independent oracle, gate, constructor, and exact replay.

This trial is development-set evidence only. It is not held-out evidence and
does not resolve the Alon--Tarsi conjecture outside the closed subdivision
operation class.
